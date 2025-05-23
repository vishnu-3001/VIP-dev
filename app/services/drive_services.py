import re
import io
import json
from typing import List,Dict,Tuple
from docx import Document
from langchain.prompts import PromptTemplate
from docx.oxml import OxmlElement
from utils import *
from docx.oxml.ns import qn
from app.database import get_connection
from fastapi import HTTPException


highlight_colors = {
    "project-update": "#d6eaf8",
    "meeting-notes": "#e8daef",
    "todo": "#ffdab9",
    "feedback": "#fffacd",
    "other": "#d5f5e3"
}

date_pattern=re.compile(
    r'^('
    r'\d{1,2}/\d{1,2}/\d{4}|'                  # 5/17/2024
    r'\d{1,2}/\d{1,2}/\d{2}|'                  # 5/17/24
    r'\d{1,2}-\d{1,2}-\d{2}|'                  # 05-17-24
    r'\d{1,2}-\d{1,2}-\d{4}|'                  # 05-17-2024
    r'\d{1,2}\.\d{1,2}\.\d{2}|'                # 05.17.24
    r'\d{1,2}\.\d{1,2}\.\d{4}|'                # 05.17.2024
    r'\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}|'  # 17th May 2024
    r'\w+\s+\d{1,2},\s+\d{4}|'                 # May 17, 2024
    r'\d{1,2}-\w+-\d{4}|'                      # 17-May-2024
    r'\w+\s+\d{1,2}(?:st|nd|rd),\s+\d{4}|'     # May 17th, 2024
    r'\w+\s+\d{1,2}(?:st|nd|rd)?\s+\d{4}|'     # May 17th 2024
    r'\w+\s+\d{1,2}(?:st|nd|rd|th),\s+\d{4}'   # May 17th, 2024
    r')$'
)
def format_chunk_for_gpt(paragraphs: List[str]) -> str:
    return "\n\n".join(paragraphs)

async def classify_paragraphs(paragraphs: List[str]) -> str:
    prompt_template = """
You are a smart assistant helping a student classify chunks of their project journal. Each chunk consists of a few related paragraphs.

Classify the entire chunk into **only one** of the following categories:

project-update
General updates, progress logs, discoveries, decisions, technical exploration, or milestones reached.
Example: “Found an app template that uses NativeWind. Will build on top of it.”

meeting-notes
Notes taken from a meeting: attendees, topics discussed, or decisions made.
Example: “Met with mentor to discuss dataset pre-processing issues.”

todo
Clear action items, pending tasks, or planned next steps.
Example: “Need to integrate login with Google OAuth.”

feedback
Comments or suggestions from others (mentors, peers, users) or internal review notes.
Example: “User suggested adding a dark mode toggle.”

other
Anything that doesn’t clearly fit the above (e.g., motivational quotes, personal notes, placeholders).

Return only the category name: "project-update", "meeting-notes", "todo", "feedback", or "other"

Chunk content:
\"\"\"
{chunk}
\"\"\"

Your answer (one word only):
"""
    llm=model()
    prompt = PromptTemplate(input_variables=["chunk"], template=prompt_template)
    chain = prompt | llm
    formatted = format_chunk_for_gpt(paragraphs)
    response = await chain.ainvoke({"chunk": formatted})
    output = response.content.strip().lower() if hasattr(response, "content") else response.strip().lower()

    return output if output in highlight_colors else "other"

def apply_highlight_preserve_styles(para, hex_color):
    for run in para.runs:
        if run.text.strip():
            rPr = run._element.get_or_add_rPr()
            shd = OxmlElement('w:shd')
            shd.set(qn('w:val'), 'clear')
            shd.set(qn('w:color'), 'auto')
            shd.set(qn('w:fill'), hex_color.replace("#", ""))
            rPr.append(shd)

async def highlight_by_semantics(doc_bytes: bytes,file_id) -> bytes:
    doc_io = io.BytesIO(doc_bytes)
    doc,chunks_by_date = chunk_by_dates(doc_io)
    date_label_data={}
    for date, paragraphs in chunks_by_date.items():
        para_texts = [p.text.strip() for p in paragraphs if p.text.strip()]
        if not para_texts:
            continue
        label = await classify_paragraphs(para_texts)
        date_label_data[date]=label
        for para in paragraphs:
            if para.text.strip():
                apply_highlight_preserve_styles(para, highlight_colors.get(label, "gray"))
    output_io = io.BytesIO()
    doc.save(output_io)
    save_date_label_data(date_label_data,file_id)
    output_io.seek(0)
    return output_io.getvalue()

def save_date_label_data(data,file_id):
    conn=get_connection()
    cursor=conn.cursor()
    try:
        insert_query="""
            UPDATE documents SET date_label_data = %s WHERE document_id = %s
        """
        cursor.execute(insert_query,(json.dumps(data),file_id))
        print("date label data saved")
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Database update failed with date label data:{str(e)}")
    

def chunk_by_dates(doc_input) -> Tuple[Document, Dict[str, List]]:
    doc = Document(doc_input)
    paragraphs = doc.paragraphs
    chunks_by_date = {}
    current_date = None
    current_chunk = []
    for para in paragraphs:
        text = para.text.strip()
        match = date_pattern.match(text)
        if match:
            if current_chunk:
                if current_date in chunks_by_date:
                    chunks_by_date[current_date].extend(current_chunk)
                else:
                    chunks_by_date[current_date] = current_chunk
            current_date = match.group(1)
            current_chunk = [para]
        else:
            current_chunk.append(para)
    if current_chunk:
        if current_date in chunks_by_date:
            chunks_by_date[current_date].extend(current_chunk)
        else:
            chunks_by_date[current_date] = current_chunk

    return doc,chunks_by_date


async def enhance_and_store(file_id,doc_bytes,email):
    enhanced_doc_bytes=await highlight_by_semantics(doc_bytes,file_id)
    conn=get_connection()
    cursor=conn.cursor()
    try:
        update_query="""
            update documents set enhanced_doc=%s where document_id=%s 
        """
        print("enhanced document saved")
        cursor.execute(update_query,(enhanced_doc_bytes,file_id))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Database update failed for enhanced document: {str(e)}")
    finally:
        from app.database import db_pool
        if db_pool:
            db_pool.putconn(conn)
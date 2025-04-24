import re
import io
from typing import List,Tuple
from docx import Document
from langchain.prompts import PromptTemplate
from docx.oxml import OxmlElement
from utils import *
from docx.oxml.ns import qn
from app.database import get_connection
from fastapi import HTTPException


highlight_colors = {
    "project-update": "blue",
    "meeting-notes": "cyan",
    "todo": "green",
    "feedback": "yellow",
    "other": "gray"
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

def apply_highlight_preserve_styles(para, color):
    for run in para.runs:
        if run.text.strip():
            highlight = OxmlElement('w:highlight')
            highlight.set(qn('w:val'), color)
            rPr = run._element.get_or_add_rPr()
            rPr.append(highlight)

async def highlight_by_semantics(doc_bytes:bytes)->bytes:
    doc_io = io.BytesIO(doc_bytes)
    doc, chunks = chunk_by_dates(doc_io)
    for chunk in chunks:
        paragraphs = [p.text.strip() for p in chunk] 
        label = await classify_paragraphs(paragraphs) 
        for para in chunk:
            apply_highlight_preserve_styles(para, highlight_colors.get(label, "gray"))
    output_io = io.BytesIO()
    doc.save(output_io)
    output_io.seek(0)
    return output_io.getvalue()

def chunk_by_dates(doc_input)->Tuple[Document,List[List]]:
    doc=Document(doc_input)
    chunks=[]
    paragraphs=doc.paragraphs
    current_chunk=[]
    for para in paragraphs:
        if date_pattern.match(para.text.strip()):
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk=[para]
        else:
            current_chunk.append(para)
    if current_chunk:
        chunks.append(current_chunk)
    return doc,chunks

async def enhance_and_store(file_id,doc_bytes,email):
    enhanced_doc_bytes=await highlight_by_semantics(doc_bytes)
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
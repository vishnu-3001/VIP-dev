from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils import *
from dotenv import load_dotenv
from app.database import get_connection
from fastapi import HTTPException
import json

load_dotenv()
index = get_index()
llm = model()
namespace = "vip"

async def rag_chat(question, doc_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        select_query = """
            SELECT date_label_data FROM documents WHERE document_id = %s;
        """
        cursor.execute(select_query, (doc_id,))
        result = cursor.fetchone()
        if not result or not result[0]:
            raise HTTPException(status_code=404, detail="Document not found or no date label data available.")
        
        date_label_data = result[0]
        prompt = """
<system>
You are a seasoned time-series analyst with deep expertise in date-based and label-based trends. 
You excel at producing two things:
  1. A concise narrative analysis (“answer”)
  2. A JSON object of per-label occurrence counts (“counts”)
Always return _only_ valid JSON.
</system>

<example>
DATA:
[
  {{"date":"2025-01-01","label":"A","value":10}},
  {{"date":"2025-01-02","label":"B","value":5}},
  {{"date":"2025-01-03","label":"A","value":12}}
]

QUESTION: "How many of each label appear?"
OUTPUT:
{{
  "answer": "Label A appears 2 times; Label B appears 1 time.",
  "counts": {{"A": 2, "B": 1}}
}}
</example>

<task>
DATA: {data}
QUESTION: {query}
</task>

<response_format>
Return _only_ valid JSON matching this schema:
{{
  "answer": "<your narrative here>",
  "counts": {{ "<label1>": <int>, "<label2>": <int>, … }}
}}
</response_format>
"""

        
        prompt_template = PromptTemplate(
            input_variables=["data", "query"],
            template=prompt
        )
        chain = prompt_template | llm
        response = await chain.ainvoke({
            "data": json.dumps(date_label_data, default=str),
            "query": question
        })
        if isinstance(response, str):
            output = response
        elif hasattr(response, "content"):
            output = response.content
        else:
            output = str(response)
        output = output.strip().lower()
        output = json.loads(output)
        return output["answer"]
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="LLM response is not valid JSON.")
    except KeyError:
        raise HTTPException(status_code=500, detail="Missing 'answer' key in LLM response.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database or LLM error: {str(e)}")
    finally:
        from app.database import db_pool
        cursor.close()
        if db_pool:
            db_pool.putconn(conn)
    
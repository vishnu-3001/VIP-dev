import os
from dotenv import load_dotenv
from utils import *
from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage
from app.database import get_connection,release_connection
import numpy as np



llm=model()

async def summarize_text(text):
    prompt_template=summary_prompt(text)
    prompt=PromptTemplate(input_variables=["text"],template=prompt_template)
    chain = prompt | llm  
    try:
        summary_response = await chain.ainvoke({"text": text})
        if isinstance(summary_response, AIMessage): 
            summary = summary_response.content
        else:
            raise ValueError("Unexpected response format from LLM chain.")
        summary_embedding = await generate_embeddings(summary)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO documents (content, content_summary, content_vector) 
            VALUES (%s, %s, %s) 
            RETURNING document_id
            """,
            (text, summary, np.array(summary_embedding).tolist()) 
        )
        document_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        release_connection(conn)
        print(f"New document inserted with ID: {document_id}")
        return summary
    except Exception as e:
        print(f"Error during summarization or inserting intp database:{e}")
        raise e
from fastapi import HTTPException
import json
from datetime import datetime
from app.database import get_connection
from utils import *
from langchain.prompts import PromptTemplate

async def get_date_label_data(file_id):
    conn = get_connection()
    cursor=conn.cursor()
    try:
        select_query="""
            select date_label_data from documents where document_id=%s
            """
        cursor.execute(select_query,(file_id,))
        result=cursor.fetchone()
        if not result or not result[0]:
            raise HTTPException(
                status_code =500,
                detail=f"No date label data found for document id {file_id}"
            )
        date_label_data=result[0]
        data=json.loads(date_label_data)
        converted_dict={}
        for date,label in data.items():
            try:
                date_obj = datetime.strptime(date, "%b %d, %Y")
                iso_date = date_obj.strftime("%Y-%m-%d")
                converted_dict[iso_date] = label
            except Exception:
                continue
        yearly_data,monthly_data=group_data(converted_dict)
        analysis=await get_date_analysis(converted_dict)
        response={
            "yearly_data":yearly_data,
            "monthly_data":monthly_data,
            "report":analysis
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Database error:{str(e)}")
    finally:
        from app.database import db_pool
        if db_pool:
            db_pool.putconn(conn)

async def get_date_analysis(data):
    llm=model()
    prompt="""
    <system>
    you are an expert in time series analysis who specilaizes in date and label anaylsis and you can give excellent report
    about them
    <system>
    <task>
    you are provided with a date and label analysis in json format your task is to give a detailed report in 350-400 words
    about your findings on that data like, which label is most used and what is the trend that you have seen in the lables,what
    is the contribution to different labels in the data over the time.
    {data}
    give me the report in json format with the following keys
    {{
        "report":"lorem ipsum dolor sit amet....",
    }}
    <task>
    """
    prompt_template=PromptTemplate(template=prompt,input_variables=["data"])
    chain=prompt_template | llm
    response=await chain.ainvoke({"data":data})
    output = response.content.strip().lower() if hasattr(response, "content") else response.strip().lower()
    output=json.loads(output)
    return output["report"]


def group_data(converted_dict):
    yearly_data = {}
    monthly_data = {}
    for key, label in converted_dict.items():
        date_obj = datetime.strptime(key, "%Y-%m-%d")
        year = date_obj.year
        month = date_obj.month
        month_year_label = f"{month:02d}-{year}"
        if year not in yearly_data:
            yearly_data[year] = {}
        if label not in yearly_data[year]:
            yearly_data[year][label] = 0
        yearly_data[year][label] += 1
        if month_year_label not in monthly_data:
            monthly_data[month_year_label] = {}
        if label not in monthly_data[month_year_label]:
            monthly_data[month_year_label][label] = 0
        monthly_data[month_year_label][label] += 1

    return yearly_data, monthly_data





            





from fastapi import HTTPException
import json
from datetime import datetime
from app.database import get_connection
from utils import *
from langchain.prompts import PromptTemplate
from collections import defaultdict

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
        semester_data,quarterly_data=academic_year_data(converted_dict)
        component_data=component_wise_data(converted_dict)
        response={
            "yearly_data":yearly_data,
            "monthly_data":monthly_data,
            "report":"",
            "semester_data":semester_data,
            "quarterly_data":quarterly_data,
            "component_data":component_data
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

def semester_suffix(date_str):
    date_obj=datetime.strptime(date_str,"%Y-%m-%d")
    year_suffix=str(date_obj.year)[-2:]
    month=date_obj.month
    if 1<=month<=5:
        return f"Spring {year_suffix}"
    elif 8<=month<=12:
        return f"Fall {year_suffix}"
    else:
        return f"Summer {year_suffix}"

def get_academic_quarter(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    month = date_obj.month
    year = date_obj.year

    if 9 <= month <= 11:
        quarter_name = "Fall"
        quarter_year = year
    elif month == 12:
        quarter_name = "Winter"
        quarter_year = year + 1
    elif 1 <= month <= 2:
        quarter_name = "Winter"
        quarter_year = year
    elif 3 <= month <= 5:
        quarter_name = "Spring"
        quarter_year = year
    else: 
        quarter_name = "Summer"
        quarter_year = year

    year_suffix = str(quarter_year)[-2:]
    return f"{quarter_name} {year_suffix}"


def academic_year_data(grouped_data):
    semester_data = {}
    quarterly_data = {}

    for date_str, label in grouped_data.items():
        semester = semester_suffix(date_str)
        quarter = get_academic_quarter(date_str)
        if semester not in semester_data:
            semester_data[semester] = {}
        if label not in semester_data[semester]:
            semester_data[semester][label] = 0
        semester_data[semester][label] += 1
        if quarter not in quarterly_data:
            quarterly_data[quarter] = {}
        if label not in quarterly_data[quarter]:
            quarterly_data[quarter][label] = 0
        quarterly_data[quarter][label] += 1

    return semester_data, quarterly_data

def component_wise_data(grouped_data):
    component_data=defaultdict(int)
    for date_str, label in grouped_data.items():
        component_data[label] += 1
    return component_data
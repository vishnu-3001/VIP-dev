from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

async def analyze_collaboration(log_entries: dict):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model="gpt-3.5-turbo",api_key=OPENAI_API_KEY)
    prompt_template = """
    You are a team collaboration analyst. Use the log data below to:

        Assign a collaboration score (1-10) based on defined criteria.
        Provide key observations about team dynamics.
        Suggest specific actions for improvement.
        {log_entries}
        Criteria for Scoring:
        Participation Balance: Are contributions evenly distributed?
        Consistency: Are contributions spread over time or clustered?
        Engagement: Do all members contribute actively?
        Collaboration Timing: Is the work synchronous or asynchronous?
        Workload Distribution: Are contributions proportionate?
        Constraints:
        Always base the score on the five criteria provided.
        Avoid assumptions beyond the given data.
        Use precise, concise language for insights and recommendations.
    """
    prompt = PromptTemplate(input_variables=["log_entries"], template=prompt_template)
    chain = LLMChain(prompt=prompt, llm=llm)
    log_entries_str = "\n".join([f"{k}: {', '.join(v)}" for k, v in log_entries.items()])
    return await chain.arun({"log_entries": log_entries_str})

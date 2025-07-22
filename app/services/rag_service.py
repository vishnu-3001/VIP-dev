from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils import *
from dotenv import load_dotenv
load_dotenv()
index = get_index()
emodel = embeddings_model()
llm = model()
namespace = "vip"

vectorStore = PineconeVectorStore(index=index, embedding=emodel, namespace=namespace,text_key="text")
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful assistant. Use the context below to answer the question.

Context:
{context}

Question:
{question}

Answer:"""
)
output_parser = StrOutputParser()
def infer_filter_from_query(question: str,doc_id) -> dict:
    q = question.lower()
    if "how many" in q and "project" in q:
        return {"label": "summary","doc_id":doc_id}
    if "meeting" in q:
        return {"label": "meeting-notes","doc_id":doc_id}
    elif "project" in q:
        return {"label": "project-update","doc_id":doc_id}
    elif "todo" in q:
        return {"label": "todo","doc_id":doc_id}
    return {"doc_id":doc_id}  
async def rag_chat(question,doc_id):
    try:
        filter_metadata = infer_filter_from_query(question,doc_id)
        print(filter_metadata)
        filtered_retriever = vectorStore.as_retriever(
            search_kwargs={"k": 1, "filter": filter_metadata}
        )
        rag_chain = (
            {
                "context": filtered_retriever,
                "question": lambda x: x
            }
            | prompt_template
            | llm
            | output_parser
        )
        retrieved_docs = await filtered_retriever.ainvoke(question)
        print(retrieved_docs)
        enriched_docs = []
        for doc in retrieved_docs:
            enriched_docs.append({
                "doc_id": doc.metadata.get("doc_id", "unknown"),
                "metadata": doc.metadata,
                "content": doc.page_content
            })
        response = await rag_chain.ainvoke(question)
        output = response.content.strip() if hasattr(response, "content") else response.strip()

        return output if output else "No relevant information found.",
    finally:
        index.close()


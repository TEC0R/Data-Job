import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableSequence
from langchain_core.prompts import PromptTemplate


@st.cache_resource
def load_embeddings():
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/LaBSE')
    return embeddings

embeddings = load_embeddings()
vectorstore = PineconeVectorStore(index_name='jobsdata', embedding=embeddings, pinecone_api_key=st.secrets['PINECONE_API_KEY'])


def reco_annonce_job(json_profile):
    class Job(BaseModel):
        entreprise: str = Field(description="the name of the entreprise")
        poste: str = Field(description="the name of the job position")
        contract: str = Field(description="the contract type")
        salary: str = Field(description="the salary for the job")
        link: str = Field(description="url link to the job offer")
        skill: str = Field(description="list of skills for the job offer")

    parser = JsonOutputParser(pydantic_object=Job)

    retriever = vectorstore.as_retriever()


    model = ChatGroq(temperature=0, model_name="llama3-70b-8192", groq_api_key=st.secrets['GROQ_API_KEY'])

    def read_system_prompt(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    file_path = './streamlit_function/pages/prompt_tool_reco_job.txt'
    system_prompt = read_system_prompt(file_path)

    prompt = PromptTemplate(
        template=system_prompt,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )


    rag_chain = RunnableSequence(
        retriever |
        prompt |
        model |
        parser
    )

    response = rag_chain.invoke(json_profile)
    return response
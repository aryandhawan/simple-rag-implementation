from entity.config_entity import GenerationConfig
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

class Generation:
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.llm = ChatGroq(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.prompt = ChatPromptTemplate.from_template("""
You are a friendly and knowledgeable AI/ML assistant with broad knowledge of artificial intelligence and machine learning.

Follow these rules:
1. For greetings and casual conversation — respond naturally and warmly
2. For questions covered in the context below — use the context to give a precise, grounded answer
3. For general AI/ML questions — answer helpfully using your own knowledge
4. Never mention the context, never say "I don't have information" if you actually know the answer
5. Only say you don't know for topics completely outside AI/ML/tech

Context:
{context}

Question:
{question}
""")
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate_response(self, query: str, retrieved_docs: list) -> str:
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        response = self.chain.invoke({"context": context, "question": query})
        return response
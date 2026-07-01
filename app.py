# app.py
import streamlit as st
from pathlib import Path
from config.configuration import ConfigurationManager
from components.embedding import Embedding
from components.retrieval import Retriever
from components.generation import Generation

st.set_page_config(
    page_title="AI/ML Knowledge Bot",
    page_icon="🤖",
    layout="centered"
)

@st.cache_resource
def load_pipeline():
    config_manager = ConfigurationManager()
    
    embedding_config = config_manager.get_embedding_config()
    embedding = Embedding(config=embedding_config)
    vector_store = embedding.create_embeddings(chunks=None)
    
    retrieval_config = config_manager.get_retrieval_config()
    retriever_component = Retriever(config=retrieval_config, vector_store=vector_store)
    langchain_retriever = retriever_component.get_retriever()
    
    generation_config = config_manager.get_generation_config()
    generation_component = Generation(config=generation_config)
    
    return langchain_retriever, generation_component

# Header
st.title("🤖 AI/ML Knowledge Bot")
st.caption("Ask anything about AI, ML, and LLM concepts")
st.divider()

# Load pipeline silently
langchain_retriever, generation_component = load_pipeline()

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if query := st.chat_input("Ask a question about AI/ML..."):
    
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                retrieved_docs = langchain_retriever.invoke(query)
                response = generation_component.generate_response(
                    query=query,
                    retrieved_docs=retrieved_docs
                )
                st.markdown(response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
            except Exception as e:
                st.error(f"Something went wrong: {e}")
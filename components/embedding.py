from entity.config_entity import EmbeddingConfig
from config.configuration import read_yaml,create_directories
from pathlib import Path
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

class Embedding:
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    def create_embeddings(self, chunks):
        if os.path.exists(self.config.vector_store_path) and os.listdir(self.config.vector_store_path):
            print("Vector store already exists, loading instead of re-embedding")
            return Chroma(
                persist_directory=str(self.config.vector_store_path),
                embedding_function=self.embedding_model,
                collection_name="ai_ml_concepts"
            )
        
        print("Creating new vector store")
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding_model,
            persist_directory=str(self.config.vector_store_path),
            collection_name="ai_ml_concepts"
        )
        return vector_store 
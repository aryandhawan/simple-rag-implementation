from config.configuration import ConfigurationManager,create_directories,read_yaml
from entity.config_entity import RetrievalConfig
from pathlib import Path
from components.embedding import Embedding



class Retriever:
    def __init__(self, config: RetrievalConfig, vector_store):
        self.config = config
        self.vector_store = vector_store  

    def retrieval(self, query: str):
        top_k = self.config.top_k
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": top_k}
        )

        return retriever.invoke(query)
    

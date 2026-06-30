# components/data_ingestion.py
from entity.config_entity import DataIngestionConfig
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from config.configuration import ConfigurationManager

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def load_documents(self):
        loader = DirectoryLoader(
            str(self.config.corpus_dir),
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        documents = loader.load()
        print(f"Loaded {len(documents)} documents from {self.config.corpus_dir}")
        return documents
    
config_manager = ConfigurationManager()
data_ingestion_config = config_manager.get_data_ingestion_config()

obj = DataIngestion(config=data_ingestion_config)
documents = obj.load_documents()
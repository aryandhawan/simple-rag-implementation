from entity.config_entity import DataIngestionConfig, ChunkingConfig
from config.configuration import ConfigurationManager, read_yaml, create_directories
from components.data_ingestion import DataIngestion
from components.chunking import Chunking
from components.embedding import Embedding

config_manager = ConfigurationManager()

data_ingestion_config = config_manager.get_data_ingestion_config()
data_ingestion = DataIngestion(config=data_ingestion_config)
documents = data_ingestion.load_documents()

chunking_config = config_manager.get_chunking_config()
chunking = Chunking(config=chunking_config)
chunks = chunking.chunk_documents(documents)  

embedding_config = config_manager.get_embedding_config()
embedding = Embedding(config=embedding_config)
vector_store = embedding.create_embeddings(chunks)
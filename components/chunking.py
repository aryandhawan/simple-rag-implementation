from entity.config_entity import ChunkingConfig
from config.configuration import read_yaml,create_directories
from pathlib import Path
from entity.config_entity import ChunkingConfig
from langchain_text_splitters import RecursiveCharacterTextSplitter


class Chunking:
    def __init__(self, config: ChunkingConfig):
        self.config = config
        create_directories([Path(self.config.root_dir)], verbose=True)
    
    def chunk_documents(self, documents):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,      
            chunk_overlap=self.config.chunk_overlap 
        )

        chunks = text_splitter.split_documents(documents)

        print(f"Created {len(chunks)} chunks from {len(documents)} documents.")

        return chunks
    

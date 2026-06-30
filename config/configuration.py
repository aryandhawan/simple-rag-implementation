from dataclasses import dataclass
import json
from pathlib import Path
import yaml
import os
from ensure import ensure_annotations
from box import ConfigBox
from entity.config_entity import ChunkingConfig, DataIngestionConfig,EmbeddingConfig

@ensure_annotations
def read_yaml(path_to_yaml: Path) -> ConfigBox:
    with open(path_to_yaml, 'r') as yaml_file:
        content = yaml.safe_load(yaml_file)
    return ConfigBox(content)

@ensure_annotations
def create_directories(path_to_directories: list,verbose=True):
    for path in path_to_directories:
        os.makedirs(path, exist_ok=True)
        if verbose:
            print(f"Directory created: {path}")

@ensure_annotations
def get_size(path: Path) -> str:
    size_in_bytes = os.path.getsize(path)
    size_in_kb = size_in_bytes / 1024
    size_in_mb = size_in_kb / 1024
    return f"{size_in_mb:.2f} MB"

@ensure_annotations
def save_json(path: Path, data: dict):
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

@ensure_annotations
def load_json(path: Path) -> ConfigBox:
    with open(path,'r') as json_file:
        content=json.load(json_file)
    return ConfigBox(content)

class ConfigurationManager:
    def __init__(self, config_filepath: Path = Path("config/config.yaml")):
        self.config = read_yaml(config_filepath)
        create_directories([Path(self.config.artifact_root)], verbose=True) # initialised to make directories for artifacts_root

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion
        create_directories([Path(config.root_dir)], verbose=True)
        data_ingestion_config = DataIngestionConfig(
            root_dir=Path(config.root_dir),
            corpus_dir=Path(config.corpus_dir),
            eval_set_path=Path(config.eval_set_path)
        )
        return data_ingestion_config
    
    def get_chunking_config(self)-> ChunkingConfig:
        config=self.config.chunking
        create_directories([Path(config.root_dir)], verbose=True)
        # Create and return a ChunkingConfig instance
        return ChunkingConfig(
            root_dir=Path(config.root_dir),
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
    
    def get_embedding_config(self)-> EmbeddingConfig:
        config=self.config.embedding
        create_directories([Path(config.root_dir)], verbose=True)
        # Create and return a EmbeddingConfig instance
        return EmbeddingConfig(
            root_dir=Path(config.root_dir),
            model_name=config.model_name,
            vector_store_path=config.vector_store_path
        )

    

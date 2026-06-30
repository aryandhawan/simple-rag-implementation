from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DataIngestionConfig:
    root_dir: Path
    corpus_dir: Path
    eval_set_path: Path

@dataclass(frozen=True)
class ChunkingConfig:
    root_dir: Path
    chunk_size: int
    chunk_overlap: int

@dataclass(frozen=True)
class EmbeddingConfig:
    root_dir: Path
    model_name: str
    vector_store_path: Path
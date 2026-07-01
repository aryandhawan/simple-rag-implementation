from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DataIngestionConfig:
    root_dir: Path
    corpus_dir: Path

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

@dataclass(frozen=True)
class RetrievalConfig:
    root_dir: Path
    top_k: int

@dataclass(frozen=True)
class GenerationConfig:
    root_dir: Path
    model_name: str
    temperature: float
    max_tokens: int

@dataclass(frozen=True)
class EvaluationConfig:
    root_dir: Path
    eval_set_path: Path
    judge_model_name: str
    smoke_test_questions: list[int]
    keyword_coverage_threshold: float
    accuracy_threshold: float
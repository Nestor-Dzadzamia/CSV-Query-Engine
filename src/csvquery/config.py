
from dataclasses import dataclass, field
from multiprocessing import cpu_count

@dataclass(frozen=True)
class PipelineConfig:
    chunk_size: int = 1_000_000
    encoding: str = "utf-8-sig"
    max_workers: int = field(default_factory=cpu_count)

    def __post_init__(self):
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.max_workers <= 0:
            raise ValueError("max_workers must be positive")

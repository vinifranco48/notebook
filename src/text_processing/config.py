
from dataclasses import dataclass
# Definição da configuração de processamento de texto
@dataclass
class TextProcessingConfig:
    chunk_size: int = 1000
    min_chunk_size: int = 100
    overlap_size: int = 50
    max_threads: int = 4
    language: str = "pt"
    remove_numbers: bool = False
    remove_punctuation: bool = False
    remove_whitespace: bool = True

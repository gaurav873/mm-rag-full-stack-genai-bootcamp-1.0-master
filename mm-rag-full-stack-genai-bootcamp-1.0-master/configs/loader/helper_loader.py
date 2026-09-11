from pydantic import BaseModel, ValidationError,Field
import json
import os
from pathlib import Path
from functools import lru_cache
from config import BASE_DIR


class ModalityEntry(BaseModel):
    extensions: list[str] = Field(min_length=1)
    max_size_mb: int = Field(gt=0)
    embedder: str = Field(min_length=1)

@lru_cache
def load_modality_config() -> dict[str, ModalityEntry]:
    config_path = BASE_DIR / "configs" / "data" / "modalities.json"
    # full_path = (BASE_DIR / config_path).resolve()

    if not config_path.exists():
        raise FileNotFoundError(
            f"Modality config not found at {config_path}. "
            f"Set MODALITY_CONFIG_PATH env var or check the default path."
        )

    with open(config_path, "r") as f:
        raw = json.load(f)

    try:
        return {
            name: ModalityEntry(**entry)
            for name, entry in raw.items()
        }
    except ValidationError as e:
        raise ValueError(
            f"Invalid modality config at {config_path}: {e}"
        )

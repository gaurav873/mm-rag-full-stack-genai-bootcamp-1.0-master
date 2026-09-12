from pydantic import BaseModel, ValidationError,Field
import json
from functools import lru_cache
from api.configs.settings import BASE_DIR


class ModalityEntry(BaseModel):
    extensions: list[str] = Field(min_length=1)
    max_size_mb: int = Field(gt=0)
    embedder: str = Field(min_length=1)

@lru_cache
def Validate_Document_Format() -> dict[str, ModalityEntry]:
    config_path = BASE_DIR / "data" / "modalities.json"
    # full_path = (BASE_DIR / config_path).resolve()

    if not config_path.exists():
        raise FileNotFoundError(
            f"Modality config not found at {config_path}. "
            f"Set MODALITY_CONFIG_PATH env var or check the default path."
        )

    with open(config_path, "r") as f:
        raw = json.load(f)
        print(f"Loaded modality config from {config_path}: {raw}")  

    try:
        return {
            name: ModalityEntry(**entry)
            for name, entry in raw.items()
        }
    except ValidationError as e:
        raise ValueError(
            f"Invalid modality config at {config_path}: {e}"
        )

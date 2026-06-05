"""Configuration loader."""

from pathlib import Path
import yaml

DEFAULT_CONFIG = {
    "model": {
        "backbone": "efficientnet_b0",
        "num_classes": 4,
        "use_attention": True,
    },
    "data": {
        "image_size": 224,
        "normalize_mean": [0.485, 0.456, 0.406],
        "normalize_std": [0.229, 0.224, 0.225],
    },
}


class ConfigLoader:
    @staticmethod
    def load_config(config_path: str) -> dict:
        path = Path(config_path)
        if not path.exists():
            return DEFAULT_CONFIG.copy()
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or DEFAULT_CONFIG.copy()

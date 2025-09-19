from pathlib import Path
from pydantic import ValidationError
import yaml

from simulation.schema import ConfigSchema

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "simulation/config.yaml"


def load_config() -> ConfigSchema:
    with open(CONFIG_PATH) as f:
        config_dict = yaml.safe_load(f)

    try:
        config = ConfigSchema(**config_dict)
        return config
    except ValidationError as e:
        raise ("Validation error:", e)


def save_config(configuration: ConfigSchema):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(configuration.model_dump(), f, sort_keys=False)

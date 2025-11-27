import yaml
from pydantic import ValidationError

from simulation.training.schema import TrainingConfigSchema
from pathlib import Path

TRAINING_DIR = Path(__file__).resolve().parents[0]
CONFIG_PATH = TRAINING_DIR / "config.yaml"


def load_training_config() -> TrainingConfigSchema:
    with open(CONFIG_PATH) as f:
        config_dict = yaml.safe_load(f)

    try:
        config = TrainingConfigSchema(**config_dict)
        return config
    except ValidationError as e:
        raise ("Validation error:", e)


def save_training_config(configuration: TrainingConfigSchema):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(configuration.model_dump(mode='json'), f, sort_keys=False)

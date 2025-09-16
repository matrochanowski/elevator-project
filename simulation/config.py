from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "simulation/config.yaml"

def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

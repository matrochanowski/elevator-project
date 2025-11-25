import simulation.gui.main as tgt
from pathlib import Path
import os

if __name__ == "__main__":
    target_dir = Path(__file__).parent / "gui"
    old = os.getcwd()
    os.chdir(target_dir)
    tgt.execute()

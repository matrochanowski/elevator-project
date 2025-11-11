from pathlib import Path
import os
from datetime import datetime
import pickle

from simulation.core.elevator_system import ElevatorSystem

SIMULATION_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = SIMULATION_DIR / "logs"


class SimulationLogger:
    def __init__(self, filename_prefix="run"):
        os.makedirs(LOG_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_path = os.path.join(LOG_DIR,
                                        f"{filename_prefix}_{timestamp}.parquet")
        self.system_path = os.path.join(LOG_DIR, f"{filename_prefix}_{timestamp}_system.pkl")
        self.buffer = []

    def save_system_state(self, system: ElevatorSystem):
        """Saves system object to pickle."""
        try:
            with open(self.system_path, "wb") as f:
                pickle.dump(system, f)
            print(f"[LOG] Zapisano stan systemu do pliku: {self.system_path}")
        except Exception as e:
            print(f"[LOG] Błąd podczas zapisu systemu: {e}")

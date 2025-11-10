from pathlib import Path
import pandas as pd
import os
from datetime import datetime

SIMULATION_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = SIMULATION_DIR / "logs"


class SimulationLogger:
    def __init__(self, filename_prefix="run"):
        os.makedirs(LOG_DIR, exist_ok=True)
        self.output_path = os.path.join(LOG_DIR,
        f"{filename_prefix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.parquet")
        self.buffer = []

    def log_step(self, step_idx, system):
        """Dodaje dane z jednego kroku symulacji do bufora."""
        for eid, elv in enumerate(system.elevators):
            self.buffer.append({
                "step": step_idx,
                "elevator_id": eid,
                "floor": elv.current_floor,
                "state": elv.state,
                "delay": elv.delay,
                "num_inside": len(elv.people_inside_arr),
                "requested_floors": len(system.requested_floors),
            })

    def finalize(self):
        """Zapisuje wszystkie zebrane dane do pliku Parquet po zakończeniu symulacji."""
        if not self.buffer:
            print("[LOG] Brak danych do zapisania.")
            return

        df = pd.DataFrame(self.buffer)
        df.to_parquet(self.output_path, index=False, compression="snappy")
        print(f"[LOG] Zapisano {len(df)} rekordów do pliku: {self.output_path}")

    def save_results(self):
        pass

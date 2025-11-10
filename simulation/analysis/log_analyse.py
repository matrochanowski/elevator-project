from pathlib import Path
import pandas as pd
import os

# katalog z logami - taki sam jak w SimulationLogger
SIMULATION_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = SIMULATION_DIR / "logs"


def read_simulation_log(filename: str):
    """
    Wczytuje log z pliku Parquet i wypisuje jego zawartość.
    :param filename: nazwa pliku z logiem, np. 'run_20251104_120355.parquet'
    """
    file_path = LOG_DIR / filename

    if not file_path.exists():
        print(f"[ERROR] Plik {file_path} nie istnieje.")
        return

    try:
        df = pd.read_parquet(file_path)
    except Exception as e:
        print(f"[ERROR] Nie udało się wczytać pliku {filename}: {e}")
        return

    print(f"[INFO] Wczytano {len(df)} rekordów z pliku {filename}")
    print(df.head(20))  # pokaż pierwsze 20 wierszy
    df.to_excel("excel.xlsx")


# przykład użycia (można odpalić bezpośrednio)
if __name__ == "__main__":
    read_simulation_log("run_20251104_150346.parquet")

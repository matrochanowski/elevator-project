import sys
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from ui_config import Ui_MainWindow  # nazwa klasy zależy od pliku .ui


class ElevatorSimConfig(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # podłączenie przycisku
        self.startButton.clicked.connect(self.start_simulation)

    def start_simulation(self):
        try:
            result = subprocess.run(
                [sys.executable, "../engine/runner.py"],
                check=True
            )
            QMessageBox.information(self, "Sukces", "Symulacja zakończona.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Błąd", f"Symulacja nie powiodła się:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ElevatorSimConfig()
    window.show()
    sys.exit(app.exec())

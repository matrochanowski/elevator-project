import subprocess
import sys
from PySide6.QtWidgets import QMessageBox


class MainMenuPage:
    def __init__(self, window):
        self.window = window

    def connect_buttons(self):
        self.window.startButton.clicked.connect(self.start_simulation)
        self.window.settingsButton.clicked.connect(self.window.show_settings)
        self.window.reinforcementButton.clicked.connect(self.window.show_reinforcement_panel)

    def start_simulation(self):
        try:
            subprocess.run([sys.executable, "../engine/runner.py"], check=True)
            QMessageBox.information(self.window, "Sukces", "Symulacja zakończona.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self.window, "Błąd", f"Symulacja nie powiodła się:\n{e}")

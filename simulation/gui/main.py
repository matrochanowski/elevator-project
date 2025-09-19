import sys
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QSpinBox
from ui_config import Ui_MainWindow

from simulation.schema import ConfigSchema, ElevatorConfigSchema
from simulation.config import save_config, load_config


class ElevatorSimConfig(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Podłączenie przycisków
        self.startButton.clicked.connect(self.start_simulation)
        self.settingsButton.clicked.connect(self.show_settings)
        self.MenuButton.clicked.connect(self.show_main)
        self.SaveButton.clicked.connect(self.save_settings)

        self.ElevatorsSpinBox.valueChanged.connect(self.on_num_elevators_changed)

        self.ElevatorTable.setColumnCount(2)
        self.ElevatorTable.setHorizontalHeaderLabels(["Max people", "Speed"])
        self.ElevatorTable.horizontalHeader().setStretchLastSection(True)

        # Wczytaj początkową liczbę wind
        self.on_num_elevators_changed(self.ElevatorsSpinBox.value())

        self.load_settings()

    def load_settings(self):
        config = load_config()

        # Pola ogólne
        self.FloorsSpinBox.setValue(config.floors)
        self.StepsHorizontalSlider.setValue(config.steps)
        self.MaxPeopleFloorSpinBox.setValue(config.max_people_floor)
        self.VisualisationRadioButton.setChecked(config.visualisation)

        # Windy
        num_elevators = len(config.elevators)
        self.ElevatorsSpinBox.setValue(num_elevators)  # ustawia też tabelę
        self.on_num_elevators_changed(num_elevators)  # żeby stworzyć spinboxy

        for row, elevator in enumerate(config.elevators):
            max_people_spin = self.ElevatorTable.cellWidget(row, 0)
            speed_spin = self.ElevatorTable.cellWidget(row, 1)

            if max_people_spin:
                max_people_spin.setValue(elevator.max_people)
            if speed_spin:
                speed_spin.setValue(elevator.speed)

    # --------------------------------------------------
    # Obsługa widoków (StackedWidget)
    # --------------------------------------------------
    def show_settings(self):
        self.stackedWidget.setCurrentIndex(1)  # Page 2 - ustawienia

    def show_main(self):
        self.stackedWidget.setCurrentIndex(0)  # Page 1 - główny widok

    # --------------------------------------------------
    # Start symulacji
    # --------------------------------------------------
    def start_simulation(self):
        try:
            # Możesz tutaj dodać pobieranie wartości z pól jeśli chcesz je przekazać
            # floors = self.FloorsSpinBox.value()
            # steps = self.StepsHorizontalSlider.value()
            subprocess.run(
                [sys.executable, "../engine/runner.py"],
                check=True
            )
            QMessageBox.information(self, "Sukces", "Symulacja zakończona.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Błąd", f"Symulacja nie powiodła się:\n{e}")

    def on_num_elevators_changed(self, value: int):
        self.ElevatorTable.setRowCount(value)
        for row in range(value):
            # Max people (SpinBox)
            spin_max = QSpinBox()
            spin_max.setRange(1, 20)
            spin_max.setValue(5)
            self.ElevatorTable.setCellWidget(row, 0, spin_max)

            # Delay (SpinBox)
            spin_delay = QSpinBox()
            spin_delay.setRange(1, 30)
            spin_delay.setValue(5)
            self.ElevatorTable.setCellWidget(row, 1, spin_delay)

    # --------------------------------------------------
    # Obsługa przycisku Save w ustawieniach
    # --------------------------------------------------
    def save_settings(self):
        floors = self.FloorsSpinBox.value()
        steps = self.StepsHorizontalSlider.value()
        max_people_floor = self.MaxPeopleFloorSpinBox.value()

        visualisation = self.VisualisationRadioButton.isChecked()

        # elevators = [ElevatorConfigSchema(max_people=max_people_elevator, speed=speed, starting_floor=0)]

        elevators = []
        for row in range(self.ElevatorTable.rowCount()):
            max_people = self.ElevatorTable.cellWidget(row, 0).value()
            speed = self.ElevatorTable.cellWidget(row, 1).value()
            elevators.append(ElevatorConfigSchema(
                max_people=max_people,
                speed=speed,
                starting_floor=0
            ))

        configuration = ConfigSchema(floors=floors,
                                     steps=steps,
                                     max_people_floor=max_people_floor,
                                     visualisation=visualisation,
                                     elevators=elevators)

        save_config(configuration)

        # Tutaj możesz wstawić logikę zapisu lub przekazania ustawień
        print(f"Zapisano ustawienia: floors={floors}, steps={steps}")
        QMessageBox.information(self, "Zapisano", "Ustawienia zostały zapisane.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ElevatorSimConfig()
    window.show()
    sys.exit(app.exec())

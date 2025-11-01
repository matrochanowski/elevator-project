import sys
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QSpinBox
from ui_config import Ui_MainWindow

from simulation.schema import ConfigSchema, ElevatorConfigSchema
from simulation.config import save_config, load_config

from simulation.enums import AlgorithmEnum
from simulation.utils import extract_params_suffix


class ElevatorSimConfig(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Podłączenie przycisków
        self.startButton.clicked.connect(self.start_simulation)
        self.settingsButton.clicked.connect(self.show_settings)
        self.settingsButton_2.clicked.connect(self.show_settings)
        self.MenuButton.clicked.connect(self.show_main)
        self.MenuButton_2.clicked.connect(self.show_main)
        self.TrafficConfigurationButton.clicked.connect(self.show_traffic_conf)
        self.reinforcementButton.clicked.connect(self.show_reinforcement_panel)
        self.SaveButton.clicked.connect(self.save_settings)
        self.AlgorithmComboBox.currentIndexChanged.connect(self.on_algorithm_changed)

        self.ElevatorsSpinBox.valueChanged.connect(self.on_num_elevators_changed)

        self.ElevatorTable.setColumnCount(3)
        self.ElevatorTable.setHorizontalHeaderLabels(["Max people", "Speed", "Starting floor"])
        self.ElevatorTable.horizontalHeader().setStretchLastSection(True)

        self.on_num_elevators_changed(self.ElevatorsSpinBox.value())
        self.ModelComboBox.currentIndexChanged.connect(self.on_model_changed)

        for alg in AlgorithmEnum:
            self.AlgorithmComboBox.addItem(alg.pretty, userData=alg)

        self.load_settings()

    def load_settings(self):
        config = load_config()

        # Pola ogólne
        self.FloorsSpinBox.setValue(config.floors)
        self.StepsHorizontalSlider.setValue(config.steps)
        self.MaxPeopleFloorSpinBox.setValue(config.max_people_floor)
        self.VisualisationRadioButton.setChecked(config.visualisation)
        index = self.AlgorithmComboBox.findData(config.algorithm)
        if index != -1:
            self.AlgorithmComboBox.setCurrentIndex(index)

        index = self.ModelComboBox.findData(config.model)
        if index != -1:
            self.ModelComboBox.setCurrentIndex(index)

        # Windy
        num_elevators = len(config.elevators)

        self.ElevatorsSpinBox.setValue(num_elevators)  # ustawia też tabelę
        self.on_num_elevators_changed(num_elevators)  # żeby stworzyć spinboxy

        for row, elevator in enumerate(config.elevators):
            max_people_spin = self.ElevatorTable.cellWidget(row, 0)
            speed_spin = self.ElevatorTable.cellWidget(row, 1)
            floor_spin = self.ElevatorTable.cellWidget(row, 2)

            if max_people_spin:
                max_people_spin.setValue(elevator.max_people)
            if speed_spin:
                speed_spin.setValue(elevator.speed)
            if floor_spin:
                floor_spin.setValue(elevator.starting_floor)

    def on_algorithm_changed(self, index):
        alg = AlgorithmEnum(self.AlgorithmComboBox.itemData(index))

        if alg.needs_model:
            models = alg.list_models()
            self.ModelComboBox.clear()
            for model in models:
                self.ModelComboBox.addItem(model, model)
            self.ModelComboBox.setEnabled(True)

            self.label_7.setHidden(False)
            self.label_8.setHidden(False)
            self.label_9.setHidden(False)
            self.label_10.setHidden(False)
            self.label_11.setHidden(False)
        else:
            self.ModelComboBox.clear()
            self.ModelComboBox.setEnabled(False)

            self.label_7.setHidden(True)
            self.label_8.setHidden(True)
            self.label_9.setHidden(True)
            self.label_10.setHidden(True)
            self.label_11.setHidden(True)

    def on_model_changed(self, index):
        model_name = self.ModelComboBox.itemData(index)
        if not model_name:
            return

        n_elevators, n_floors = extract_params_suffix(model_name)

        self.FloorsSpinBox.setValue(n_floors)
        self.ElevatorsSpinBox.setValue(n_elevators)

        self.label_10.setText(str(n_floors))
        self.label_11.setText(str(n_elevators))

    def show_settings(self):
        self.stackedWidget.setCurrentIndex(1)  # Page 2 - settings

    def show_main(self):
        self.stackedWidget.setCurrentIndex(0)  # Page 1 - main menu

    def show_traffic_conf(self):
        self.stackedWidget.setCurrentIndex(2)  # Page 3 - traffic configuration

    def show_reinforcement_panel(self):
        self.stackedWidget.setCurrentIndex(3)  # Page 4 - reinforcement learning panel

    def start_simulation(self):
        try:
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

            # Starting floor
            spin_starting_floor = QSpinBox()
            spin_starting_floor.setRange(0, load_config().floors)
            spin_starting_floor.setValue(0)
            self.ElevatorTable.setCellWidget(row, 2, spin_starting_floor)

    def save_settings(self, index):
        floors = self.FloorsSpinBox.value()
        steps = self.StepsHorizontalSlider.value()
        max_people_floor = self.MaxPeopleFloorSpinBox.value()

        visualisation = self.VisualisationRadioButton.isChecked()

        algorithm = self.AlgorithmComboBox.currentData()

        model = self.ModelComboBox.currentData()

        alg = AlgorithmEnum(self.AlgorithmComboBox.itemData(index))
        if alg.needs_model:
            n_elevators_n_floors = extract_params_suffix(model)
            if n_elevators_n_floors != (self.ElevatorTable.rowCount(), floors):
                QMessageBox.warning(self, "Wrong configuration!", "Number of elevators and number of floors "
                                                                  "doesn't match the model's properties")
                return

        # elevators = [ElevatorConfigSchema(max_people=max_people_elevator, speed=speed, starting_floor=0)]

        elevators = []
        for row in range(self.ElevatorTable.rowCount()):
            max_people = self.ElevatorTable.cellWidget(row, 0).value()
            speed = self.ElevatorTable.cellWidget(row, 1).value()
            starting_floor = self.ElevatorTable.cellWidget(row, 2).value()
            elevators.append(ElevatorConfigSchema(
                max_people=max_people,
                speed=speed,
                starting_floor=starting_floor
            ))

        configuration = ConfigSchema(floors=floors,
                                     steps=steps,
                                     max_people_floor=max_people_floor,
                                     visualisation=visualisation,
                                     elevators=elevators,
                                     algorithm=algorithm,
                                     model=model)

        save_config(configuration)

        print(f"Zapisano ustawienia: floors={floors}, steps={steps}")
        QMessageBox.information(self, "Saved", "Settings saved successfully.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ElevatorSimConfig()
    window.show()
    sys.exit(app.exec())

import sys
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QSpinBox
from ui_config import Ui_MainWindow

from simulation.schema import ConfigSchema, ElevatorConfigSchema, TrafficConfigSchema
from simulation.config import save_config, load_config

from simulation.enums import AlgorithmEnum, TrafficGeneratorEnum, UpPeakParams, DownPeakParams, MixedPeakParams
from simulation.utils import extract_params_suffix


class ElevatorSimConfig(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Podłączenie przycisków
        self.startButton.clicked.connect(self.start_simulation)
        self.settingsButton.clicked.connect(self.show_settings)
        self.settingsButton_2.clicked.connect(self.show_settings)
        self.back_to_config_button.clicked.connect(self.show_settings)
        self.MenuButton.clicked.connect(self.show_main)
        self.MenuButton_2.clicked.connect(self.show_main)
        self.TrafficConfigurationButton.clicked.connect(self.show_traffic_conf)
        self.reinforcementButton.clicked.connect(self.show_reinforcement_panel)
        self.SaveButton.clicked.connect(self.save_settings)
        self.SaveButton_2.clicked.connect(self.save_settings)
        self.AlgorithmComboBox.currentIndexChanged.connect(self.on_algorithm_changed)

        # Traffic generators:
        self.current_traffic_mode = None
        self.up_peak_button.clicked.connect(self.set_up_peak)
        self.down_peak_button.clicked.connect(self.set_down_peak)
        self.mixed_peak_button.clicked.connect(self.set_mixed_peak)
        self.randomButton.setCheckable(True)
        self.randomButton.clicked.connect(self.serve_random_button)

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

        # TRAFFIC
        match config.traffic.generator_type:
            case TrafficGeneratorEnum('up-peak'):
                self.set_up_peak()
                if config.traffic.up_peak_params.arrival_floor:
                    self.arrval_floor_spin_box.setValue(config.traffic.up_peak_params.arrival_floor)
            case TrafficGeneratorEnum('down-peak'):
                self.set_down_peak()
                if config.traffic.down_peak_params.destination_floor:
                    self.destination_floor_spin_box.setValue(config.traffic.down_peak_params.destination_floor)
            case TrafficGeneratorEnum('mixed-peak'):
                self.set_mixed_peak()
                mixed_params = config.traffic.mixed_peak_params
                if mixed_params.arrival_floor:
                    self.arrival_floor_spin_box_2.setValue(mixed_params.arrival_floor)
                if mixed_params.destination_floor:
                    self.destination_floor_spin_box_2.setValue(mixed_params.destination_floor)
                if mixed_params.up_peak_ratio:
                    self.mixed_up_peak_ratio_spinbox.setValue(mixed_params.up_peak_ratio)
                else:
                    self.mixed_up_peak_ratio_spinbox.setValue(0.4)  # hardcoded, to change
                if mixed_params.down_peak_ratio:
                    self.mixed_down_peak_ratio_spinbox.setValue(mixed_params.down_peak_ratio)
                else:
                    self.mixed_down_peak_ratio_spinbox.setValue(0.4)  # hardcoded, to change
                if mixed_params.interfloor_ratio:
                    self.mixed_interfloor_peak_ratio_spinbox.setValue(mixed_params.interfloor_ratio)
                else:
                    self.mixed_interfloor_peak_ratio_spinbox.setValue(0.4)  # hardcoded, to change

        self.intensitySpinBox.setValue(config.traffic.intensity)
        if config.traffic.seed is None:
            self.randomButton.setChecked(True)
        else:
            self.randomButton.setChecked(False)
            self.seedSpinBox.setValue(config.traffic.seed)

    def on_algorithm_changed(self, index):
        alg = AlgorithmEnum(self.AlgorithmComboBox.itemData(index))
        print(alg)

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

    def set_up_peak(self):
        self.up_peak_button.setChecked(True)
        self.down_peak_button.setChecked(False)
        self.mixed_peak_button.setChecked(False)
        self.current_traffic_mode = TrafficGeneratorEnum('up-peak')
        self.traffic_stacked_widget.setCurrentIndex(0)

    def set_down_peak(self):
        self.up_peak_button.setChecked(False)
        self.down_peak_button.setChecked(True)
        self.mixed_peak_button.setChecked(False)
        self.current_traffic_mode = TrafficGeneratorEnum('down-peak')
        self.traffic_stacked_widget.setCurrentIndex(1)

    def set_mixed_peak(self):
        self.up_peak_button.setChecked(False)
        self.down_peak_button.setChecked(False)
        self.mixed_peak_button.setChecked(True)
        self.current_traffic_mode = TrafficGeneratorEnum('mixed-peak')
        self.traffic_stacked_widget.setCurrentIndex(2)

    def serve_random_button(self):
        if self.randomButton.isChecked():
            self.seedSpinBox.setHidden(True)
        else:
            self.seedSpinBox.setHidden(False)

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

        alg = AlgorithmEnum(self.AlgorithmComboBox.currentData())

        # TRAFFIC
        traffic_mode = self.current_traffic_mode
        intensity = self.intensitySpinBox.value()
        if self.seedSpinBox.isHidden():
            seed = None
        else:
            seed = self.seedSpinBox.value()

        up_peak_params = None
        down_peak_params = None
        mixed_peak_params = None

        match traffic_mode:
            case TrafficGeneratorEnum('up-peak'):
                up_peak_params = UpPeakParams()
                up_peak_params.arrival_floor = self.arrval_floor_spin_box.value()
                if up_peak_params.arrival_floor > self.FloorsSpinBox.value():
                    QMessageBox.warning(self, 'Bad parameters!', "Arrival floor parameter doesn't "
                                                                 "match number of floors")
                    return
            case TrafficGeneratorEnum('down-peak'):
                down_peak_params = DownPeakParams()
                down_peak_params.destination_floor = self.destination_floor_spin_box.value()
                if down_peak_params.destination_floor > self.FloorsSpinBox.value():
                    QMessageBox.warning(self, 'Bad parameters!', "Destination floor parameter doesn't "
                                                                 "match number of floors")
                    return
            case TrafficGeneratorEnum('mixed-peak'):
                mixed_peak_params = MixedPeakParams()
                mixed_peak_params.destination_floor = self.destination_floor_spin_box_2.value()
                mixed_peak_params.arrival_floor = self.arrival_floor_spin_box_2.value()
                mixed_peak_params.up_peak_ratio = self.mixed_up_peak_ratio_spinbox.value()
                mixed_peak_params.down_peak_ratio = self.mixed_down_peak_ratio_spinbox.value()
                mixed_peak_params.interfloor_ratio = self.mixed_interfloor_peak_ratio_spinbox.value()
                try:
                    mixed_peak_params.model_validate(mixed_peak_params)
                except ValueError:
                    QMessageBox.warning(self, 'Bad parameters!', "Wrong ratio! Must equal 1.0")
                    return
        traffic = TrafficConfigSchema(generator_type=traffic_mode,
                                      intensity=intensity,
                                      seed=seed,
                                      up_peak_params=up_peak_params,
                                      down_peak_params=down_peak_params,
                                      mixed_peak_params=mixed_peak_params)

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
                                     model=model,
                                     traffic=traffic)

        save_config(configuration)

        print(f"Zapisano ustawienia: floors={floors}, steps={steps}")
        QMessageBox.information(self, "Saved", "Settings saved successfully.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ElevatorSimConfig()
    window.show()
    sys.exit(app.exec())

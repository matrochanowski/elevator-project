from PySide6.QtWidgets import QSpinBox, QMessageBox

from simulation.schema import ConfigSchema, ElevatorConfigSchema, TrafficConfigSchema
from simulation.config import save_config, load_config
from simulation.enums import AlgorithmEnum, TrafficGeneratorEnum, UpPeakParams, DownPeakParams, MixedPeakParams
from simulation.utils import extract_params_suffix
from simulation.gui.core.table_helpers import setup_elevator_table


class SettingsPage:
    def __init__(self, window):
        self.window = window
        self.window.current_traffic_mode = None
        self.setup_algorithm_combo()
        self.load_settings()

    def connect_buttons(self):
        self.window.SaveButton.clicked.connect(self.save_settings)
        self.window.MenuButton.clicked.connect(self.window.show_main)
        self.window.TrafficConfigurationButton.clicked.connect(self.window.show_traffic_conf)
        self.window.AlgorithmComboBox.currentIndexChanged.connect(self.on_algorithm_changed)
        self.window.ModelComboBox.currentIndexChanged.connect(self.on_model_changed)
        self.window.ElevatorsSpinBox.valueChanged.connect(self.on_num_elevators_changed)

    def setup_algorithm_combo(self):
        for alg in AlgorithmEnum:
            self.window.AlgorithmComboBox.addItem(alg.pretty, userData=alg)

    def load_settings(self):
        config = load_config()
        w = self.window

        w.FloorsSpinBox.setValue(config.floors)
        w.StepsHorizontalSlider.setValue(config.steps)
        w.MaxPeopleFloorSpinBox.setValue(config.max_people_floor)
        w.VisualisationRadioButton.setChecked(config.visualisation)

        idx = w.AlgorithmComboBox.findData(config.algorithm)
        if idx != -1:
            w.AlgorithmComboBox.setCurrentIndex(idx)

        idx = w.ModelComboBox.findData(config.model)
        if idx != -1:
            w.ModelComboBox.setCurrentIndex(idx)

        self.on_num_elevators_changed(len(config.elevators))
        for row, elevator in enumerate(config.elevators):
            w.ElevatorTable.cellWidget(row, 0).setValue(elevator.max_people)
            w.ElevatorTable.cellWidget(row, 1).setValue(elevator.speed)
            w.ElevatorTable.cellWidget(row, 2).setValue(elevator.starting_floor)

    def on_algorithm_changed(self, index):
        alg = AlgorithmEnum(self.window.AlgorithmComboBox.itemData(index))
        w = self.window

        if alg.needs_model:
            w.ModelComboBox.clear()
            for model in alg.list_models():
                w.ModelComboBox.addItem(model, model)
            w.ModelComboBox.setEnabled(True)
            for i in range(7, 12):
                getattr(w, f"label_{i}").setHidden(False)
        else:
            w.ModelComboBox.clear()
            w.ModelComboBox.setEnabled(False)
            for i in range(7, 12):
                getattr(w, f"label_{i}").setHidden(True)

    def on_model_changed(self, index):
        model_name = self.window.ModelComboBox.itemData(index)
        if not model_name:
            return
        n_elevators, n_floors = extract_params_suffix(model_name)
        self.window.FloorsSpinBox.setValue(n_floors)
        self.window.ElevatorsSpinBox.setValue(n_elevators)
        self.window.label_10.setText(str(n_floors))
        self.window.label_11.setText(str(n_elevators))

    def on_num_elevators_changed(self, value):
        setup_elevator_table(self.window.ElevatorTable, value)

    def save_settings(self):
        w = self.window
        floors = w.FloorsSpinBox.value()
        steps = w.StepsHorizontalSlider.value()
        max_people_floor = w.MaxPeopleFloorSpinBox.value()
        visualisation = w.VisualisationRadioButton.isChecked()
        algorithm = w.AlgorithmComboBox.currentData()
        model = w.ModelComboBox.currentData()

        elevators = []
        for row in range(w.ElevatorTable.rowCount()):
            elevators.append(ElevatorConfigSchema(
                max_people=w.ElevatorTable.cellWidget(row, 0).value(),
                speed=w.ElevatorTable.cellWidget(row, 1).value(),
                starting_floor=w.ElevatorTable.cellWidget(row, 2).value()
            ))

        configuration = ConfigSchema(
            floors=floors,
            steps=steps,
            max_people_floor=max_people_floor,
            visualisation=visualisation,
            elevators=elevators,
            algorithm=algorithm,
            model=model,
            traffic=None  # Zostaje w traffic_page
        )
        save_config(configuration)
        QMessageBox.information(w, "Saved", "Settings saved successfully.")

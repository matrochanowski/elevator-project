from PySide6.QtWidgets import QMessageBox
import os
from pathlib import Path

from simulation.schema import ConfigSchema, ElevatorConfigSchema, TrafficConfigSchema
from simulation.config import save_config, load_config
from simulation.enums import AlgorithmEnum, TrafficGeneratorEnum, UpPeakParams, DownPeakParams, MixedPeakParams, \
    FromFileParams
from simulation.utils import extract_params_suffix
from simulation.engine.traffic_generator import generate_scenario_apriori

from simulation.gui.core.table_helpers import setup_elevator_table
from simulation.gui.dialogs.scenario_name_dialog import ScenarioNameDialog

REPO_DIR = Path(__file__).resolve().parents[3]
SCENARIO_DIR = REPO_DIR / "database" / "scenarios"


class ConfigPage:
    def __init__(self, window):
        self.window = window
        self.current_traffic_mode = None
        self._setup_algorithm_combo()
        self._connect_traffic_buttons()
        self._connect_elevator_logic()
        self.load_settings()
        self.setup_scenario_combobox()

    # --- PUBLIC API ---
    def connect_buttons(self):
        w = self.window
        # Settings page
        w.SaveButton.clicked.connect(self.save_settings)
        w.MenuButton.clicked.connect(w.show_main)
        w.TrafficConfigurationButton.clicked.connect(w.show_traffic_conf)
        w.saveTrafficScenarioButton.clicked.connect(self.open_scenario_dialog)

        # Traffic page
        w.SaveButton_2.clicked.connect(self.save_settings)
        w.MenuButton_2.clicked.connect(w.show_main)
        w.back_to_config_button.clicked.connect(w.show_settings)

        self.window.StepsHorizontalSlider.sliderMoved.connect(self.on_steps_changed)
        self.window.StepsHorizontalSlider.valueChanged.connect(self.on_steps_changed)

    # --- INITIALIZATION ---
    def _setup_algorithm_combo(self):
        for alg in AlgorithmEnum:
            self.window.AlgorithmComboBox.addItem(alg.pretty, userData=alg)

    def _connect_elevator_logic(self):
        w = self.window
        w.AlgorithmComboBox.currentIndexChanged.connect(self.on_algorithm_changed)
        w.ModelComboBox.currentIndexChanged.connect(self.on_model_changed)
        w.ElevatorsSpinBox.valueChanged.connect(self.on_num_elevators_changed)

    def _connect_traffic_buttons(self):
        w = self.window
        w.up_peak_button.clicked.connect(self.set_up_peak)
        w.down_peak_button.clicked.connect(self.set_down_peak)
        w.mixed_peak_button.clicked.connect(self.set_mixed_peak)
        w.from_file_button.clicked.connect(self.set_from_file)
        w.randomButton.clicked.connect(self.toggle_seed_visibility)

    # --- SETTINGS LOGIC ---
    def load_settings(self):
        config = load_config()
        w = self.window

        w.FloorsSpinBox.setValue(config.floors)
        w.ElevatorsSpinBox.setValue(len(config.elevators))
        w.StepsHorizontalSlider.setValue(config.steps)
        w.StepsHorizontalSlider.setSingleStep(1000)
        w.StepsHorizontalSlider.setPageStep(1000)
        w.stepCount.setText(str(config.steps))
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

        # Load traffic config
        match config.traffic.generator_type:
            case TrafficGeneratorEnum("up-peak"):
                self.set_up_peak()
                w.arrval_floor_spin_box.setValue(config.traffic.up_peak_params.arrival_floor)
            case TrafficGeneratorEnum("down-peak"):
                self.set_down_peak()
                w.destination_floor_spin_box.setValue(config.traffic.down_peak_params.destination_floor)
            case TrafficGeneratorEnum("mixed-peak"):
                self.set_mixed_peak()
                p = config.traffic.mixed_peak_params
                w.arrival_floor_spin_box_2.setValue(p.arrival_floor)
                w.destination_floor_spin_box_2.setValue(p.destination_floor)
                w.mixed_up_peak_ratio_spinbox.setValue(p.up_peak_ratio)
                w.mixed_down_peak_ratio_spinbox.setValue(p.down_peak_ratio)
                w.mixed_interfloor_peak_ratio_spinbox.setValue(p.interfloor_ratio)
            case TrafficGeneratorEnum("from file"):
                self.set_from_file()

        w.intensitySpinBox.setValue(config.traffic.intensity)
        if config.traffic.seed is None:
            w.randomButton.setChecked(True)
            w.seedSpinBox.setHidden(True)
        else:
            w.randomButton.setChecked(False)
            w.seedSpinBox.setHidden(False)
            w.seedSpinBox.setValue(config.traffic.seed)

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

    def on_steps_changed(self, value):
        value = (value // 1000) * 1000
        self.window.StepsHorizontalSlider.setValue(value)
        self.window.stepCount.setText(str(self.window.StepsHorizontalSlider.value()))

    # --- TRAFFIC LOGIC ---
    def toggle_seed_visibility(self):
        self.window.seedSpinBox.setHidden(self.window.randomButton.isChecked())

    def set_up_peak(self):
        self._set_mode(TrafficGeneratorEnum("up-peak"), 0)
        self.window.up_peak_button.setChecked(True)

    def set_down_peak(self):
        self._set_mode(TrafficGeneratorEnum("down-peak"), 1)
        self.window.down_peak_button.setChecked(True)

    def set_mixed_peak(self):
        self._set_mode(TrafficGeneratorEnum("mixed-peak"), 2)
        self.window.mixed_peak_button.setChecked(True)

    def set_from_file(self):
        self._set_mode(TrafficGeneratorEnum("from file"), 3)
        self.window.from_file_button.setChecked(True)

    def _set_mode(self, mode, index):
        self.current_traffic_mode = mode
        self.window.traffic_stacked_widget.setCurrentIndex(index)

    def setup_scenario_combobox(self):
        self.window.scenarioFileComboBox.clear()

        if not os.path.exists(SCENARIO_DIR):
            raise FileExistsError(f"Directory {SCENARIO_DIR} doesn't exist!")

        scenario_files = []
        for file in os.listdir(SCENARIO_DIR):
            scenario_files.append(file)

        scenario_files.sort()
        self.window.scenarioFileComboBox.addItems(scenario_files)

        config = load_config()
        if config.traffic.from_file_params:
            if config.traffic.from_file_params.filename:
                # set filename as "selected" in combobox
                saved_filename = config.traffic.from_file_params.filename
                index = self.window.scenarioFileComboBox.findText(saved_filename)
                if index >= 0:
                    self.window.scenarioFileComboBox.setCurrentIndex(index)
                else:
                    if scenario_files:
                        self.window.scenarioFileComboBox.setCurrentIndex(0)
            else:
                if scenario_files:
                    self.window.scenarioFileComboBox.setCurrentIndex(0)

    def open_scenario_dialog(self):
        self.save_settings()
        dialog = ScenarioNameDialog(parent=self.window)
        scenario_name = dialog.get_scenario_name()

        if scenario_name:
            full_filename = dialog.get_full_filename()
            generate_scenario_apriori(scenario_name=full_filename, n_steps=self.window.StepsHorizontalSlider.value())
            QMessageBox.information(self.window, "Saved", f"Scenario {scenario_name} saved successfully.")
            self.setup_scenario_combobox()

    # --- SAVE SETTINGS ---
    def save_settings(self):
        w = self.window
        floors = w.FloorsSpinBox.value()
        steps = w.StepsHorizontalSlider.value()
        max_people_floor = w.MaxPeopleFloorSpinBox.value()
        visualisation = w.VisualisationRadioButton.isChecked()
        algorithm = w.AlgorithmComboBox.currentData()
        model = w.ModelComboBox.currentData()
        alg = AlgorithmEnum(algorithm)

        # TRAFFIC
        traffic_mode = self.current_traffic_mode
        intensity = w.intensitySpinBox.value()
        seed = None if w.seedSpinBox.isHidden() else w.seedSpinBox.value()

        up_peak_params = down_peak_params = mixed_peak_params = from_file_params = None
        if traffic_mode == TrafficGeneratorEnum("up-peak"):
            up_peak_params = UpPeakParams(arrival_floor=w.arrval_floor_spin_box.value())
            if up_peak_params.arrival_floor > floors:
                QMessageBox.warning(w, "Bad parameters!", "Arrival floor exceeds number of floors.")
                return
        elif traffic_mode == TrafficGeneratorEnum("down-peak"):
            down_peak_params = DownPeakParams(destination_floor=w.destination_floor_spin_box.value())
            if down_peak_params.destination_floor > floors:
                QMessageBox.warning(w, "Bad parameters!", "Destination floor exceeds number of floors.")
                return
        elif traffic_mode == TrafficGeneratorEnum("mixed-peak"):
            mixed_peak_params = MixedPeakParams(
                arrival_floor=w.arrival_floor_spin_box_2.value(),
                destination_floor=w.destination_floor_spin_box_2.value(),
                up_peak_ratio=w.mixed_up_peak_ratio_spinbox.value(),
                down_peak_ratio=w.mixed_down_peak_ratio_spinbox.value(),
                interfloor_ratio=w.mixed_interfloor_peak_ratio_spinbox.value(),
            )
            try:
                mixed_peak_params.model_validate(mixed_peak_params)
            except ValueError:
                QMessageBox.warning(w, "Bad parameters!", "Sum of ratios must equal 1.0")
                return
        elif traffic_mode == TrafficGeneratorEnum("from file"):
            from_file_params = FromFileParams(
                filename=w.scenarioFileComboBox.currentText()
            )

        traffic = TrafficConfigSchema(
            generator_type=traffic_mode,
            intensity=intensity,
            seed=seed,
            up_peak_params=up_peak_params,
            down_peak_params=down_peak_params,
            mixed_peak_params=mixed_peak_params,
            from_file_params=from_file_params
        )

        # ELEVATORS
        elevators = []
        for row in range(w.ElevatorTable.rowCount()):
            elevators.append(ElevatorConfigSchema(
                max_people=w.ElevatorTable.cellWidget(row, 0).value(),
                speed=w.ElevatorTable.cellWidget(row, 1).value(),
                starting_floor=w.ElevatorTable.cellWidget(row, 2).value()
            ))

        # VALIDATION
        if alg.needs_model:
            n_elevators, n_floors = extract_params_suffix(model)
            if (n_elevators, n_floors) != (w.ElevatorTable.rowCount(), floors):
                QMessageBox.warning(
                    w,
                    "Wrong configuration!",
                    "Number of elevators/floors doesn't match model parameters."
                )
                return

        configuration = ConfigSchema(
            floors=floors,
            steps=steps,
            max_people_floor=max_people_floor,
            visualisation=visualisation,
            elevators=elevators,
            algorithm=algorithm,
            model=model,
            traffic=traffic
        )

        save_config(configuration)
        QMessageBox.information(w, "Saved", "Settings saved successfully.")

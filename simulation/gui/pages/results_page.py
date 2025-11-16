from pathlib import Path
import os

from pprint import pformat

from typing import TYPE_CHECKING

from simulation.analysis.result_analyse import analyse_from_file
from simulation.analysis.schema import ResultsInfoForGui

from simulation.gui.dialogs.rename_file_dialog import RenameFileDialog
from simulation.gui.dialogs.show_text_dialog import ShowTextDialog

SIMULATION_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = SIMULATION_DIR / "logs"

if TYPE_CHECKING:
    from simulation.gui.core.window_controller import ElevatorSimWindowController


class ResultsPage:
    def __init__(self, window: "ElevatorSimWindowController"):
        self.window = window
        self.populate_files()

    def connect_buttons(self):
        w = self.window
        self.window.backButton.clicked.connect(w.show_main)
        w.acceptFilenameButton.clicked.connect(self.load_simulation_info_results)
        w.reloadFilesPushButton.clicked.connect(self.populate_files)
        w.changeNamePushButton.clicked.connect(self.on_rename_clicked)
        w.advancedAnalysis.clicked.connect(self.show_config)

    def load_simulation_info_results(self):
        w = self.window
        filename = w.resultsFileComboBox.currentText()
        ri: ResultsInfoForGui = analyse_from_file(filename)

        w.numberOfStepsAnalysis.setText(str(ri.info.steps))
        w.algorithmAnalysis.setText(ri.info.algorithm.pretty)
        w.seedAnalysis.setText(str(ri.info.traffic.seed))
        w.generatorAnalysis.setText(str(ri.info.traffic.generator_type.value))
        w.elevatorsAnalysis.setText(str(len(ri.info.elevators)))
        w.floorsAnalysis.setText(str(ri.info.floors))

        w.journeyTime.setText(str(round(ri.results.mean_journey_time, 3)))
        w.waitingTime.setText(str(round(ri.results.mean_waiting_time, 3)))
        w.travelTime.setText(str(round(ri.results.mean_travel_time, 3)))
        w.wTime.setText(str(round(ri.results.mean_j_time_dist, 3)))
        w.nPassengers.setText(str(ri.results.n_passengers))

    def populate_files(self):
        log_dir = LOG_DIR

        files = [f for f in log_dir.iterdir() if f.is_file()]

        if not files:
            return

        files_sorted = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)

        file_names = [f.name for f in files_sorted]

        combo = self.window.resultsFileComboBox
        combo.clear()
        combo.addItems(file_names)

        combo.setCurrentIndex(0)

    def on_rename_clicked(self):
        cb = self.window.resultsFileComboBox

        old_name = cb.currentText()
        if not old_name:
            return

        # Otwieramy dialog
        dlg = RenameFileDialog(old_name, parent=self.window)
        new_name = dlg.get_new_name()

        if new_name is None:
            return

        old_path = os.path.join(LOG_DIR, old_name)
        new_path = os.path.join(LOG_DIR, new_name)

        try:
            os.rename(old_path, new_path)
        except Exception as e:
            print(f"Rename error: {e}")
            return

        idx = cb.currentIndex()
        cb.setItemText(idx, new_name)

    def show_config(self):
        w = self.window
        filename = w.resultsFileComboBox.currentText()
        ri: ResultsInfoForGui = analyse_from_file(filename)

        text = ri.info.model_dump()

        text = pformat(text, width=80, indent=4)

        dlg = ShowTextDialog(text, parent=self.window)
        dlg.exec()

        self.load_simulation_info_results()

from simulation.enums import TrafficGeneratorEnum


class TrafficPage:
    def __init__(self, window):
        self.window = window
        self.current_traffic_mode = None

    def connect_buttons(self):
        w = self.window
        w.up_peak_button.clicked.connect(self.set_up_peak)
        w.down_peak_button.clicked.connect(self.set_down_peak)
        w.mixed_peak_button.clicked.connect(self.set_mixed_peak)
        w.MenuButton_2.clicked.connect(w.show_main)
        w.SaveButton_2.clicked.connect(lambda: None)
        w.back_to_config_button.clicked.connect(w.show_settings)
        w.randomButton.clicked.connect(self.toggle_seed_visibility)

    def toggle_seed_visibility(self):
        w = self.window
        w.seedSpinBox.setHidden(w.randomButton.isChecked())

    def set_up_peak(self):
        self._set_mode(TrafficGeneratorEnum("up-peak"), 0)

    def set_down_peak(self):
        self._set_mode(TrafficGeneratorEnum("down-peak"), 1)

    def set_mixed_peak(self):
        self._set_mode(TrafficGeneratorEnum("mixed-peak"), 2)

    def _set_mode(self, mode, index):
        self.current_traffic_mode = mode
        self.window.traffic_stacked_widget.setCurrentIndex(index)

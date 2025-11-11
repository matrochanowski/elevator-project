class ReinforcementPage:
    def __init__(self, window):
        self.window = window

    def connect_buttons(self):
        self.window.settingsButton_2.clicked.connect(self.window.show_settings)

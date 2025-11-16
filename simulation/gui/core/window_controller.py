from PySide6.QtWidgets import QMainWindow
from simulation.gui.ui_config import Ui_MainWindow

from simulation.gui.pages.main_menu_page import MainMenuPage
from simulation.gui.pages.config_page import ConfigPage
from simulation.gui.pages.reinforcement_page import ReinforcementPage
from simulation.gui.pages.results_page import ResultsPage


class ElevatorSimWindowController(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # subpages init
        self.main_menu = MainMenuPage(self)
        self.config_page = ConfigPage(self)  # settings + traffic
        self.reinforcement_page = ReinforcementPage(self)
        self.results_page = ResultsPage(self)

        # buttons connection
        self.main_menu.connect_buttons()
        self.config_page.connect_buttons()
        self.reinforcement_page.connect_buttons()
        self.results_page.connect_buttons()

        # start page
        self.show_main()

    # Routing
    def show_main(self):
        self.stackedWidget.setCurrentIndex(0)

    def show_settings(self):
        self.stackedWidget.setCurrentIndex(1)

    def show_traffic_conf(self):
        self.stackedWidget.setCurrentIndex(2)

    def show_reinforcement_panel(self):
        self.stackedWidget.setCurrentIndex(3)

    def show_analyse_panel(self):
        self.stackedWidget.setCurrentIndex(4)

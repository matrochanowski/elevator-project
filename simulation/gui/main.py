import sys
from PySide6.QtWidgets import QApplication
from simulation.gui.core.window_controller import ElevatorSimWindowController


def execute():
    app = QApplication(sys.argv)
    window = ElevatorSimWindowController()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    execute()

import sys
from PySide6.QtWidgets import QApplication
from core.window_controller import ElevatorSimWindowController


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ElevatorSimWindowController()
    window.show()
    sys.exit(app.exec())

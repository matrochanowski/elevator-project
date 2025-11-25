from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QLabel, QPushButton, QDialogButtonBox)
import os
from pathlib import Path

SIMULATION_DIR = Path(__file__).resolve().parents[2]
SCENARIO_DIR = SIMULATION_DIR / "engine" / "scenarios"


class ScenarioNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate New Scenario")
        self.resize(400, 150)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Label and input field with .csv suffix
        input_layout = QHBoxLayout()

        self.filename_label = QLabel("Scenario name:")
        input_layout.addWidget(self.filename_label)

        self.name_edit = QLineEdit(self)
        self.name_edit.setPlaceholderText("Enter scenario name")
        input_layout.addWidget(self.name_edit)

        self.extension_label = QLabel(".csv")
        input_layout.addWidget(self.extension_label)

        layout.addLayout(input_layout)

        # Add some spacing
        layout.addSpacing(20)

        # Generate and Cancel buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok,
            parent=self
        )
        self.button_box.button(QDialogButtonBox.Ok).setText("Generate")

        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)

        # Connect text change signal to update validation
        self.name_edit.textChanged.connect(self.validate_input)

    def validate_input(self):
        """Enable/disable Generate button based on input validity"""
        text = self.name_edit.text().strip()
        is_valid = bool(text) and not any(c in text for c in '/\\:*?"<>|')
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(is_valid)

    def validate_and_accept(self):
        """Validate filename and accept dialog if valid"""
        filename = self.get_full_filename()

        # Check for invalid characters
        invalid_chars = '/\\:*?"<>|'
        if any(char in filename for char in invalid_chars):
            return

        # Check if file already exists (optional warning)
        if os.path.exists(os.path.join(SCENARIO_DIR, filename)):
            # You might want to show a warning here
            print(f"Warning: File {filename} already exists")

        self.accept()

    def get_scenario_name(self) -> str | None:
        """Returns the scenario name without extension if dialog was accepted"""
        if self.exec() == QDialog.Accepted:
            return self.name_edit.text().strip()
        return None

    def get_full_filename(self) -> str:
        """Returns the complete filename with .csv extension"""
        name = self.name_edit.text().strip()
        if name.endswith('.csv'):
            return name
        return f"{name}.csv"
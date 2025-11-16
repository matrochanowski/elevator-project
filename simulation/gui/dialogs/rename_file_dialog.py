from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox


class RenameFileDialog(QDialog):
    def __init__(self, initial_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rename File")
        self.resize(400, 100)

        layout = QVBoxLayout(self)

        self.edit = QLineEdit(self)
        self.edit.setText(initial_name)
        layout.addWidget(self.edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel,
            parent=self
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_new_name(self) -> str | None:
        if self.exec() == QDialog.Accepted:
            return self.edit.text().strip()
        return None

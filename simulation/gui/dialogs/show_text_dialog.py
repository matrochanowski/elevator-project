from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox

class ShowTextDialog(QDialog):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Show Text")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(text)
        layout.addWidget(self.text_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok, parent=self)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def exec_and_get_text(self) -> str:
        self.exec()
        return self.text_edit.toPlainText()

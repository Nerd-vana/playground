import sys
import re
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QListWidget, QPushButton, QLineEdit)
import pyperclip

class TextReplaceApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Text Replace App')

        layout = QHBoxLayout()

        self.text_area = QTextEdit(self)
        self.text_area.setPlaceholderText("Enter text here...")
        layout.addWidget(self.text_area)

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        right_layout = QVBoxLayout()

        self.string_input = QLineEdit(self)
        self.string_input.setPlaceholderText("Enter string to search and press Enter")
        self.string_input.returnPressed.connect(self.add_string)
        right_layout.addWidget(self.string_input)

        self.replace_button = QPushButton("Replace & Copy", self)
        self.replace_button.clicked.connect(self.replace_text)
        right_layout.addWidget(self.replace_button)

        self.restore_button = QPushButton("Restore Text", self)
        self.restore_button.clicked.connect(self.restore_text)
        right_layout.addWidget(self.restore_button)

        layout.addLayout(right_layout)
        self.setLayout(layout)

    def add_string(self):
        text = self.string_input.text()
        if text:
            self.list_widget.addItem(text)
            self.string_input.clear()

    def is_name(self, text):
        return text.isalpha()

    def obfuscate_name(self, name):
        # Use a random name for obfuscation, maintaining the length
        sample_names = ["Alice", "Bob", "Charlie", "David", "Eva"]
        new_name = random.choice(sample_names)
        if len(name) > 4:
            new_name = new_name[:len(name)]
        return new_name + "xxx" if len(name) > 4 else new_name

    def obfuscate_number(self, number):
        # Mask the entire number
        return "*" * len(number)

    def obfuscate(self, text):
        if self.is_name(text):
            return self.obfuscate_name(text)
        elif text.isdigit():
            return self.obfuscate_number(text)
        return text

    def replace_text(self):
        original_text = self.text_area.toPlainText()
        items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        self.replacements = {}

        for item in items:
            obfuscated_text = self.obfuscate(item)
            self.replacements[obfuscated_text] = item
            original_text = original_text.replace(item, obfuscated_text)

        self.text_area.setPlainText(original_text)
        pyperclip.copy(original_text)

    def restore_text(self):
        clipboard_text = pyperclip.paste()
        for obfuscated_text, original in self.replacements.items():
            clipboard_text = clipboard_text.replace(obfuscated_text, original)
        
        self.text_area.setPlainText(clipboard_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TextReplaceApp()
    ex.show()
    sys.exit(app.exec_())

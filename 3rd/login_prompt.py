from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QFormLayout, QCheckBox


class LoginPrompt(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Login")
        self.resize(300, 200)

        # Поля ввода имени и комнаты
        self.username_field = QLineEdit(self)
        self.username_field.setPlaceholderText("Enter your name")

        self.room_field = QLineEdit(self)
        self.room_field.setPlaceholderText("Enter room name")

        # Checkbox для приватной комнаты
        self.private_checkbox = QCheckBox("Private Room", self)

        # Кнопка подтверждения
        self.confirm_btn = QPushButton("Connect")
        self.confirm_btn.clicked.connect(self.accept)

        # Компоновка элементов
        layout = QFormLayout()
        layout.addRow("Name:", self.username_field)
        layout.addRow("Room:", self.room_field)
        layout.addRow(self.private_checkbox)
        layout.addWidget(self.confirm_btn)
        self.setLayout(layout)

    def collect_inputs(self):
        """
        Возвращает имя пользователя, имя комнаты и обрабатывает выбор приватной комнаты.
        """
        username = self.username_field.text().strip()
        room = self.room_field.text().strip()
        if self.private_checkbox.isChecked() and not room.startswith("private_"):
            room = f"private_{room}"
        return username, room


# Пример использования
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    dialog = LoginPrompt()
    if dialog.exec_():
        username, room = dialog.collect_inputs()
        print(f"Username: {username}, Room: {room}")
    sys.exit(app.exec_())

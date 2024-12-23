from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFileDialog, QInputDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import pyqtSignal
import os

class ChatInterface(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Chat - Room: {self.client.chatroom}")
        self.resize(600, 400)

        self.message_area = QTextEdit(self)
        self.message_area.setReadOnly(True)

        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("Enter your message...")
        self.input_box.returnPressed.connect(self.send_text)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_text)

        self.upload_btn = QPushButton("Upload File")
        self.upload_btn.clicked.connect(self.upload_file)

        self.switch_room_btn = QPushButton("Switch Room")
        self.switch_room_btn.clicked.connect(self.switch_room)

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.message_area)
        layout.addWidget(self.input_box)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.send_btn)
        button_layout.addWidget(self.upload_btn)
        button_layout.addWidget(self.switch_room_btn)
        button_layout.addWidget(self.exit_btn)

        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.client.new_message.connect(self.show_message)
        self.client.file_received.connect(self.store_file)
        self.client.disconnected.connect(self.on_disconnect)

    def show_message(self, message):
        self.message_area.append(message)

    def send_text(self):
        text = self.input_box.text().strip()
        if text:
            self.client.send_text(text)
            self.message_area.append(f"You: {text}")  # Отображаем отправленное сообщение
            self.input_box.clear()

    def upload_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Choose File")
        if filepath:
            self.client.upload_file(filepath)
            self.message_area.append(f"[INFO] File sent: {os.path.basename(filepath)}")

    def store_file(self, filename, filedata):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", filename)
        if save_path:
            with open(save_path, "wb") as file:
                file.write(filedata)
            self.message_area.append(f"[INFO] File saved to: {save_path}")

    def switch_room(self):
        new_room, ok = QInputDialog.getText(self, "Switch Room", "Enter new room name:")
        if ok and new_room.strip():
            self.client.change_chatroom(new_room.strip())
            self.message_area.append(f"[INFO] Switched to room: {new_room.strip()}")

    def on_disconnect(self):
        QMessageBox.warning(self, "Disconnected", "Lost connection to the server.")
        self.close()

    def closeEvent(self, event):
        self.client.close_connection()
        event.accept()

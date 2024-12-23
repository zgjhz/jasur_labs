import socket
from threading import Thread
from PyQt5.QtCore import QObject, pyqtSignal
import os
from PyQt5.QtWidgets import QMessageBox


class ChatClient(QObject):
    new_message = pyqtSignal(str)
    file_received = pyqtSignal(str, bytes)
    disconnected = pyqtSignal()

    def __init__(self, server_ip, server_port, username, chatroom):
        super().__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.username = username
        self.chatroom = chatroom
        self.connection = None

    def establish_connection(self):
        try:
            self.connection = socket.socket()
            self.connection.connect((self.server_ip, self.server_port))
            self.change_chatroom(self.chatroom)
            Thread(target=self.receive_data, daemon=True).start()
        except Exception as error:
            QMessageBox.critical(None, "Connection Issue", f"Unable to connect to the server: {error}")
            self.disconnected.emit()

    def receive_data(self):
        try:
            while True:
                received = self.connection.recv(1024).decode()
                if not received:
                    break
                if received.startswith("/file"):
                    filename = received.split(" ", 1)[-1].strip()
                    data = b""
                    while True:
                        chunk = self.connection.recv(1024)
                        if chunk.endswith(b"<EOF>"):
                            data += chunk[:-5]
                            break
                        data += chunk
                    self.file_received.emit(filename, data)
                else:
                    self.new_message.emit(received)
        except Exception as err:
            print(f"[ERROR] {err}")
        finally:
            self.disconnected.emit()

    def change_chatroom(self, chatroom):
        try:
            self.chatroom = chatroom
            self.connection.send(f"/join {chatroom}\n".encode())
        except Exception as error:
            QMessageBox.critical(None, "Error", f"Unable to switch chatroom: {error}")

    def send_text(self, text):
        try:
            full_message = f"{self.username}: {text}"
            self.connection.send(full_message.encode())
        except Exception as err:
            print(f"[ERROR] Message sending failed: {err}")

    def upload_file(self, filepath):
        try:
            filename = os.path.basename(filepath)
            self.connection.send(f"/sendfile {filename}\n".encode())
            with open(filepath, "rb") as file:
                while chunk := file.read(1024):
                    self.connection.send(chunk)
            self.connection.send(b"<EOF>")
        except Exception as err:
            QMessageBox.critical(None, "Error", f"File upload failed: {err}")

    def close_connection(self):
        if self.connection:
            self.connection.close()

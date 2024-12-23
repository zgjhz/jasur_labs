import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog
from chat_client import ChatClient
from chat_interface import ChatInterface
from login_prompt import LoginPrompt


def run_chat_client():
    app = QApplication(sys.argv)

    login_prompt = LoginPrompt()
    if login_prompt.exec() == QDialog.Accepted:
        username, chatroom = login_prompt.collect_inputs()
        if not username or not chatroom:
            QMessageBox.critical(None, "Error", "Name and room are required!")
            sys.exit()

        server_ip = "127.0.0.1"
        server_port = 5002
        client = ChatClient(server_ip, server_port, username, chatroom)
        chat_interface = ChatInterface(client)

        client.establish_connection()
        chat_interface.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    run_chat_client()

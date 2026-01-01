from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from app.ui.styles import BUTTON_STYLE, INPUT_STYLE, LABEL_STYLE, MAIN_STYLE
from app.ui.main_window import MainWindow


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")
        self.setFixedSize(300, 450)
        self.setStyleSheet(MAIN_STYLE)

        layout = QVBoxLayout()

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Login")

        self.login_button.setStyleSheet(BUTTON_STYLE)
        self.username_input.setStyleSheet(INPUT_STYLE)
        self.password_input.setStyleSheet(INPUT_STYLE)
        self.username_label.setStyleSheet(LABEL_STYLE)
        self.password_label.setStyleSheet(LABEL_STYLE)

        self.login_button.clicked.connect(self.handle_login)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        # логика аутификации
        
        print(f"Attempting login with Username: {username} and Password: {password}")

        # Если аутентификация успешна, открыть главное окно
        self.close()
        self.main_window = MainWindow()
        self.main_window.show()
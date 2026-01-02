from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from app.ui.styles import BUTTON_STYLE, INPUT_STYLE, LABEL_STYLE, MAIN_STYLE
from app.ui.main_window import MainWindow
from app.logic.auth_service import AuthService


class LoginWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        # Инициализируем сервис аутентификации, передавая ему менеджер БД
        self.auth_service = AuthService(self.db_manager)

        self.setWindowTitle("Login")
        self.setFixedSize(300, 450)
        self.setStyleSheet(MAIN_STYLE)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter) # Центрируем элементы

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        
        self.login_button = QPushButton("Login")

        # Применяем стили
        self.login_button.setStyleSheet(BUTTON_STYLE)
        self.username_input.setStyleSheet(INPUT_STYLE)
        self.password_input.setStyleSheet(INPUT_STYLE)
        self.username_label.setStyleSheet(LABEL_STYLE)
        self.password_label.setStyleSheet(LABEL_STYLE)

        self.login_button.clicked.connect(self.handle_login)
        # Позволяем входить по нажатию Enter в поле пароля
        self.password_input.returnPressed.connect(self.handle_login)

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
        
        # Пытаемся аутентифицировать пользователя через сервис
        user = self.auth_service.authenticate(username, password)
        
        if user:
            print(f"Login successful: {user['username']} (Role: {'Admin' if user['is_admin'] else 'User'})")
            
            # Закрываем окно логина
            self.close()
            
            # Открываем главное окно, передавая данные пользователя и БД
            self.main_window = MainWindow(user, self.db_manager)
            self.main_window.show()
        else:
            # Показываем ошибку, если логин/пароль неверны
            QMessageBox.warning(self, "Login Failed", "Неверное имя пользователя или пароль.")
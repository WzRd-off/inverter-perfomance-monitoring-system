from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox, QDialog)
from PyQt6.QtCore import Qt
from app.ui.styles import BUTTON_STYLE, INPUT_STYLE, LABEL_STYLE
from app.logic.auth_service import AuthService

class ProfileView(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data # Текущий юзер (из session)
        self.auth_service = AuthService(db_manager)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel("Профіль користувача")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(header)

        # Контейнер для формы (белая карточка)
        card = QFrame()
        card.setStyleSheet("background-color: white; border-radius: 10px; padding: 20px;")
        form_layout = QVBoxLayout(card)

        # Роль (Read-only)
        role = "Адміністратор" if self.user_data['is_admin'] else "Користувач"
        self.lbl_role = QLabel(f"Роль у системі: {role}")
        self.lbl_role.setStyleSheet("color: #7f8c8d; font-weight: bold; margin-bottom: 10px;")
        form_layout.addWidget(self.lbl_role)

        # Логин (Read-only)
        form_layout.addWidget(QLabel("Логін:"))
        self.inp_username = QLineEdit(self.user_data['username'])
        self.inp_username.setStyleSheet(INPUT_STYLE)
        self.inp_username.setReadOnly(True)
        form_layout.addWidget(self.inp_username)

        # ФИО
        form_layout.addWidget(QLabel("ПІБ:"))
        self.inp_fullname = QLineEdit(self.user_data.get('full_name', ''))
        self.inp_fullname.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(self.inp_fullname)

        # Email
        form_layout.addWidget(QLabel("Email:"))
        self.inp_email = QLineEdit(self.user_data.get('email', ''))
        self.inp_email.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(self.inp_email)

        # Телефон
        form_layout.addWidget(QLabel("Телефон:"))
        self.inp_phone = QLineEdit(self.user_data.get('phone', ''))
        self.inp_phone.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(self.inp_phone)

        # Кнопки действий
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("Зберегти зміни")
        self.btn_save.setStyleSheet(BUTTON_STYLE)
        self.btn_save.clicked.connect(self.save_changes)
        
        self.btn_pass = QPushButton("Змінити пароль")
        self.btn_pass.setStyleSheet("background-color: #f39c12; color: white; border-radius: 5px; padding: 8px;")
        self.btn_pass.clicked.connect(self.open_password_dialog)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_pass)
        btn_layout.addStretch()
        
        form_layout.addLayout(btn_layout)
        
        layout.addWidget(card)
        layout.addStretch()
        
        self.setLayout(layout)

    def save_changes(self):
        full_name = self.inp_fullname.text()
        email = self.inp_email.text()
        phone = self.inp_phone.text()
        
        self.db_manager.update_user_profile(self.user_data['id'], full_name, email, phone)
        
        # Обновляем локальные данные
        self.user_data['full_name'] = full_name
        self.user_data['email'] = email
        self.user_data['phone'] = phone
        
        QMessageBox.information(self, "Успіх", "Дані профілю оновлено.")

    def open_password_dialog(self):
        dialog = ChangePasswordDialog(self.db_manager, self.user_data['id'], self.auth_service, self)
        dialog.exec()


class ChangePasswordDialog(QDialog):
    def __init__(self, db_manager, user_id, auth_service, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_id = user_id
        self.auth_service = auth_service
        
        self.setWindowTitle("Зміна пароля")
        self.setFixedSize(300, 250)
        self.setStyleSheet("background-color: #ecf0f1;")
        
        layout = QVBoxLayout()
        
        self.inp_old = QLineEdit()
        self.inp_old.setPlaceholderText("Поточний пароль")
        self.inp_old.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_old.setStyleSheet(INPUT_STYLE)
        
        self.inp_new = QLineEdit()
        self.inp_new.setPlaceholderText("Новий пароль")
        self.inp_new.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_new.setStyleSheet(INPUT_STYLE)
        
        self.inp_confirm = QLineEdit()
        self.inp_confirm.setPlaceholderText("Підтвердження пароля")
        self.inp_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_confirm.setStyleSheet(INPUT_STYLE)
        
        btn_save = QPushButton("Змінити")
        btn_save.setStyleSheet(BUTTON_STYLE)
        btn_save.clicked.connect(self.save_password)
        
        layout.addWidget(QLabel("Введіть дані:"))
        layout.addWidget(self.inp_old)
        layout.addWidget(self.inp_new)
        layout.addWidget(self.inp_confirm)
        layout.addWidget(btn_save)
        
        self.setLayout(layout)

    def save_password(self):
        old_pass = self.inp_old.text()
        new_pass = self.inp_new.text()
        confirm_pass = self.inp_confirm.text()
        
        # 1. Проверяем старый пароль
        old_hash = self.auth_service.hash_password(old_pass)
        if not self.db_manager.check_password(self.user_id, old_hash):
            QMessageBox.warning(self, "Помилка", "Невірний поточний пароль.")
            return
            
        # 2. Проверяем совпадение новых
        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Помилка", "Нові паролі не співпадають.")
            return
            
        if len(new_pass) < 4:
            QMessageBox.warning(self, "Помилка", "Пароль надто короткий.")
            return

        # 3. Сохраняем
        new_hash = self.auth_service.hash_password(new_pass)
        self.db_manager.change_password(self.user_id, new_hash)
        
        QMessageBox.information(self, "Успіх", "Пароль успішно змінено.")
        self.accept()
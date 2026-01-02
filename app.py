import sys
import os
from PyQt6.QtWidgets import QApplication
from app.database.db_manager import DatabaseManager
from app.ui.login_window import LoginWindow

# Пути к файлам
DB_PATH = os.path.join("data", "app_database.db")
SCHEMA_PATH = os.path.join("app", "database", "schema.sql")

def main():
    app = QApplication(sys.argv)
    
    # 1. Инициализация Базы Данных
    print("Подключение к базе данных...")
    db_manager = DatabaseManager(DB_PATH)
    
    # Создаем таблицы, если их нет
    if db_manager.execute_script(SCHEMA_PATH):
        print("База данных успешно инициализирована.")
    else:
        print("Ошибка инициализации БД!")
        sys.exit(1)

    # 2. Запуск окна логина
    # Передаем менеджер БД внутрь
    window = LoginWindow(db_manager)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
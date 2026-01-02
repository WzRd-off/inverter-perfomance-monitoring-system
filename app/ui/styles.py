PRIMARY_COLOR = "#2980b9"
ERROR_COLOR = "#e74c3c"
TEXT_COLOR = "#2c3e50"
BACKGROUND_COLOR = "#ecf0f1"

# Стили для кнопок
BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 5px;
        font-size: 14px;
        padding: 8px 16px;
        border: none;
    }}
    QPushButton:hover {{
        background-color: #3498db;
    }}
    QPushButton:pressed {{
        background-color: #1f618d;
    }}
"""

# Стили для полей ввода
INPUT_STYLE = f"""
    QLineEdit, QComboBox, QDateEdit {{
        border: 2px solid #bdc3c7;
        border-radius: 4px;
        padding: 5px;
        font-size: 14px;
        background-color: white;
        color: {TEXT_COLOR};
    }}
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
        border-color: #3498db;
    }}
    /* Для выпадающего списка */
    QComboBox QAbstractItemView {{
        background-color: white;
        color: {TEXT_COLOR};
        selection-background-color: {PRIMARY_COLOR};
        selection-color: white;
    }}
"""

# Стили для меток (Labels)
LABEL_STYLE = f"""
    QLabel {{
        color: {TEXT_COLOR};
        font-size: 14px;
    }}
"""

# Общие стили для главного окна и виджетов
# Исправлено: color: white -> color: {TEXT_COLOR}
MAIN_STYLE = f"""
    QMainWindow {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
        font-size: 14px;
    }}
    QWidget {{
        color: {TEXT_COLOR};
        font-size: 14px;
    }}
    QMessageBox {{
        background-color: {BACKGROUND_COLOR};
    }}
    QMessageBox QLabel {{
        color: {TEXT_COLOR};
    }}
"""
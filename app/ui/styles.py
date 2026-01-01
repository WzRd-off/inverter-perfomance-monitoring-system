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
    }}
    QPushButton:hover {{
        background-color: #3498db;
    }}
"""

# Стили для полей ввода
INPUT_STYLE = """
    QLineEdit {
        border: 2px solid #bdc3c7;
        border-radius: 4px;
        padding: 5px;
        font-size: 14px;
        background-color: white;
        color: black;
    }
    QLineEdit:focus {
        border-color: #3498db;
    }
"""

# Стили для меток
LABEL_STYLE = f"""
    QLabel {{
        color: {TEXT_COLOR};
        font-size: 14px;
    }}
"""

# Общие стили для главного окна
MAIN_STYLE = f"""
    QMainWindow {{
        background-color: {BACKGROUND_COLOR};
        color: white;
        font-size: 14px;
    }}
"""
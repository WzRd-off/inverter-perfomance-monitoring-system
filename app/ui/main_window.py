from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QStackedWidget, QLabel, QFrame)
from PyQt6.QtCore import Qt
from app.ui.styles import MAIN_STYLE

# Імпорти сторінок
from app.ui.views.devices import DevicesView
from app.ui.views.monitoring import MonitoringView
from app.ui.views.stats import StatsView  # <--- Додали імпорт

class MainWindow(QMainWindow):
    def __init__(self, user_data, db_manager):
        super().__init__()
        self.user_data = user_data
        self.db_manager = db_manager
        
        self.setWindowTitle("Inverter Monitoring System")
        self.setFixedSize(1100, 700)
        self.setStyleSheet(MAIN_STYLE)
        
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Боковое меню ---
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("background-color: #2c3e50; min-width: 200px;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        menu_title = QLabel("Меню")
        menu_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 10px;")
        sidebar_layout.addWidget(menu_title)
        
        self.btn_dashboard = self.create_menu_button("Дашборд")
        self.btn_monitoring = self.create_menu_button("Мониторинг")
        self.btn_stats = self.create_menu_button("Статистика") # <--- Додали кнопку
        self.btn_devices = self.create_menu_button("Пристрої")
        
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_monitoring)
        sidebar_layout.addWidget(self.btn_stats) # <--- Додали в лайаут
        
        if self.user_data['is_admin']:
             sidebar_layout.addWidget(self.btn_devices)

        sidebar_layout.addStretch()
        
        self.btn_logout = self.create_menu_button("Вихід")
        self.btn_logout.setStyleSheet("background-color: #c0392b; color: white; padding: 10px; text-align: left;")
        self.btn_logout.clicked.connect(self.close)
        sidebar_layout.addWidget(self.btn_logout)

        # --- Контент ---
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: #ecf0f1;")
        
        # Стр 1: Дашборд
        self.page_dashboard = QWidget()
        dash_layout = QVBoxLayout(self.page_dashboard)
        dash_layout.addWidget(QLabel(f"Вітаємо, {self.user_data['full_name']}!"))
        dash_layout.addStretch()
        
        # Стр 2: Мониторинг
        self.page_monitoring = MonitoringView(self.db_manager)
        
        # Стр 3: Статистика (Index 2)
        self.page_stats = StatsView(self.db_manager) # <--- Створили сторінку
        
        # Стр 4: Устройства (Index 3)
        self.page_devices = DevicesView(self.db_manager)

        self.content_area.addWidget(self.page_dashboard)   # 0
        self.content_area.addWidget(self.page_monitoring)  # 1
        self.content_area.addWidget(self.page_stats)       # 2 <--- Додали в стек
        self.content_area.addWidget(self.page_devices)     # 3
        
        # Навігація
        self.btn_dashboard.clicked.connect(lambda: self.content_area.setCurrentIndex(0))
        self.btn_monitoring.clicked.connect(lambda: self.content_area.setCurrentIndex(1))
        self.btn_stats.clicked.connect(lambda: self.content_area.setCurrentIndex(2)) # <--- Підключили
        self.btn_devices.clicked.connect(lambda: self.content_area.setCurrentIndex(3))

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)
        
        self.setCentralWidget(central_widget)

    def create_menu_button(self, text):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                text-align: left;
                padding: 10px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        return btn
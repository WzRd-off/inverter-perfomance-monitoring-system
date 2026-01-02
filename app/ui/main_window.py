from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QStackedWidget, QLabel, QFrame)
from PyQt6.QtCore import Qt
from app.ui.styles import MAIN_STYLE

# Імпорти сторінок
from app.ui.views.devices import DevicesView
from app.ui.views.monitoring import MonitoringView
from app.ui.views.stats import StatsView
from app.ui.views.batteries import BatteriesView
from app.ui.views.errors import ErrorsView
from app.ui.views.profile import ProfileView # <---
from app.ui.views.reports import ReportsView # <---

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
        self.btn_errors = self.create_menu_button("Журнал збоїв")
        self.btn_stats = self.create_menu_button("Статистика")
        self.btn_reports = self.create_menu_button("Звіти") # <---
        
        # Админские кнопки
        self.btn_devices = self.create_menu_button("Інвертори")
        self.btn_batteries = self.create_menu_button("Акумулятори")
        
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_monitoring)
        sidebar_layout.addWidget(self.btn_errors)
        sidebar_layout.addWidget(self.btn_stats)
        sidebar_layout.addWidget(self.btn_reports) # <---
        
        if self.user_data['is_admin']:
             sidebar_layout.addWidget(self.btn_devices)
             sidebar_layout.addWidget(self.btn_batteries)

        sidebar_layout.addStretch()
        
        # Кнопки внизу (Профиль и Выход)
        self.btn_profile = self.create_menu_button("Профіль") # <---
        sidebar_layout.addWidget(self.btn_profile)
        
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
        
        # Стр 3: Журнал (Index 2)
        self.page_errors = ErrorsView(self.db_manager)
        
        # Стр 4: Статистика (Index 3)
        self.page_stats = StatsView(self.db_manager)
        
        # Стр 5: Устройства (Index 4)
        self.page_devices = DevicesView(self.db_manager)

        # Стр 6: Акумулятори (Index 5)
        self.page_batteries = BatteriesView(self.db_manager)
        
        # Стр 7: Звіти (Index 6)
        self.page_reports = ReportsView(self.db_manager) # <---
        
        # Стр 8: Профіль (Index 7)
        self.page_profile = ProfileView(self.db_manager, self.user_data) # <---

        self.content_area.addWidget(self.page_dashboard)   # 0
        self.content_area.addWidget(self.page_monitoring)  # 1
        self.content_area.addWidget(self.page_errors)      # 2
        self.content_area.addWidget(self.page_stats)       # 3
        self.content_area.addWidget(self.page_devices)     # 4
        self.content_area.addWidget(self.page_batteries)   # 5
        self.content_area.addWidget(self.page_reports)     # 6
        self.content_area.addWidget(self.page_profile)     # 7
        
        # Навигация
        self.btn_dashboard.clicked.connect(lambda: self.content_area.setCurrentIndex(0))
        self.btn_monitoring.clicked.connect(lambda: self.content_area.setCurrentIndex(1))
        self.btn_errors.clicked.connect(lambda: self.content_area.setCurrentIndex(2))
        self.btn_stats.clicked.connect(lambda: self.content_area.setCurrentIndex(3))
        if self.user_data['is_admin']:
            self.btn_devices.clicked.connect(lambda: self.content_area.setCurrentIndex(4))
            self.btn_batteries.clicked.connect(lambda: self.content_area.setCurrentIndex(5))
        
        self.btn_reports.clicked.connect(lambda: self.content_area.setCurrentIndex(6))
        self.btn_profile.clicked.connect(lambda: self.content_area.setCurrentIndex(7))

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
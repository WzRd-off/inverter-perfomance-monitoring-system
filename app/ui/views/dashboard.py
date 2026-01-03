from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

class DashboardView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
        # Автооновлення раз на 5 секунд
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_stats)
        self.timer.start(5000)

    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel("Панель керування системою")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(header)

        # Сітка карток
        grid = QGridLayout()
        grid.setSpacing(20)

        # Картки
        self.card_inv = self._create_card("Інвертори (Всього/Активні)", "0 / 0", "#3498db")
        self.card_bat = self._create_card("Акумулятори", "0", "#9b59b6")
        self.card_err = self._create_card("Активні аварії", "0", "#e74c3c")
        self.card_maint = self._create_card("Потребують ТО", "0", "#f39c12")

        grid.addWidget(self.card_inv, 0, 0)
        grid.addWidget(self.card_bat, 0, 1)
        grid.addWidget(self.card_err, 1, 0)
        grid.addWidget(self.card_maint, 1, 1)

        layout.addLayout(grid)
        
        # Блок "Найближче ТО" (Список)
        layout.addSpacing(30)
        sub_header = QLabel("Прогноз технічного обслуговування (Топ-5)")
        sub_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(sub_header)

        self.maintenance_list = QVBoxLayout()
        maintenance_frame = QFrame()
        maintenance_frame.setStyleSheet("background-color: white; border-radius: 5px;")
        maintenance_frame.setLayout(self.maintenance_list)
        
        layout.addWidget(maintenance_frame)
        layout.addStretch()
        
        self.setLayout(layout)
        self.refresh_stats()

    def _create_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 5px solid {color};
                border-radius: 5px;
            }}
        """)
        card.setMinimumHeight(100)
        l = QVBoxLayout(card)
        
        t = QLabel(title)
        t.setStyleSheet("color: #7f8c8d; font-size: 14px; border: none;")
        v = QLabel(value)
        v.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold; border: none;")
        v.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        l.addWidget(t)
        l.addWidget(v)
        return card

    def refresh_stats(self):
        stats = self.db_manager.get_dashboard_stats()
        
        # Оновлення цифр
        total = stats.get('inverters_total', 0)
        active = stats.get('inverters_active', 0)
        self.card_inv.layout().itemAt(1).widget().setText(f"{total} / {active}")
        
        self.card_bat.layout().itemAt(1).widget().setText(str(stats.get('batteries_total', 0)))
        
        err_count = stats.get('active_errors', 0)
        self.card_err.layout().itemAt(1).widget().setText(str(err_count))
        
        maint_count = stats.get('maintenance_overdue', 0)
        self.card_maint.layout().itemAt(1).widget().setText(str(maint_count))
        if maint_count > 0:
             self.card_maint.setStyleSheet(self.card_maint.styleSheet().replace("#f39c12", "#c0392b")) # Red if overdue
        
        # Оновлення списку ТО
        self._update_maintenance_list()

    def _update_maintenance_list(self):
        # Очищення старого списку
        while self.maintenance_list.count():
            item = self.maintenance_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        forecast = self.db_manager.get_maintenance_forecast()
        
        if not forecast:
            self.maintenance_list.addWidget(QLabel("Немає даних для прогнозу."))
            return

        # Беремо топ-5
        for item in forecast[:5]:
            # === FIX: Check for None before converting to int ===
            if item['days_left'] is None:
                continue

            try:
                days = int(item['days_left'])
                sn = item['serial_number']
                date_to = item['next_service_date']
                
                if days < 0:
                    text = f"⚠️ {sn}: Прострочено на {abs(days)} дн. (Дата: {date_to})"
                    color = "red"
                elif days <= 30:
                    text = f"⚠️ {sn}: Через {days} дн. (Дата: {date_to})"
                    color = "orange"
                else:
                    text = f"✅ {sn}: Через {days} дн. (Дата: {date_to})"
                    color = "green"
                    
                lbl = QLabel(text)
                lbl.setStyleSheet(f"color: {color}; font-size: 14px; padding: 5px; border: none;")
                self.maintenance_list.addWidget(lbl)
            except (ValueError, TypeError):
                continue
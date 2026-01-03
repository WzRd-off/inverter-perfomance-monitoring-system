from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

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
        
        header = QLabel("Загальний огляд системи")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(header)

        # Сітка для карток (2x2)
        grid = QGridLayout()
        grid.setSpacing(20)

        # Створюємо віджети карток
        self.card_inv_total = self._create_card("Всього інверторів", "0", "#3498db")
        self.card_inv_active = self._create_card("Активні інвертори", "0", "#2ecc71")
        self.card_bat_total = self._create_card("Акумуляторні батареї", "0", "#9b59b6")
        self.card_errors = self._create_card("Активні аварії", "0", "#e74c3c")

        grid.addWidget(self.card_inv_total, 0, 0)
        grid.addWidget(self.card_inv_active, 0, 1)
        grid.addWidget(self.card_bat_total, 1, 0)
        grid.addWidget(self.card_errors, 1, 1)

        layout.addLayout(grid)
        layout.addStretch() # Підтискаємо все вгору
        
        self.setLayout(layout)
        self.refresh_stats() # Перше оновлення

    def _create_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 5px solid {color};
                border-radius: 5px;
            }}
        """)
        card.setMinimumHeight(120)
        
        l = QVBoxLayout(card)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #7f8c8d; font-size: 16px; border: none;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {color}; font-size: 36px; font-weight: bold; border: none;")
        lbl_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        l.addWidget(lbl_title)
        l.addWidget(lbl_value)
        
        return card

    def refresh_stats(self):
        stats = self.db_manager.get_dashboard_stats()
        
        # Оновлюємо текст (знаходимо QLabel зі значенням - це другий елемент у лайауті)
        self.card_inv_total.layout().itemAt(1).widget().setText(str(stats.get('inverters_total', 0)))
        self.card_inv_active.layout().itemAt(1).widget().setText(str(stats.get('inverters_active', 0)))
        self.card_bat_total.layout().itemAt(1).widget().setText(str(stats.get('batteries_total', 0)))
        
        err_count = stats.get('active_errors', 0)
        self.card_errors.layout().itemAt(1).widget().setText(str(err_count))
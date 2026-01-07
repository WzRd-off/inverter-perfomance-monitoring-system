from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QGridLayout, QScrollArea, QSizePolicy, QTableWidget, 
                             QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QCursor

class DashboardView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        
        # Обновление раз в 3 секунды
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_stats)
        self.timer.start(3000)

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 1. Header
        header_layout = QHBoxLayout()
        title = QLabel("Головна панель керування")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        
        self.lbl_last_update = QLabel("Оновлено: -")
        self.lbl_last_update.setStyleSheet("color: gray; font-size: 12px;")
        self.lbl_last_update.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_last_update)
        main_layout.addLayout(header_layout)

        # 2. KPI Cards
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)

        self.card_total_inv = self._create_kpi_card("Інвертори", "0", "#3498db", "Всього / Активні")
        self.card_total_bat = self._create_kpi_card("Акумулятори", "0", "#9b59b6")
        self.card_alarms = self._create_kpi_card("Активні аварії", "0", "#e74c3c", "Потребують уваги")
        self.card_eff = self._create_kpi_card("Середній ККД", "0%", "#27ae60", "За цю добу")
        self.card_gen = self._create_kpi_card("Генерація", "0 Wh", "#f39c12", "За цю добу")

        kpi_layout.addWidget(self.card_total_inv)
        kpi_layout.addWidget(self.card_total_bat)
        kpi_layout.addWidget(self.card_alarms)
        kpi_layout.addWidget(self.card_eff)
        kpi_layout.addWidget(self.card_gen)
        
        main_layout.addLayout(kpi_layout)

        # 3. Status Grid
        lbl_status = QLabel("Статус обладнання")
        lbl_status.setStyleSheet("font-size: 18px; font-weight: bold; color: #34495e; margin-top: 10px;")
        main_layout.addWidget(lbl_status)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")
        scroll_area.setFixedHeight(150) # Ограничиваем высоту, чтобы влез прогноз
        
        self.status_container = QWidget()
        self.status_grid = QGridLayout(self.status_container)
        self.status_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.status_grid.setSpacing(15)
        
        scroll_area.setWidget(self.status_container)
        main_layout.addWidget(scroll_area)

        # 4. Forecast Section (New)
        lbl_forecast = QLabel("Прогноз подій (ТО та Заміна)")
        lbl_forecast.setStyleSheet("font-size: 18px; font-weight: bold; color: #34495e; margin-top: 10px;")
        main_layout.addWidget(lbl_forecast)

        self.table_forecast = QTableWidget()
        self.table_forecast.setColumnCount(5)
        self.table_forecast.setHorizontalHeaderLabels(["Тип події", "Модель / S/N", "Дата встановлення", "План. дата", "Залишилось"])
        self.table_forecast.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_forecast.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_forecast.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_forecast.setFixedHeight(200)
        
        main_layout.addWidget(self.table_forecast)

        self.setLayout(main_layout)
        self.refresh_stats()

    def _create_kpi_card(self, title, value, color, subtitle=""):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border-left: 5px solid {color};
            }}
        """)
        card.setMinimumHeight(100)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #7f8c8d; font-size: 14px; font-weight: 500;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        
        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet("color: #95a5a6; font-size: 11px;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        layout.addWidget(lbl_sub)
        
        return card

    def refresh_stats(self):
        from datetime import datetime
        
        # 1. Update KPI
        stats = self.db_manager.get_dashboard_aggregated_stats()
        
        total_inv = stats.get('inverters_total', 0)
        self.card_total_inv.layout().itemAt(1).widget().setText(f"{total_inv}")
        
        self.card_total_bat.layout().itemAt(1).widget().setText(str(stats.get('batteries_total', 0)))
        
        alarms = stats.get('active_errors', 0)
        self.card_alarms.layout().itemAt(1).widget().setText(str(alarms))
        
        avg_eff = stats.get('avg_efficiency', 0.0)
        self.card_eff.layout().itemAt(1).widget().setText(f"{avg_eff:.1f}%")
        
        gen_wh = stats.get('daily_generation_wh', 0.0)
        if gen_wh > 1000:
            gen_str = f"{gen_wh/1000:.2f} kWh"
        else:
            gen_str = f"{gen_wh:.0f} Wh"
        self.card_gen.layout().itemAt(1).widget().setText(gen_str)
        
        self.lbl_last_update.setText(f"Оновлено: {datetime.now().strftime('%H:%M:%S')}")

        # 2. Update Status Grid
        self._update_status_grid()
        
        # 3. Update Forecast List
        self._update_forecast_list()

    def _update_status_grid(self):
        # Очистка
        while self.status_grid.count():
            item = self.status_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        inverters = self.db_manager.get_inverters_status_list()
        
        columns = 4
        row = 0
        col = 0
        
        for inv in inverters:
            status = inv['status']
            if status == 'OK' or status == 'Normal':
                bg_color = "#2ecc71"
                status_text = "NORMAL"
            elif status == 'Warning':
                bg_color = "#f1c40f"
                status_text = "WARNING"
            elif status == 'Error':
                bg_color = "#e74c3c"
                status_text = "ERROR"
            elif status == 'Offline':
                bg_color = "#95a5a6"
                status_text = "OFFLINE"
            else:
                bg_color = "#95a5a6"
                status_text = status.upper()

            frame = QFrame()
            frame.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border-radius: 8px;
                    color: white;
                }}
                QFrame:hover {{
                    border: 2px solid #34495e;
                }}
            """)
            frame.setFixedSize(200, 100)
            
            fl = QVBoxLayout(frame)
            name_lbl = QLabel(f"{inv['model_name']}")
            name_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
            sn_lbl = QLabel(f"S/N: {inv['serial_number']}")
            sn_lbl.setStyleSheet("font-size: 11px;")
            stat_lbl = QLabel(status_text)
            stat_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            stat_lbl.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
            
            fl.addWidget(name_lbl)
            fl.addWidget(sn_lbl)
            fl.addWidget(stat_lbl)
            
            self.status_grid.addWidget(frame, row, col)
            
            col += 1
            if col >= columns:
                col = 0
                row += 1

    def _update_forecast_list(self):
        forecasts = self.db_manager.get_full_forecast_report()
        self.table_forecast.setRowCount(0)
        
        for row_idx, item in enumerate(forecasts):
            self.table_forecast.insertRow(row_idx)
            
            # Тип
            type_item = QTableWidgetItem(str(item['type']))
            if "ТО" in item['type']:
                type_item.setForeground(QColor("#e67e22")) # Orange
            else:
                type_item.setForeground(QColor("#c0392b")) # Red
            self.table_forecast.setItem(row_idx, 0, type_item)
            
            # Модель
            self.table_forecast.setItem(row_idx, 1, QTableWidgetItem(f"{item['model_name']} ({item['serial_number']})"))
            
            # Дата установки
            self.table_forecast.setItem(row_idx, 2, QTableWidgetItem(str(item['install_date'])))
            
            # Целевая дата
            self.table_forecast.setItem(row_idx, 3, QTableWidgetItem(str(item['target_date'])))
            
            # Осталось
            try:
                days = int(item['days_left'])
                if days < 0:
                    days_str = f"ПРОСТРОЧЕНО на {abs(days)} дн."
                else:
                    days_str = f"{days} дн."
                
                days_item = QTableWidgetItem(days_str)
                if days < 30:
                     days_item.setBackground(QColor("#fadbd8")) # Light red bg
                self.table_forecast.setItem(row_idx, 4, days_item)
            except:
                self.table_forecast.setItem(row_idx, 4, QTableWidgetItem("N/A"))
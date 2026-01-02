import os
import pyqtgraph as pg
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from app.ui.styles import BUTTON_STYLE, LABEL_STYLE
from app.logic.emulator import TelemetryEmulator
from app.logic.analyzer import SystemAnalyzer

class MonitoringView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        
        csv_path = os.path.join("data", "emulator.csv")
        self.emulator = TelemetryEmulator(csv_path)
        self.analyzer = SystemAnalyzer(self.db_manager)
        
        self.is_monitoring = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        
        self.history_limit = 50
        self.time_data = []
        self.power_data = []
        self.voltage_data = []
        self.counter = 0

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # --- Верхня панель ---
        top_panel = QHBoxLayout()
        
        lbl_inv = QLabel("Оберіть інвертор:")
        lbl_inv.setStyleSheet(LABEL_STYLE)
        
        self.combo_inverter = QComboBox()
        self.combo_inverter.setStyleSheet("padding: 5px; font-size: 14px; min-width: 200px;")
        # Завантаження відбудеться автоматично в showEvent
        
        self.btn_toggle = QPushButton("Запустити моніторинг")
        self.btn_toggle.setStyleSheet(BUTTON_STYLE)
        self.btn_toggle.clicked.connect(self.toggle_monitoring)
        
        self.lbl_status = QLabel("СТАТУС: ОЧІКУВАННЯ")
        self.lbl_status.setStyleSheet("font-weight: bold; font-size: 16px; color: gray; margin-left: 20px;")

        top_panel.addWidget(lbl_inv)
        top_panel.addWidget(self.combo_inverter)
        top_panel.addWidget(self.btn_toggle)
        top_panel.addWidget(self.lbl_status)
        top_panel.addStretch()
        
        layout.addLayout(top_panel)

        # --- Основна зона ---
        content_layout = QHBoxLayout()
        
        # Таблиця
        self.table_metrics = QTableWidget()
        self.table_metrics.setColumnCount(2)
        self.table_metrics.setHorizontalHeaderLabels(["Параметр", "Значення"])
        self.table_metrics.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_metrics.verticalHeader().setVisible(False)
        self.table_metrics.setFixedWidth(350)
        
        self.metrics_map = {
            "Потужність PV (Вхід)": "dc_input_power",
            "Потужність AC (Вихід)": "ac_output_power",
            "Напруга PV": "dc_voltage",
            "Напруга Мережі": "ac_voltage",
            "Заряд батареї (SOC)": "battery_soc",
            "Напруга батареї": "battery_voltage",
            "Температура Інвертора": "inverter_temperature",
            "Температура Батареї": "battery_temperature",
            "Частота мережі": "grid_frequency"
        }
        self.table_metrics.setRowCount(len(self.metrics_map))
        for i, name in enumerate(self.metrics_map.keys()):
            self.table_metrics.setItem(i, 0, QTableWidgetItem(name))
            self.table_metrics.setItem(i, 1, QTableWidgetItem("-"))
        
        content_layout.addWidget(self.table_metrics)

        # Графіки
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        
        self.graph_widget = pg.GraphicsLayoutWidget()
        
        self.plot_power = self.graph_widget.addPlot(title="Потужність (Вт)")
        self.plot_power.showGrid(x=True, y=True)
        self.curve_power = self.plot_power.plot(pen=pg.mkPen(color='#2980b9', width=2))
        
        self.graph_widget.nextRow()
        
        self.plot_voltage = self.graph_widget.addPlot(title="Напруга PV (В)")
        self.plot_voltage.showGrid(x=True, y=True)
        self.curve_voltage = self.plot_voltage.plot(pen=pg.mkPen(color='#e67e22', width=2))

        content_layout.addWidget(self.graph_widget)
        
        layout.addLayout(content_layout)
        self.setLayout(layout)

    def showEvent(self, event):
        """Цей метод викликається автоматично при перемиканні на цю вкладку"""
        self._load_inverters()
        super().showEvent(event)

    def _load_inverters(self):
        # Зберігаємо поточний вибір, щоб він не збивався при оновленні
        current_id = self.combo_inverter.currentData()
        
        self.combo_inverter.clear()
        inverters = self.db_manager.get_all_inverters()
        
        found_current = False
        for inv in inverters:
            text = f"{inv['model_name']} (S/N: {inv['serial_number']})"
            self.combo_inverter.addItem(text, inv['id'])
            if inv['id'] == current_id:
                found_current = True
        
        # Якщо попередній вибраний інвертор ще існує, вибираємо його знову
        if found_current:
            index = self.combo_inverter.findData(current_id)
            self.combo_inverter.setCurrentIndex(index)

    def toggle_monitoring(self):
        if self.combo_inverter.count() == 0:
            QMessageBox.warning(self, "Помилка", "Спочатку додайте інвертор у вкладці 'Пристрої'")
            return

        if not self.is_monitoring:
            self.is_monitoring = True
            self.btn_toggle.setText("Зупинити")
            self.btn_toggle.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px;")
            self.timer.start(1000)
            self.combo_inverter.setEnabled(False) # Блокуємо вибір під час роботи
        else:
            self.is_monitoring = FalseS
            self.btn_toggle.setText("Запустити моніторинг")
            self.btn_toggle.setStyleSheet(BUTTON_STYLE)
            self.timer.stop()
            self.lbl_status.setText("СТАТУС: ЗУПИНЕНО")
            self.lbl_status.setStyleSheet("font-weight: bold; font-size: 16px; color: gray; margin-left: 20px;")
            self.combo_inverter.setEnabled(True)

    def update_data(self):
        data = self.emulator.get_next_record()
        if not data:
            return

        current_inv_id = self.combo_inverter.currentData()
        data['inverter_id'] = current_inv_id

        errors = self.analyzer.check_status(data)
        
        if errors:
            status_text = f"УВАГА: ВИЯВЛЕНО {len(errors)} ПОМИЛОК!"
            status_style = "font-weight: bold; font-size: 16px; color: red; margin-left: 20px;"
        else:
            status_text = "СТАТУС: НОРМА"
            status_style = "font-weight: bold; font-size: 16px; color: green; margin-left: 20px;"
        
        self.lbl_status.setText(status_text)
        self.lbl_status.setStyleSheet(status_style)

        for row, (label, key) in enumerate(self.metrics_map.items()):
            val = data.get(key)
            if val is not None:
                self.table_metrics.setItem(row, 1, QTableWidgetItem(str(val)))

        self.counter += 1
        self.time_data.append(self.counter)
        self.power_data.append(data.get('ac_output_power', 0))
        self.voltage_data.append(data.get('dc_voltage', 0))

        if len(self.time_data) > self.history_limit:
            self.time_data.pop(0)
            self.power_data.pop(0)
            self.voltage_data.pop(0)

        self.curve_power.setData(self.time_data, self.power_data)
        self.curve_voltage.setData(self.time_data, self.voltage_data)
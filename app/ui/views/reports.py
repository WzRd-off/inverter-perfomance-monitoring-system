from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, 
                             QPushButton, QDateEdit, QFrame, QMessageBox, QFileDialog)
from PyQt6.QtCore import QDate
from app.ui.styles import BUTTON_STYLE, INPUT_STYLE, LABEL_STYLE
import csv

class ReportsView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel("Генерація звітів")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(header)

        # Карточка настроек
        card = QFrame()
        card.setStyleSheet("background-color: white; border-radius: 10px; padding: 20px;")
        form = QVBoxLayout(card)
        
        # Тип отчета
        form.addWidget(QLabel("Тип звіту:"))
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Історія показників (CSV)", "Журнал помилок (CSV)", "Зведений звіт (Text)"])
        self.combo_type.setStyleSheet(INPUT_STYLE)
        form.addWidget(self.combo_type)
        
        # Инвертор
        form.addWidget(QLabel("Інвертор:"))
        self.combo_inv = QComboBox()
        self.combo_inv.setStyleSheet(INPUT_STYLE)
        self._load_inverters()
        form.addWidget(self.combo_inv)
        
        # Период
        form.addWidget(QLabel("Період з:"))
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate().addDays(-7))
        self.date_start.setStyleSheet(INPUT_STYLE)
        form.addWidget(self.date_start)
        
        form.addWidget(QLabel("по:"))
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setStyleSheet(INPUT_STYLE)
        form.addWidget(self.date_end)
        
        # Кнопка
        btn_gen = QPushButton("Згенерувати та зберегти")
        btn_gen.setStyleSheet(BUTTON_STYLE)
        btn_gen.clicked.connect(self.generate_report)
        form.addWidget(btn_gen)
        
        layout.addWidget(card)
        layout.addStretch()
        self.setLayout(layout)

    def _load_inverters(self):
        self.combo_inv.addItem("Всі інвертори", None)
        invs = self.db_manager.get_all_inverters()
        for i in invs:
            self.combo_inv.addItem(f"{i['model_name']} ({i['serial_number']})", i['id'])

    def generate_report(self):
        report_type = self.combo_type.currentText()
        inv_id = self.combo_inv.currentData()
        d_start = self.date_start.date().toString("yyyy-MM-dd")
        d_end = self.date_end.date().toString("yyyy-MM-dd")

        if "Історія показників" in report_type:
            if inv_id is None:
                QMessageBox.warning(self, "Увага", "Для цього звіту оберіть конкретний інвертор.")
                return
            data = self.db_manager.get_sensor_data_by_period(inv_id, d_start, d_end)
            if not data:
                QMessageBox.information(self, "Інфо", "Немає даних за цей період.")
                return
            self._save_csv(data, ["Timestamp", "Input Power", "Output Power", "Status"], 
                           ["timestamp", "dc_input_power", "ac_output_power", "status"])

        elif "Журнал помилок" in report_type:
            # Для ошибок мы не фильтруем по инвертору в запросе пока что, но можем доработать
            data = self.db_manager.get_all_errors() # Здесь можно добавить фильтр по датам
            if not data:
                QMessageBox.information(self, "Інфо", "Помилок не знайдено.")
                return
            self._save_csv(data, ["ID", "Time", "Type", "Param", "Value", "Status"],
                           ["id", "timestamp", "error_type", "parameter_name", "current_value", "status"])

        elif "Зведений звіт" in report_type:
            QMessageBox.information(self, "Інфо", "Функція в розробці.")

    def _save_csv(self, data, headers, keys):
        file_path, _ = QFileDialog.getSaveFileName(self, "Зберегти звіт", "", "CSV Files (*.csv)")
        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(headers)
                for row in data:
                    writer.writerow([row[k] for k in keys])
            QMessageBox.information(self, "Успіх", f"Звіт збережено: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))
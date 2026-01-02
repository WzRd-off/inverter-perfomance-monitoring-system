from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QDialogButtonBox, QDateEdit, QMessageBox)
from PyQt6.QtCore import QDate
from app.ui.styles import INPUT_STYLE, LABEL_STYLE

class BatteryDialog(QDialog):
    def __init__(self, db_manager, battery_data=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.battery_data = battery_data
        
        self.setWindowTitle("Додати акумулятор" if not battery_data else "Редагувати акумулятор")
        self.setFixedSize(400, 400)
        self.setStyleSheet("background-color: #ecf0f1;")

        layout = QVBoxLayout()

        # Модель
        layout.addWidget(QLabel("Модель акумулятора:"))
        self.combo_model = QComboBox()
        self.combo_model.setStyleSheet(INPUT_STYLE)
        self._load_models()
        layout.addWidget(self.combo_model)

        # Инвертор (к кому подключена)
        layout.addWidget(QLabel("Підключено до інвертора:"))
        self.combo_inverter = QComboBox()
        self.combo_inverter.setStyleSheet(INPUT_STYLE)
        self._load_inverters()
        layout.addWidget(self.combo_inverter)

        # Серийный номер
        layout.addWidget(QLabel("Серійний номер:"))
        self.input_serial = QLineEdit()
        self.input_serial.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.input_serial)

        # Дата установки
        layout.addWidget(QLabel("Дата встановлення:"))
        self.date_install = QDateEdit()
        self.date_install.setCalendarPopup(True)
        self.date_install.setDate(QDate.currentDate())
        self.date_install.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.date_install)

        # Кнопки
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

        if self.battery_data:
            self._fill_data()

    def _load_models(self):
        models = self.db_manager.get_battery_models()
        for m in models:
            self.combo_model.addItem(m['battery_model'], m['id'])

    def _load_inverters(self):
        self.combo_inverter.addItem("Не підключено", None)
        inverters = self.db_manager.get_inverters_simple()
        for i in inverters:
            self.combo_inverter.addItem(f"S/N: {i['serial_number']}", i['id'])

    def _fill_data(self):
        idx_model = self.combo_model.findData(self.battery_data['model_id'])
        if idx_model >= 0: self.combo_model.setCurrentIndex(idx_model)
        
        if self.battery_data['inverter_id']:
            idx_inv = self.combo_inverter.findData(self.battery_data['inverter_id'])
            if idx_inv >= 0: self.combo_inverter.setCurrentIndex(idx_inv)
        
        self.input_serial.setText(self.battery_data['serial_number'])
        if self.battery_data['install_date']:
            self.date_install.setDate(QDate.fromString(self.battery_data['install_date'], "yyyy-MM-dd"))

    def validate_and_accept(self):
        if not self.input_serial.text():
            QMessageBox.warning(self, "Помилка", "Серійний номер не може бути порожнім")
            return
        self.accept()

    def get_data(self):
        return {
            "model_id": self.combo_model.currentData(),
            "inverter_id": self.combo_inverter.currentData(),
            "serial_number": self.input_serial.text(),
            "install_date": self.date_install.date().toString("yyyy-MM-dd")
        }
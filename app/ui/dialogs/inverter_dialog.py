from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QDialogButtonBox, QDateEdit, QMessageBox)
from PyQt6.QtCore import QDate
from app.ui.styles import INPUT_STYLE, LABEL_STYLE

class InverterDialog(QDialog):
    def __init__(self, db_manager, inverter_data=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.inverter_data = inverter_data # Если None - создание, иначе редактирование
        
        self.setWindowTitle("Додати інвертор" if not inverter_data else "Редагувати інвертор")
        self.setFixedSize(400, 350)
        self.setStyleSheet("background-color: #ecf0f1;")

        layout = QVBoxLayout()

        # Модель
        layout.addWidget(QLabel("Модель інвертора:"))
        self.combo_model = QComboBox()
        self.combo_model.setStyleSheet(INPUT_STYLE)
        self._load_models()
        layout.addWidget(self.combo_model)

        # Серийный номер
        layout.addWidget(QLabel("Серійний номер:"))
        self.input_serial = QLineEdit()
        self.input_serial.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.input_serial)

        # Локация
        layout.addWidget(QLabel("Місце встановлення:"))
        self.input_location = QLineEdit()
        self.input_location.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.input_location)

        # Дата установки
        layout.addWidget(QLabel("Дата встановлення:"))
        self.date_install = QDateEdit()
        self.date_install.setCalendarPopup(True)
        self.date_install.setDate(QDate.currentDate())
        self.date_install.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.date_install)

        # Кнопки OK/Cancel
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

        # Если редактирование - заполняем поля
        if self.inverter_data:
            self._fill_data()

    def _load_models(self):
        models = self.db_manager.get_inverter_models()
        for m in models:
            # save ID in user data
            self.combo_model.addItem(m['model_name'], m['id'])

    def _fill_data(self):
        # Устанавливаем модель
        index = self.combo_model.findData(self.inverter_data['model_id'])
        if index >= 0:
            self.combo_model.setCurrentIndex(index)
        
        self.input_serial.setText(self.inverter_data['serial_number'])
        self.input_location.setText(self.inverter_data['location'])
        if self.inverter_data['install_date']:
            self.date_install.setDate(QDate.fromString(self.inverter_data['install_date'], "yyyy-MM-dd"))

    def validate_and_accept(self):
        if not self.input_serial.text():
            QMessageBox.warning(self, "Помилка", "Серійний номер не може бути порожнім")
            return
        
        self.accept()

    def get_data(self):
        return {
            "model_id": self.combo_model.currentData(),
            "serial_number": self.input_serial.text(),
            "location": self.input_location.text(),
            "install_date": self.date_install.date().toString("yyyy-MM-dd")
        }
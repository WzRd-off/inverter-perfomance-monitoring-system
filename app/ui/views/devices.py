from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QLabel)
from PyQt6.QtCore import Qt
from app.ui.styles import BUTTON_STYLE
from app.ui.dialogs.inverter_dialog import InverterDialog

class DevicesView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        
        layout = QVBoxLayout()
        
        # Заголовок
        header = QLabel("Керування інверторами")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)

        # Панель кнопок
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Додати інвертор")
        self.btn_add.setStyleSheet(BUTTON_STYLE)
        self.btn_edit = QPushButton("Редагувати")
        self.btn_edit.setStyleSheet(BUTTON_STYLE)
        self.btn_delete = QPushButton("Видалити")
        self.btn_delete.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 5px; padding: 8px;")
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Модель", "S/N", "Локація", "Дата встан.", "Статус"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Запрет редактирования ячеек напрямую
        layout.addWidget(self.table)

        # Обработчики
        self.btn_add.clicked.connect(self.add_device)
        self.btn_edit.clicked.connect(self.edit_device)
        self.btn_delete.clicked.connect(self.delete_device)

        self.setLayout(layout)
        self.refresh_table()

    def refresh_table(self):
        """Загрузка данных из БД в таблицу"""
        self.table.setRowCount(0)
        inverters = self.db_manager.get_all_inverters()
        
        for row_idx, inv in enumerate(inverters):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(inv['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(inv['model_name'])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(inv['serial_number'])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(inv['location'])))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(inv['install_date'])))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(inv['status'])))

    def add_device(self):
        dialog = InverterDialog(self.db_manager, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            self.db_manager.add_inverter(
                data['model_id'], data['serial_number'], data['location'], data['install_date']
            )
            self.refresh_table()

    def get_selected_id(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None
        # ID всегда в 0-й колонке
        return int(self.table.item(selected_items[0].row(), 0).text())

    def edit_device(self):
        inv_id = self.get_selected_id()
        if not inv_id:
            QMessageBox.warning(self, "Увага", "Оберіть інвертор для редагування")
            return
            
        # Получаем полные данные (в реальном проекте лучше сделать отдельный SELECT WHERE id=...)
        # Здесь найдем в списке для простоты
        all_invs = self.db_manager.get_all_inverters()
        target_inv = next((i for i in all_invs if i['id'] == inv_id), None)
        
        if target_inv:
            dialog = InverterDialog(self.db_manager, inverter_data=target_inv, parent=self)
            if dialog.exec():
                data = dialog.get_data()
                self.db_manager.update_inverter(
                    inv_id, data['model_id'], data['serial_number'], data['location'], data['install_date']
                )
                self.refresh_table()

    def delete_device(self):
        inv_id = self.get_selected_id()
        if not inv_id:
            QMessageBox.warning(self, "Увага", "Оберіть інвертор для видалення")
            return

        confirm = QMessageBox.question(
            self, "Підтвердження", "Ви дійсно хочете видалити цей пристрій?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_inverter(inv_id)
            self.refresh_table()
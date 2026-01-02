from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QLabel)
from PyQt6.QtCore import Qt
from app.ui.styles import BUTTON_STYLE
from app.ui.dialogs.battery_dialog import BatteryDialog

class BatteriesView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        
        layout = QVBoxLayout()
        
        header = QLabel("Керування акумуляторами")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Додати батарею")
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

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Модель", "S/N", "Інвертор (S/N)", "Дата встан.", "Статус"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.btn_add.clicked.connect(self.add_battery)
        self.btn_edit.clicked.connect(self.edit_battery)
        self.btn_delete.clicked.connect(self.delete_battery)

        self.setLayout(layout)
        # Оновлення таблиці буде викликатись з main_window або вручну

    def showEvent(self, event):
        self.refresh_table()
        super().showEvent(event)

    def refresh_table(self):
        self.table.setRowCount(0)
        batteries = self.db_manager.get_all_batteries()
        
        for row_idx, bat in enumerate(batteries):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(bat['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(bat['battery_model'])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(bat['serial_number'])))
            
            inv_sn = bat['inverter_sn'] if bat['inverter_sn'] else "-"
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(inv_sn)))
            
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(bat['install_date'])))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(bat['status'])))

    def get_selected_id(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None
        return int(self.table.item(selected_items[0].row(), 0).text())

    def add_battery(self):
        dialog = BatteryDialog(self.db_manager, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            self.db_manager.add_battery(
                data['model_id'], data['serial_number'], data['install_date'], data['inverter_id']
            )
            self.refresh_table()

    def edit_battery(self):
        bat_id = self.get_selected_id()
        if not bat_id: return
        
        all_bats = self.db_manager.get_all_batteries()
        target = next((b for b in all_bats if b['id'] == bat_id), None)
        
        if target:
            dialog = BatteryDialog(self.db_manager, battery_data=target, parent=self)
            if dialog.exec():
                data = dialog.get_data()
                self.db_manager.update_battery(
                    bat_id, data['model_id'], data['serial_number'], data['install_date'], data['inverter_id']
                )
                self.refresh_table()

    def delete_battery(self):
        bat_id = self.get_selected_id()
        if not bat_id: return
        
        if QMessageBox.question(self, "Підтвердження", "Видалити акумулятор?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_battery(bat_id)
            self.refresh_table()
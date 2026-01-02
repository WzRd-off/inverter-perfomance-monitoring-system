from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QLabel, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from app.ui.styles import BUTTON_STYLE, LABEL_STYLE

class ErrorsView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        
        layout = QVBoxLayout()
        
        header = QLabel("Журнал збоїв та попереджень")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)

        # Панель фильтров
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фільтр:"))
        
        self.combo_filter = QComboBox()
        self.combo_filter.addItems(["Всі", "Активні (не усунені)", "Усунені"])
        self.combo_filter.currentTextChanged.connect(self.refresh_table)
        filter_layout.addWidget(self.combo_filter)
        
        filter_layout.addStretch()
        
        # Кнопка действия
        self.btn_resolve = QPushButton("Позначити як усунене")
        self.btn_resolve.setStyleSheet(BUTTON_STYLE)
        self.btn_resolve.clicked.connect(self.resolve_error)
        filter_layout.addWidget(self.btn_resolve)
        
        layout.addLayout(filter_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Час", "Інвертор", "Тип помилки", 
            "Параметр", "Значення", "Статус", "Усунено"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)
        # Автоматическое обновление при показе окна (через showEvent не всегда удобно, сделаем просто метод)

    def showEvent(self, event):
        self.refresh_table()
        super().showEvent(event)

    def refresh_table(self):
        self.table.setRowCount(0)
        
        filter_mode = None
        filter_text = self.combo_filter.currentText()
        if filter_text == "Активні (не усунені)":
            filter_mode = "Active"
        elif filter_text == "Усунені":
            filter_mode = "Resolved"
            
        errors = self.db_manager.get_all_errors(filter_mode)
        
        for row_idx, err in enumerate(errors):
            self.table.insertRow(row_idx)
            
            # ID
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(err['id'])))
            
            # Time
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(err['timestamp']).replace('T', ' ')))
            
            # Inverter
            inv_str = f"{err['inverter_name'] or 'Unknown'} ({err['inverter_sn']})"
            self.table.setItem(row_idx, 2, QTableWidgetItem(inv_str))
            
            # Type
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(err['error_type'])))
            
            # Param & Value
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(err['parameter_name'])))
            val_str = f"{err['current_value']} (Max: {err['normal_max']})"
            self.table.setItem(row_idx, 5, QTableWidgetItem(val_str))
            
            # Status (Coloring)
            status_item = QTableWidgetItem(str(err['status']))
            if err['status'] == 'Error':
                status_item.setForeground(QColor('red'))
            elif err['status'] == 'Warning':
                status_item.setForeground(QColor('orange'))
            self.table.setItem(row_idx, 6, status_item)
            
            # Resolved Date
            res_date = str(err['date_resolved']) if err['date_resolved'] else "---"
            self.table.setItem(row_idx, 7, QTableWidgetItem(res_date))

    def get_selected_id(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None
        return int(self.table.item(selected_items[0].row(), 0).text())

    def resolve_error(self):
        err_id = self.get_selected_id()
        if not err_id:
            QMessageBox.warning(self, "Увага", "Оберіть помилку зі списку")
            return
            
        # Проверяем, может она уже решена
        # (в реальном приложении можно проверить статус в БД, здесь поверим UI)
        current_status_item = self.table.item(self.table.currentRow(), 7) # Колонка "Усунено"
        if current_status_item.text() != "---":
            QMessageBox.information(self, "Інфо", "Ця помилка вже усунена.")
            return

        confirm = QMessageBox.question(
            self, "Підтвердження", 
            "Ви підтверджуєте, що проблема усунена і система перевірена?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.db_manager.resolve_error(err_id)
            self.refresh_table()
            QMessageBox.information(self, "Успіх", "Статус помилки оновлено.")
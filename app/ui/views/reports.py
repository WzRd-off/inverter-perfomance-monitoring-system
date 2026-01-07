from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, 
                             QPushButton, QDateEdit, QFrame, QMessageBox, QFileDialog)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QTextDocument
from PyQt6.QtPrintSupport import QPrinter
from app.ui.styles import BUTTON_STYLE, INPUT_STYLE
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

        card = QFrame()
        card.setStyleSheet("background-color: white; border-radius: 10px; padding: 20px;")
        form = QVBoxLayout(card)
        
        form.addWidget(QLabel("Тип звіту:"))
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Історія показників", "Журнал помилок"])
        self.combo_type.setStyleSheet(INPUT_STYLE)
        form.addWidget(self.combo_type)
        
        form.addWidget(QLabel("Формат:"))
        self.combo_format = QComboBox()
        self.combo_format.addItems(["CSV (Excel)", "PDF (Документ)"])
        self.combo_format.setStyleSheet(INPUT_STYLE)
        form.addWidget(self.combo_format)
        
        form.addWidget(QLabel("Інвертор:"))
        self.combo_inv = QComboBox()
        self.combo_inv.setStyleSheet(INPUT_STYLE)
        self._load_inverters()
        form.addWidget(self.combo_inv)
        
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
        
        btn_gen = QPushButton("Згенерувати")
        btn_gen.setStyleSheet(BUTTON_STYLE)
        btn_gen.clicked.connect(self.generate_report)
        form.addWidget(btn_gen)
        
        layout.addWidget(card)
        layout.addStretch()
        self.setLayout(layout)

    def _load_inverters(self):
        # Добавляем опцию "Всі інвертори" с data=None
        self.combo_inv.addItem("Всі інвертори", None)
        invs = self.db_manager.get_all_inverters()
        for i in invs:
            self.combo_inv.addItem(f"{i['model_name']} ({i['serial_number']})", i['id'])

    def generate_report(self):
        r_type = self.combo_type.currentText()
        r_format = self.combo_format.currentText()
        inv_id = self.combo_inv.currentData() # None если "Всі"
        d_start = self.date_start.date().toString("yyyy-MM-dd")
        d_end = self.date_end.date().toString("yyyy-MM-dd")

        data = []
        headers = []
        keys = []
        title_suffix = ""

        # 1. Збір даних
        if "Історія" in r_type:
            # Убрана проверка "if inv_id is None". 
            # Метод db_manager.get_sensor_data_by_period сам обработает None
            raw = self.db_manager.get_sensor_data_by_period(inv_id, d_start, d_end)
            data = [dict(r) for r in raw]
            
            headers = ["Інвертор (S/N)", "Час", "Вхід (Вт)", "Вихід (Вт)", "Статус"]
            keys = ["inverter_sn", "timestamp", "dc_input_power", "ac_output_power", "status"]
            
        elif "Журнал" in r_type:
            raw = self.db_manager.get_all_errors()
            # Фильтр по дате
            data = [dict(r) for r in raw if d_start <= str(r['timestamp'])[:10] <= d_end]
            # Фильтр по инвертору (если выбран конкретный)
            if inv_id is not None:
                data = [r for r in data if r['inverter_id'] == inv_id]
                
            headers = ["ID", "Час", "Інвертор", "Помилка", "Параметр", "Статус"]
            keys = ["id", "timestamp", "inverter_sn", "error_type", "parameter_name", "status"]

        if not data:
            QMessageBox.information(self, "Інфо", "Дані відсутні.")
            return

        title_suffix = " (Всі)" if inv_id is None else f" (ID: {inv_id})"

        # 2. Експорт
        if "CSV" in r_format:
            self._save_csv(data, headers, keys)
        else:
            self._save_pdf(data, headers, keys, r_type + title_suffix, f"{d_start} - {d_end}")

    def _save_csv(self, data, headers, keys):
        path, _ = QFileDialog.getSaveFileName(self, "Зберегти CSV", "", "CSV (*.csv)")
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(headers)
                    for row in data:
                        writer.writerow([row.get(k, '') for k in keys])
                QMessageBox.information(self, "Успіх", "Файл збережено.")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", str(e))

    def _save_pdf(self, data, headers, keys, title, period):
        path, _ = QFileDialog.getSaveFileName(self, "Зберегти PDF", "", "PDF (*.pdf)")
        if not path:
            return

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: #2c3e50; font-size: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 12px; }}
                th, td {{ border: 1px solid #ddd; padding: 6px; text-align: left; }}
                th {{ background-color: #2980b9; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Звіт: {title}</h1>
            <p><b>Період:</b> {period}</p>
            <p><b>Дата формування:</b> {QDate.currentDate().toString("yyyy-MM-dd")}</p>
            <table>
                <thead>
                    <tr>{''.join(f'<th>{h}</th>' for h in headers)}</tr>
                </thead>
                <tbody>
        """
        
        limit = 2000 # Лимит строк для PDF
        for i, row in enumerate(data):
            if i >= limit:
                html += f"<tr><td colspan='{len(headers)}'>... (показано перші {limit} записів) ...</td></tr>"
                break
                
            html += "<tr>"
            for k in keys:
                val = str(row.get(k, ''))
                val = val.replace('T', ' ')
                html += f"<td>{val}</td>"
            html += "</tr>"
            
        html += """
                </tbody>
            </table>
        </body>
        </html>
        """

        document = QTextDocument()
        document.setHtml(html)
        
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        
        document.print(printer)
        QMessageBox.information(self, "Успіх", "PDF збережено.")
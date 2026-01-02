from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QDateEdit, QFrame, QMessageBox)
from PyQt6.QtCore import QDate, Qt
from app.ui.styles import BUTTON_STYLE, LABEL_STYLE, INPUT_STYLE
from app.logic.calculator import Calculator
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import datetime

class StatsView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # --- Панель налаштувань ---
        settings_panel = QFrame()
        settings_panel.setStyleSheet("background-color: white; border-radius: 5px;")
        sp_layout = QHBoxLayout(settings_panel)
        
        sp_layout.addWidget(QLabel("Інвертор:"))
        self.combo_inv = QComboBox()
        self.combo_inv.setStyleSheet(INPUT_STYLE)
        # Завантаження в showEvent
        sp_layout.addWidget(self.combo_inv)
        
        sp_layout.addWidget(QLabel("З:"))
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate().addDays(-1))
        self.date_start.setStyleSheet(INPUT_STYLE)
        sp_layout.addWidget(self.date_start)
        
        sp_layout.addWidget(QLabel("По:"))
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setStyleSheet(INPUT_STYLE)
        sp_layout.addWidget(self.date_end)
        
        btn_calc = QPushButton("Розрахувати")
        btn_calc.setStyleSheet(BUTTON_STYLE)
        btn_calc.clicked.connect(self.calculate_stats)
        sp_layout.addWidget(btn_calc)
        
        sp_layout.addStretch()
        layout.addWidget(settings_panel)

        # --- Результати ---
        results_panel = QHBoxLayout()
        self.lbl_gen = self._create_card("Генерація (Wh)", "0.0")
        self.lbl_eff = self._create_card("Сер. ККД (%)", "0.0")
        self.lbl_rel = self._create_card("Надійність", "1.0")
        
        results_panel.addWidget(self.lbl_gen)
        results_panel.addWidget(self.lbl_eff)
        results_panel.addWidget(self.lbl_rel)
        layout.addLayout(results_panel)

        # --- Графіки ---
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def showEvent(self, event):
        """Оновлюємо список інверторів при відкритті вкладки"""
        self._load_inverters()
        super().showEvent(event)

    def _create_card(self, title, value):
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 5px; padding: 10px;")
        l = QVBoxLayout(frame)
        t = QLabel(title)
        t.setStyleSheet("color: gray; font-size: 12px;")
        v = QLabel(value)
        v.setStyleSheet("color: #2c3e50; font-size: 24px; font-weight: bold;")
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(t)
        l.addWidget(v)
        return frame

    def _load_inverters(self):
        current_id = self.combo_inv.currentData()
        self.combo_inv.clear()
        invs = self.db_manager.get_all_inverters()
        
        found = False
        for i in invs:
            self.combo_inv.addItem(f"{i['model_name']} ({i['serial_number']})", i['id'])
            if i['id'] == current_id:
                found = True
        
        if found:
            idx = self.combo_inv.findData(current_id)
            self.combo_inv.setCurrentIndex(idx)

    def calculate_stats(self):
        if self.combo_inv.count() == 0:
            return

        inv_id = self.combo_inv.currentData()
        d_start = self.date_start.date().toString("yyyy-MM-dd")
        d_end = self.date_end.date().toString("yyyy-MM-dd")

        data = self.db_manager.get_sensor_data_by_period(inv_id, d_start, d_end)
        errors = self.db_manager.get_errors_count_by_period(inv_id, d_start, d_end)
        
        if not data:
            QMessageBox.information(self, "Інфо", "Немає даних за цей період")
            return

        total_gen = Calculator.calculate_generation([dict(r) for r in data])
        
        eff_sum = 0
        count = 0
        eff_history = []
        timestamps = []
        
        for row in data:
            eff = Calculator.calculate_efficiency(row['ac_output_power'], row['dc_input_power'])
            eff_sum += eff
            count += 1
            timestamps.append(datetime.datetime.fromisoformat(row['timestamp']))
            eff_history.append(eff)
            
        avg_eff = eff_sum / count if count > 0 else 0
        days = self.date_start.date().daysTo(self.date_end.date()) + 1
        reliability = Calculator.calculate_reliability_index(errors, days * 24)

        self.lbl_gen.layout().itemAt(1).widget().setText(f"{total_gen:.2f}")
        self.lbl_eff.layout().itemAt(1).widget().setText(f"{avg_eff:.1f}%")
        self.lbl_rel.layout().itemAt(1).widget().setText(f"{reliability:.3f}")

        self.canvas.axes.cla()
        self.canvas.axes.plot(timestamps, eff_history, 'r-', label='ККД (%)')
        self.canvas.axes.set_title("Динаміка ККД")
        self.canvas.axes.grid(True)
        self.canvas.axes.legend()
        self.canvas.draw()


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
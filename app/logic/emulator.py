import csv
import os
from datetime import datetime

class TelemetryEmulator:
    def __init__(self, file_path: str):
        """
        Клас для емуляції отримання даних від інвертора.
        Читає CSV файл рядок за рядком.
        """
        self.file_path = file_path
        self.data = []
        self.current_index = 0
        self._load_data()

    def _load_data(self):
        """Завантажує всі дані з CSV у пам'ять"""
        if not os.path.exists(self.file_path):
            print(f"File not found: {self.file_path}")
            return

        try:
            with open(self.file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                self.data = list(reader)
        except Exception as e:
            print(f"Error reading CSV: {e}")

    def get_next_record(self):
        """
        Повертає наступний запис (словник).
        """
        if not self.data:
            return None

        record = self.data[self.current_index]
        
        # Конвертуємо типи (рядки в числа)
        processed_record = self._convert_types(record)

        # ТЗ: Формат повинен бути ISO 8601 (з літерою T).
        # Ми нічого не змінюємо, віддаємо як є в CSV.
        
        self.current_index = (self.current_index + 1) % len(self.data)
        
        return processed_record

    def _convert_types(self, record):
        """Конвертує рядкові значення з CSV у числа"""
        new_record = record.copy()
        float_fields = [
            'dc_input_power', 'ac_output_power', 'dc_voltage', 'ac_voltage', 
            'dc_current', 'ac_current', 'battery_soc', 'battery_voltage', 
            'battery_current', 'battery_temperature', 'inverter_temperature', 
            'grid_frequency'
        ]
        int_fields = ['inverter_id', 'battery_id']

        for key, value in new_record.items():
            if not value or value == 'NULL':
                new_record[key] = None
                continue
                
            try:
                if key in float_fields:
                    new_record[key] = float(value)
                elif key in int_fields:
                    new_record[key] = int(value)
            except ValueError:
                pass 
        
        return new_record
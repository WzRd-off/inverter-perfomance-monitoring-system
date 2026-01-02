class SystemAnalyzer:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        # Кеш для нормативів, щоб не смикати БД кожну секунду
        # Структура: { inverter_id: { ...norms... } }
        self._norms_cache = {}

    def check_status(self, data: dict):
        """
        Головний метод перевірки.
        Приймає поточні дані (словник), перевіряє їх на відповідність нормативам.
        Повертає список знайдених помилок (якщо є).
        """
        inverter_id = data.get('inverter_id')
        if not inverter_id:
            return []

        # 1. Отримуємо нормативи для цього інвертора
        norms = self._get_norms(inverter_id)
        if not norms:
            return [] # Немає з чим порівнювати

        errors = []

        # 2. Перевірка параметрів (Логіка з ТЗ)
        
        # Перевірка вхідної напруги PV (DC Voltage)
        if data['dc_voltage'] is not None and norms['max_pv_voltage']:
            if data['dc_voltage'] > norms['max_pv_voltage']:
                errors.append(self._create_error_record(data, 'OverVoltage', 'dc_voltage', norms['max_pv_voltage']))

        # Перевірка температури інвертора
        if data['inverter_temperature'] is not None and norms['temperature_max']:
            if data['inverter_temperature'] > norms['temperature_max']:
                errors.append(self._create_error_record(data, 'OverTemperature', 'inverter_temperature', norms['temperature_max']))

        # Перевірка вихідної потужності (Перевантаження)
        if data['ac_output_power'] is not None and norms['rated_power']:
             if data['ac_output_power'] > norms['rated_power']:
                 errors.append(self._create_error_record(data, 'OverLoad', 'ac_output_power', norms['rated_power']))

        # 3. Зберігаємо помилки в БД
        for err in errors:
            self._save_error_to_db(err)

        return errors

    def _get_norms(self, inverter_id):
        """Завантажує нормативи моделі інвертора з БД"""
        if inverter_id in self._norms_cache:
            return self._norms_cache[inverter_id]

        query = """
            SELECT m.* FROM inverters i
            JOIN model_inverters m ON i.model_id = m.id
            WHERE i.id = ?
        """
        row = self.db_manager.execute_query(query, (inverter_id,), fetch_one=True)
        
        if row:
            # Перетворюємо sqlite3.Row у словник для кешування
            self._norms_cache[inverter_id] = dict(row)
            return self._norms_cache[inverter_id]
        return None

    def _create_error_record(self, data, error_type, param_name, limit_val):
        """Формує структуру помилки"""
        return {
            'inverter_id': data['inverter_id'],
            'timestamp': data['timestamp'],
            'error_type': error_type,
            'parameter_name': param_name,
            'current_value': data[param_name],
            'normal_max': limit_val,
            'operation_mode': data.get('system_status', 'Unknown'),
            'status': 'Error'
        }

    def _save_error_to_db(self, error_data):
        """Записує помилку в таблицю Errors"""
        query = """
            INSERT INTO errors (inverter_id, timestamp, error_type, parameter_name, 
                                current_value, normal_max, operation_mode, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db_manager.execute_query(query, (
            error_data['inverter_id'],
            error_data['timestamp'],
            error_data['error_type'],
            error_data['parameter_name'],
            error_data['current_value'],
            error_data['normal_max'],
            error_data['operation_mode'],
            error_data['status']
        ))
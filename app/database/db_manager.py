import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str):
        """
        Инициализация менеджера БД.
        :param db_path: Путь к файлу базы данных (например, 'data/app_database.db')
        """
        self.db_path = db_path
        self.connection = None
        self._ensure_db_folder_exists()

    def _ensure_db_folder_exists(self):
        """Создает папку для БД, если ее нет."""
        folder = os.path.dirname(self.db_path)
        if folder and not os.path.exists(folder):
            try:
                os.makedirs(folder)
                print(f"INFO: Создана папка для БД: {folder}")
            except OSError as e:
                print(f"ERROR: Не удалось создать папку {folder}: {e}")

    def connect(self):
        """Создает подключение к БД, если его нет."""
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path)
                # Позволяет обращаться к полям по имени (row['id'])
                self.connection.row_factory = sqlite3.Row
                # Включаем поддержку внешних ключей
                self.connection.execute("PRAGMA foreign_keys = ON;")
            except sqlite3.Error as e:
                print(f"CRITICAL ERROR: Ошибка подключения к БД: {e}")

    def close(self):
        """Закрывает подключение."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_script(self, script_path: str):
        """
        Выполняет SQL-скрипт из файла (для создания таблиц).
        """
        self.connect()
        if not os.path.exists(script_path):
            print(f"ERROR: Файл схемы не найден по пути: {script_path}")
            return False
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            self.connection.executescript(sql_script)
            self.connection.commit()
            print(f"INFO: Скрипт {script_path} успешно выполнен.")
            return True
        except Exception as e:
            print(f"CRITICAL ERROR: Ошибка при выполнении SQL скрипта: {e}")
            return False

    def execute_query(self, query: str, params: tuple = (), fetch_one=False, fetch_all=False):
        """
        Универсальный метод для выполнения запросов.
        :param query: SQL запрос
        :param params: Кортеж параметров (?, ?)
        :param fetch_one: Вернуть одну строку?
        :param fetch_all: Вернуть все строки?
        :return: Результат запроса или None
        """
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                self.connection.commit()
                return cursor.lastrowid # Для INSERT возвращаем ID созданной строки
            
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
                
        except sqlite3.Error as e:
            print(f"SQL ERROR: {e}\nQuery: {query}\nParams: {params}")
            return None

    # =========================================================================
    # РАЗДЕЛ 1: INVERTERS (Инверторы)
    # =========================================================================

    def get_all_inverters(self):
        """Получить список всех инверторов с названием модели и интервалом ТО"""
        query = """
            SELECT i.*, m.model_name, m.maintenance_interval_days
            FROM inverters i
            LEFT JOIN model_inverters m ON i.model_id = m.id
            ORDER BY i.id DESC
        """
        return self.execute_query(query, fetch_all=True)

    def get_inverter_models(self):
        """Получить список всех моделей инверторов для выпадающего списка"""
        return self.execute_query("SELECT id, model_name FROM model_inverters", fetch_all=True)

    def add_inverter(self, model_id, serial_number, location, install_date):
        """Добавить новый инвертор"""
        query = """
            INSERT INTO inverters (model_id, serial_number, location, install_date, status)
            VALUES (?, ?, ?, ?, 'Offline')
        """
        return self.execute_query(query, (model_id, serial_number, location, install_date))

    def update_inverter(self, inverter_id, model_id, serial_number, location, install_date):
        """Обновить данные инвертора"""
        query = """
            UPDATE inverters 
            SET model_id=?, serial_number=?, location=?, install_date=?
            WHERE id=?
        """
        return self.execute_query(query, (model_id, serial_number, location, install_date, inverter_id))

    def delete_inverter(self, inverter_id):
        """Удалить инвертор"""
        return self.execute_query("DELETE FROM inverters WHERE id=?", (inverter_id,))

    # =========================================================================
    # РАЗДЕЛ 2: BATTERIES (Аккумуляторы)
    # =========================================================================
    
    def get_all_batteries(self):
        """Отримати список всіх батарей з назвами моделей та інверторів"""
        query = """
            SELECT b.*, m.battery_model, i.serial_number as inverter_sn
            FROM batteries b
            LEFT JOIN model_batteries m ON b.model_id = m.id
            LEFT JOIN inverters i ON b.inverter_id = i.id
            ORDER BY b.id DESC
        """
        return self.execute_query(query, fetch_all=True)

    def get_battery_models(self):
        """Получить список моделей батарей"""
        return self.execute_query("SELECT id, battery_model FROM model_batteries", fetch_all=True)

    def get_inverters_simple(self):
        """Простий список інверторів для випадаючого списку (ID + SN)"""
        return self.execute_query("SELECT id, serial_number FROM inverters", fetch_all=True)

    def add_battery(self, model_id, serial_number, install_date, inverter_id):
        """Добавить новую батарею"""
        query = """
            INSERT INTO batteries (model_id, serial_number, install_date, inverter_id, status)
            VALUES (?, ?, ?, ?, 'Normal')
        """
        return self.execute_query(query, (model_id, serial_number, install_date, inverter_id))

    def update_battery(self, battery_id, model_id, serial_number, install_date, inverter_id):
        """Обновить данные батареи"""
        query = """
            UPDATE batteries 
            SET model_id=?, serial_number=?, install_date=?, inverter_id=?
            WHERE id=?
        """
        return self.execute_query(query, (model_id, serial_number, install_date, inverter_id, battery_id))

    def delete_battery(self, battery_id):
        """Удалить батарею"""
        return self.execute_query("DELETE FROM batteries WHERE id=?", (battery_id,))

    # =========================================================================
    # РАЗДЕЛ 3: ERRORS LOG (Журнал сбоев)
    # =========================================================================

    def get_all_errors(self, status_filter=None):
        """
        Отримати список помилок.
        status_filter: 'Active' (показувати тільки не вирішені), 'Resolved', або None (всі)
        """
        base_query = """
            SELECT e.*, i.serial_number as inverter_sn, i.name as inverter_name
            FROM errors e
            LEFT JOIN inverters i ON e.inverter_id = i.id
        """
        
        if status_filter == 'Active':
            # Активні - це ті, у яких немає дати вирішення (NULL)
            query = base_query + " WHERE e.date_resolved IS NULL ORDER BY e.timestamp DESC"
            return self.execute_query(query, fetch_all=True)
        elif status_filter == 'Resolved':
            query = base_query + " WHERE e.date_resolved IS NOT NULL ORDER BY e.timestamp DESC"
            return self.execute_query(query, fetch_all=True)
        else:
            # Всі
            query = base_query + " ORDER BY e.timestamp DESC"
            return self.execute_query(query, fetch_all=True)

    def resolve_error(self, error_id):
        """Позначити помилку як вирішену (встановити поточну дату)"""
        query = """
            UPDATE errors 
            SET date_resolved = CURRENT_TIMESTAMP, status = 'Resolved'
            WHERE id = ?
        """
        return self.execute_query(query, (error_id,))

    # =========================================================================
    # РАЗДЕЛ 4: MONITORING & STATISTICS (Мониторинг и Статистика)
    # =========================================================================
    
    def save_sensor_data(self, data):
        """Збереження поточних показників у БД"""
        query = """
            INSERT INTO sensor_values (
                inverter_id, timestamp, 
                pv_voltage, pv_current, pv_power,
                output_voltage, output_current, output_power,
                battery_voltage, battery_current, battery_soc,
                temperature, grid_frequency, operation_mode, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data.get('inverter_id'),
            data.get('timestamp'),
            data.get('dc_voltage'),      
            data.get('dc_current'),      
            data.get('dc_input_power'),  
            data.get('ac_voltage'),      
            data.get('ac_current'),      
            data.get('ac_output_power'), 
            data.get('battery_voltage'),
            data.get('battery_current'),
            data.get('battery_soc'),
            data.get('inverter_temperature'),
            data.get('grid_frequency'),
            data.get('system_status'),   
            'Normal'
        )
        self.execute_query(query, params)

    def get_sensor_data_by_period(self, inverter_id, start_date, end_date):
        """Отримати показники сенсорів за вказаний період"""
        start_ts = f"{start_date}T00:00:00"
        end_ts = f"{end_date}T23:59:59"
        
        query = """
            SELECT timestamp, pv_power as dc_input_power, output_power as ac_output_power, status
            FROM sensor_values
            WHERE inverter_id = ? 
            AND timestamp >= ? 
            AND timestamp <= ?
            ORDER BY timestamp ASC
        """
        return self.execute_query(query, (inverter_id, start_ts, end_ts), fetch_all=True)

    def get_errors_count_by_period(self, inverter_id, start_date, end_date):
        """Отримати кількість помилок за період"""
        start_ts = f"{start_date}T00:00:00"
        end_ts = f"{end_date}T23:59:59"
        
        query = """
            SELECT COUNT(*) as error_count
            FROM errors
            WHERE inverter_id = ? AND status = 'Error' 
            AND timestamp >= ? AND timestamp <= ?
        """
        res = self.execute_query(query, (inverter_id, start_ts, end_ts), fetch_one=True)
        return res['error_count'] if res else 0

    # =========================================================================
    # РАЗДЕЛ 5: PROFILE & AUTH (Профиль и Авторизация)
    # =========================================================================

    def get_user_by_id(self, user_id):
        """Получить данные пользователя по ID"""
        return self.execute_query("SELECT * FROM users WHERE id=?", (user_id,), fetch_one=True)

    def update_user_profile(self, user_id, full_name, email, phone):
        """Обновить профиль пользователя"""
        query = "UPDATE users SET full_name=?, email=?, phone=? WHERE id=?"
        return self.execute_query(query, (full_name, email, phone, user_id))

    def check_password(self, user_id, password_hash):
        """Проверить текущий пароль (хеш)"""
        res = self.execute_query("SELECT id FROM users WHERE id=? AND password_hash=?", (user_id, password_hash), fetch_one=True)
        return res is not None

    def change_password(self, user_id, new_hash):
        """Изменить пароль пользователя"""
        return self.execute_query("UPDATE users SET password_hash=? WHERE id=?", (new_hash, user_id))

    # =========================================================================
    # РАЗДЕЛ 6: DASHBOARD & ANALYTICS (Дашборд и Прогнозы)
    # =========================================================================

    def get_dashboard_stats(self):
        """Збирає всі лічильники для дашборда"""
        stats = {}
        # 1. Загальна кількість
        res = self.execute_query("SELECT COUNT(*) as cnt FROM inverters", fetch_one=True)
        stats['inverters_total'] = res['cnt'] if res else 0

        # 2. Активні (де статус не 'Offline')
        res = self.execute_query("SELECT COUNT(*) as cnt FROM inverters WHERE status != 'Offline'", fetch_one=True)
        stats['inverters_active'] = res['cnt'] if res else 0

        # 3. Активні аварії
        res = self.execute_query("SELECT COUNT(*) as cnt FROM errors WHERE date_resolved IS NULL", fetch_one=True)
        stats['active_errors'] = res['cnt'] if res else 0

        # 4. Прострочене ТО (Predictive Maintenance Logic)
        # Вибираємо інвертори, де (дата встановлення + інтервал) < сьогодні
        # SQLite: date(install_date, '+' || maintenance_interval_days || ' days') < date('now')
        query_maint = """
            SELECT COUNT(*) as cnt 
            FROM inverters i
            JOIN model_inverters m ON i.model_id = m.id
            WHERE date(i.install_date, '+' || m.maintenance_interval_days || ' days') < date('now')
        """
        res = self.execute_query(query_maint, fetch_one=True)
        stats['maintenance_overdue'] = res['cnt'] if res else 0

        # 5. Всього батарей
        res = self.execute_query("SELECT COUNT(*) as cnt FROM batteries", fetch_one=True)
        stats['batteries_total'] = res['cnt'] if res else 0

        return stats

    def get_maintenance_forecast(self):
        """
        Повертає список інверторів з прогнозом ТО.
        Для таблиці прогнозування.
        """
        query = """
            SELECT 
                i.serial_number, 
                m.model_name,
                i.install_date,
                m.maintenance_interval_days,
                date(i.install_date, '+' || m.maintenance_interval_days || ' days') as next_service_date,
                (julianday(date(i.install_date, '+' || m.maintenance_interval_days || ' days')) - julianday('now')) as days_left
            FROM inverters i
            JOIN model_inverters m ON i.model_id = m.id
            ORDER BY days_left ASC
        """
        return self.execute_query(query, fetch_all=True)
import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self._ensure_db_folder_exists()

    def _ensure_db_folder_exists(self):
        folder = os.path.dirname(self.db_path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)

    def connect(self):
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path)
                self.connection.row_factory = sqlite3.Row
                self.connection.execute("PRAGMA foreign_keys = ON;")
            except sqlite3.Error as e:
                print(f"Ошибка подключения к БД: {e}")

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_script(self, script_path: str):
        self.connect()
        if not os.path.exists(script_path):
            return False
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            self.connection.executescript(sql_script)
            self.connection.commit()
            return True
        except Exception:
            return False

    def execute_query(self, query: str, params: tuple = (), fetch_one=False, fetch_all=False):
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                self.connection.commit()
                return cursor.lastrowid
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"SQL Error: {e}")
            return None

    # --- INVERTERS CRUD ---
    def get_all_inverters(self):
        query = """
            SELECT i.*, m.model_name 
            FROM inverters i
            LEFT JOIN model_inverters m ON i.model_id = m.id
            ORDER BY i.id DESC
        """
        return self.execute_query(query, fetch_all=True)

    def get_inverter_models(self):
        return self.execute_query("SELECT id, model_name FROM model_inverters", fetch_all=True)

    def add_inverter(self, model_id, serial_number, location, install_date):
        query = """
            INSERT INTO inverters (model_id, serial_number, location, install_date, status)
            VALUES (?, ?, ?, ?, 'Offline')
        """
        return self.execute_query(query, (model_id, serial_number, location, install_date))

    def update_inverter(self, inverter_id, model_id, serial_number, location, install_date):
        query = """
            UPDATE inverters 
            SET model_id=?, serial_number=?, location=?, install_date=?
            WHERE id=?
        """
        return self.execute_query(query, (model_id, serial_number, location, install_date, inverter_id))

    def delete_inverter(self, inverter_id):
        return self.execute_query("DELETE FROM inverters WHERE id=?", (inverter_id,))

    # --- STATISTICS & MONITORING METHODS ---
    
    def save_sensor_data(self, data):
        """
        Збереження поточних показників у БД.
        Зберігаємо timestamp як є (з літерою T), згідно ТЗ.
        """
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
            data.get('timestamp'), # Зберігаємо з T
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
        """
        Отримати показники сенсорів за вказаний період.
        Формат пошуку: ISO 8601 (з літерою T).
        start_date: 'YYYY-MM-DD'
        end_date: 'YYYY-MM-DD'
        """
        # Формуємо ISO рядки для пошуку
        start_ts = f"{start_date}T00:00:00"
        end_ts = f"{end_date}T23:59:59"
        
        # Аліаси (as) обов'язкові, щоб Calculator зрозумів імена полів
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
        """Отримати кількість помилок за період (з T)"""
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
import sqlite3
import os
from datetime import datetime, date

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self._ensure_db_folder_exists()

    def _ensure_db_folder_exists(self):
        folder = os.path.dirname(self.db_path)
        if folder and not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except OSError as e:
                print(f"ERROR: Не удалось создать папку {folder}: {e}")

    def connect(self):
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
                self.connection.execute("PRAGMA foreign_keys = ON;")
            except sqlite3.Error as e:
                print(f"CRITICAL ERROR: Ошибка подключения к БД: {e}")

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
        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
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
            print(f"SQL ERROR: {e}\nQuery: {query}")
            return None

    # --- INVERTERS ---
    def get_all_inverters(self):
        query = """
            SELECT i.*, m.model_name, m.maintenance_interval_days
            FROM inverters i
            LEFT JOIN model_inverters m ON i.model_id = m.id
            ORDER BY i.id ASC
        """
        return self.execute_query(query, fetch_all=True)

    def get_inverter_models(self):
        return self.execute_query("SELECT id, model_name FROM model_inverters", fetch_all=True)

    def add_inverter(self, model_id, serial_number, location, install_date):
        query = "INSERT INTO inverters (model_id, serial_number, location, install_date, status) VALUES (?, ?, ?, ?, 'Offline')"
        return self.execute_query(query, (model_id, serial_number, location, install_date))

    def update_inverter(self, inverter_id, model_id, serial_number, location, install_date):
        query = "UPDATE inverters SET model_id=?, serial_number=?, location=?, install_date=? WHERE id=?"
        return self.execute_query(query, (model_id, serial_number, location, install_date, inverter_id))

    def delete_inverter(self, inverter_id):
        return self.execute_query("DELETE FROM inverters WHERE id=?", (inverter_id,))

    # --- BATTERIES ---
    def get_all_batteries(self):
        query = """
            SELECT b.*, m.battery_model, i.serial_number as inverter_sn
            FROM batteries b
            LEFT JOIN model_batteries m ON b.model_id = m.id
            LEFT JOIN inverters i ON b.inverter_id = i.id
            ORDER BY b.id ASC
        """
        return self.execute_query(query, fetch_all=True)

    def get_battery_models(self):
        return self.execute_query("SELECT id, battery_model FROM model_batteries", fetch_all=True)

    def get_inverters_simple(self):
        return self.execute_query("SELECT id, serial_number FROM inverters", fetch_all=True)

    def add_battery(self, model_id, serial_number, install_date, inverter_id):
        query = "INSERT INTO batteries (model_id, serial_number, install_date, inverter_id, status) VALUES (?, ?, ?, ?, 'Normal')"
        return self.execute_query(query, (model_id, serial_number, install_date, inverter_id))

    def update_battery(self, battery_id, model_id, serial_number, install_date, inverter_id):
        query = "UPDATE batteries SET model_id=?, serial_number=?, install_date=?, inverter_id=? WHERE id=?"
        return self.execute_query(query, (model_id, serial_number, install_date, inverter_id, battery_id))

    def delete_battery(self, battery_id):
        return self.execute_query("DELETE FROM batteries WHERE id=?", (battery_id,))

    # --- ERRORS ---
    def get_all_errors(self, status_filter=None):
        base_query = """
            SELECT e.*, i.serial_number as inverter_sn, i.name as inverter_name
            FROM errors e
            LEFT JOIN inverters i ON e.inverter_id = i.id
        """
        if status_filter == 'Active':
            query = base_query + " WHERE e.date_resolved IS NULL ORDER BY e.timestamp DESC"
            return self.execute_query(query, fetch_all=True)
        elif status_filter == 'Resolved':
            query = base_query + " WHERE e.date_resolved IS NOT NULL ORDER BY e.timestamp DESC"
            return self.execute_query(query, fetch_all=True)
        else:
            query = base_query + " ORDER BY e.timestamp DESC"
            return self.execute_query(query, fetch_all=True)

    def resolve_error(self, error_id):
        query = "UPDATE errors SET date_resolved = CURRENT_TIMESTAMP, status = 'Resolved' WHERE id = ?"
        return self.execute_query(query, (error_id,))

    # --- SENSOR DATA & STATS ---
    def save_sensor_data(self, data):
        query = """
            INSERT INTO sensor_values (
                inverter_id, timestamp, 
                pv_voltage, pv_current, pv_power,
                output_voltage, output_current, output_power,
                battery_voltage, battery_current, battery_soc,
                temperature, grid_frequency, operation_mode, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        status = data.get('system_status', 'Unknown')
        inv_id = data.get('inverter_id')
        if inv_id:
            self.execute_query("UPDATE inverters SET status = ? WHERE id = ?", (status, inv_id))

        params = (
            inv_id,
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
            status,   
            'Normal'
        )
        self.execute_query(query, params)

    def get_sensor_data_by_period(self, inverter_id, start_date, end_date):
        """
        Если inverter_id == None, возвращает данные по ВСЕМ инверторам.
        ВАЖНО: Добавлены алиасы (AS) для совместимости с Calculator (ac_output_power, dc_input_power).
        """
        start_ts = f"{start_date}T00:00:00"
        end_ts = f"{end_date}T23:59:59"
        
        # Общая часть SELECT с правильными алиасами для совместимости с Calculator
        select_clause = """
            SELECT 
                sv.*, 
                sv.output_power as ac_output_power,
                sv.pv_power as dc_input_power,
                i.serial_number as inverter_sn 
            FROM sensor_values sv
            JOIN inverters i ON sv.inverter_id = i.id
        """

        if inverter_id:
            query = f"""
                {select_clause}
                WHERE sv.inverter_id = ? 
                AND sv.timestamp >= ? AND sv.timestamp <= ?
                ORDER BY sv.timestamp ASC
            """
            return self.execute_query(query, (inverter_id, start_ts, end_ts), fetch_all=True)
        else:
            query = f"""
                {select_clause}
                WHERE sv.timestamp >= ? AND sv.timestamp <= ?
                ORDER BY i.id ASC, sv.timestamp ASC
            """
            return self.execute_query(query, (start_ts, end_ts), fetch_all=True)

    def get_errors_count_by_period(self, inverter_id, start_date, end_date):
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

    # --- DASHBOARD LOGIC ---
    def get_dashboard_aggregated_stats(self):
        today = date.today().isoformat()
        stats = {}

        # 1. Counts
        res_inv = self.execute_query("SELECT COUNT(*) as cnt FROM inverters", fetch_one=True)
        stats['inverters_total'] = res_inv['cnt'] if res_inv else 0
        
        res_bat = self.execute_query("SELECT COUNT(*) as cnt FROM batteries", fetch_one=True)
        stats['batteries_total'] = res_bat['cnt'] if res_bat else 0
        
        res_err = self.execute_query("SELECT COUNT(*) as cnt FROM errors WHERE date_resolved IS NULL", fetch_one=True)
        stats['active_errors'] = res_err['cnt'] if res_err else 0

        # 2. Daily Generation & Avg Efficiency
        start_ts = f"{today}T00:00:00"
        end_ts = f"{today}T23:59:59"
        
        query_data = """
            SELECT pv_power, output_power, timestamp 
            FROM sensor_values 
            WHERE timestamp >= ? AND timestamp <= ?
        """
        rows = self.execute_query(query_data, (start_ts, end_ts), fetch_all=True)
        
        from app.logic.calculator import Calculator
        
        total_gen = 0.0
        eff_sum = 0.0
        eff_count = 0
        
        for r in rows:
            pac = r['output_power'] or 0
            pdc = r['pv_power'] or 0
            eff = Calculator.calculate_efficiency(pac, pdc)
            if eff > 0:
                eff_sum += eff
                eff_count += 1
        
        stats['avg_efficiency'] = (eff_sum / eff_count) if eff_count > 0 else 0.0

        inverters = self.execute_query("SELECT id FROM inverters", fetch_all=True)
        for inv in inverters:
            inv_id = inv['id']
            inv_data_query = """
                SELECT timestamp, output_power as ac_output_power 
                FROM sensor_values 
                WHERE inverter_id = ? AND timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp ASC
            """
            inv_rows = self.execute_query(inv_data_query, (inv_id, start_ts, end_ts), fetch_all=True)
            records = [dict(r) for r in inv_rows]
            total_gen += Calculator.calculate_generation(records)
            
        stats['daily_generation_wh'] = total_gen
        
        return stats

    def get_inverters_status_list(self):
        query = """
            SELECT i.id, i.serial_number, m.model_name, i.status 
            FROM inverters i
            LEFT JOIN model_inverters m ON i.model_id = m.id
            ORDER BY i.id ASC
        """
        return self.execute_query(query, fetch_all=True)

    # --- FORECASTING ---
    def get_maintenance_forecast(self):
        """Прогноз ТО на основе интервала обслуживания"""
        query = """
            SELECT 
                'ТО' as type,
                i.serial_number, 
                m.model_name,
                i.install_date,
                date(i.install_date, '+' || m.maintenance_interval_days || ' days') as target_date,
                (julianday(date(i.install_date, '+' || m.maintenance_interval_days || ' days')) - julianday('now')) as days_left
            FROM inverters i
            JOIN model_inverters m ON i.model_id = m.id
            WHERE days_left < 30 
            ORDER BY days_left ASC
        """
        return self.execute_query(query, fetch_all=True)
    
    def get_replacement_forecast(self):
        """Прогноз замены на основе recommended_replacement_years"""
        # Инверторы
        q_inv = """
            SELECT 
                'Заміна (Інвертор)' as type,
                i.serial_number, 
                m.model_name,
                i.install_date,
                date(i.install_date, '+' || m.recommended_replacement_years || ' years') as target_date,
                (julianday(date(i.install_date, '+' || m.recommended_replacement_years || ' years')) - julianday('now')) as days_left
            FROM inverters i
            JOIN model_inverters m ON i.model_id = m.id
            WHERE days_left < 365 
        """
        
        # Батареи
        q_bat = """
            SELECT 
                'Заміна (АКБ)' as type,
                b.serial_number, 
                m.battery_model as model_name,
                b.install_date,
                date(b.install_date, '+' || m.recommended_replacement_years || ' years') as target_date,
                (julianday(date(b.install_date, '+' || m.recommended_replacement_years || ' years')) - julianday('now')) as days_left
            FROM batteries b
            JOIN model_batteries m ON b.model_id = m.id
            WHERE days_left < 365 
        """
        
        query = f"{q_inv} UNION ALL {q_bat} ORDER BY days_left ASC"
        return self.execute_query(query, fetch_all=True)

    def get_full_forecast_report(self):
        maint = self.get_maintenance_forecast()
        repl = self.get_replacement_forecast()
        return maint + repl

    # --- USER ---
    def get_user_by_id(self, user_id):
        return self.execute_query("SELECT * FROM users WHERE id=?", (user_id,), fetch_one=True)

    def update_user_profile(self, user_id, full_name, email, phone):
        query = "UPDATE users SET full_name=?, email=?, phone=? WHERE id=?"
        return self.execute_query(query, (full_name, email, phone, user_id))

    def check_password(self, user_id, password_hash):
        res = self.execute_query("SELECT id FROM users WHERE id=? AND password_hash=?", (user_id, password_hash), fetch_one=True)
        return res is not None

    def change_password(self, user_id, new_hash):
        return self.execute_query("UPDATE users SET password_hash=? WHERE id=?", (new_hash, user_id))
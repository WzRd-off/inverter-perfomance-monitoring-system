PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS model_inverters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    rated_power REAL,
    max_pv_voltage REAL,
    max_pv_current REAL,
    max_battery_current REAL,
    max_grid_power REAL,
    temperature_min REAL,
    temperature_max REAL,
    warranty_months INTEGER,
    maintenance_interval_days INTEGER,
    recommended_replacement_years INTEGER
);

CREATE TABLE IF NOT EXISTS model_batteries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    battery_model TEXT NOT NULL,
    battery_type TEXT,
    nominal_voltage REAL,
    nominal_capacity REAL,
    max_charge_current REAL,
    max_battery_current REAL,
    max_discharge_current REAL,
    nominal_cycles INTEGER,
    temperature_min REAL,
    temperature_max REAL,
    warranty_months INTEGER,
    recommended_replacement_years INTEGER
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email TEXT,
    is_admin INTEGER DEFAULT 0, -- 0 = User, 1 = Admin
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_login TEXT,
    full_name TEXT,
    phone TEXT
);

CREATE TABLE IF NOT EXISTS inverters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    name TEXT,
    serial_number TEXT UNIQUE,
    install_date TEXT,
    location TEXT,
    connection_type TEXT,
    ip_address TEXT,
    status TEXT DEFAULT 'Offline',
    last_maintenance_date TEXT,
    notes TEXT,
    FOREIGN KEY (model_id) REFERENCES model_inverters(id)
);

CREATE TABLE IF NOT EXISTS batteries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    serial_number TEXT UNIQUE,
    install_date TEXT,
    inverter_id INTEGER, -- Может быть NULL, если не подключен
    current_cycles INTEGER DEFAULT 0,
    last_maintenance_date TEXT,
    status TEXT DEFAULT 'Normal',
    notes TEXT,
    user_id INTEGER,
    FOREIGN KEY (model_id) REFERENCES model_batteries(id),
    FOREIGN KEY (inverter_id) REFERENCES inverters(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS sensor_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inverter_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    pv_voltage REAL,
    pv_current REAL,
    pv_power REAL,
    output_voltage REAL,
    output_current REAL,
    output_power REAL,
    battery_voltage REAL,
    battery_current REAL,
    battery_soc REAL,
    temperature REAL,
    grid_frequency REAL,
    operation_mode TEXT,
    status TEXT,
    FOREIGN KEY (inverter_id) REFERENCES inverters(id)
);

CREATE TABLE IF NOT EXISTS errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inverter_id INTEGER NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    error_type TEXT,
    parameter_name TEXT,
    current_value REAL,
    normal_min REAL,
    normal_max REAL,
    operation_mode TEXT,
    status TEXT, -- Warning / Error
    date_resolved TEXT,
    FOREIGN KEY (inverter_id) REFERENCES inverters(id)
);

-- Добавляем дефолтного администратора (пароль 'admin')
-- ПРИМЕЧАНИЕ: В реальном проекте хеш должен генерироваться через hashlib/bcrypt
INSERT OR IGNORE INTO users (username, password_hash, is_admin, full_name) 
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 1, 'System Administrator');

-- Добавляем модели инверторов (Чтобы было что выбирать в списке)
INSERT OR IGNORE INTO model_inverters (model_name, rated_power, max_pv_voltage, temperature_max, warranty_months)
VALUES 
('SUN-5K-SG03LP1', 5000, 500, 60, 60),
('DEYE-8K-SG01LP1', 8000, 550, 65, 120),
('Huawei SUN2000-10KTL', 10000, 1000, 60, 120);

-- Добавляем модели аккумуляторов
INSERT OR IGNORE INTO model_batteries (battery_model, nominal_voltage, nominal_capacity)
VALUES 
('Pylontech US3000C', 48, 74),
('Deye SE-G5.1 Pro', 51.2, 100);
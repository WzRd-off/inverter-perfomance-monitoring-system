import hashlib

class AuthService:
    def __init__(self, db_manager):
        self.db = db_manager

    def hash_password(self, password: str) -> str:
        """Хеширует пароль (SHA-256)"""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate(self, username, password):
        """
        Проверяет логин и пароль.
        Возвращает данные пользователя (dict) если успешно, иначе None.
        """
        password_hash = self.hash_password(password)
        
        query = "SELECT * FROM users WHERE username = ? AND password_hash = ?"
        user = self.db.execute_query(query, (username, password_hash), fetch_one=True)
        
        if user:
            # Обновляем время последнего входа
            update_query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
            self.db.execute_query(update_query, (user['id'],))
            return dict(user) # Превращаем sqlite3.Row в обычный словарь
        
        return None
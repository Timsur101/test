import mysql.connector
from mysql.connector import Error

class DB:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",  # Замените на ваше имя пользователя MySQL
                password="password",  # Замените на ваш пароль MySQL
                database="app"
            )
            if self.connection.is_connected():
                print("Подключено к базе данных MySQL")
        except Error as e:
            print(f"Ошибка подключения к MySQL: {e}")
            self.connection = None

    def get_cursor(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()
            if not self.connection or not self.connection.is_connected():
                raise Exception("Не удалось установить подключение к базе данных")
        return self.connection.cursor()

    def check_user_exists(self, login, email):
        """Проверяет, существует ли пользователь с указанным логином или email."""
        try:
            cursor = self.get_cursor()
            query = "SELECT id FROM users WHERE login = %s OR email = %s"
            cursor.execute(query, (login, email))
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Error as e:
            print(f"Ошибка проверки пользователя: {e}")
            return False

    def register_user(self, login, email, password):
        """Регистрирует нового пользователя."""
        try:
            cursor = self.get_cursor()
            query = "INSERT INTO users (login, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (login, email, password))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Ошибка регистрации пользователя: {e}")
            return False

    def get_categories(self):
        try:
            cursor = self.get_cursor()
            cursor.execute("SELECT id, name FROM categories")
            categories = cursor.fetchall()
            cursor.close()
            return categories
        except Error as e:
            print(f"Ошибка получения категорий: {e}")
            return []

    def search(self, product="", category=""):
        try:
            cursor = self.get_cursor()
            query = """
                SELECT b.id, b.product, b.price, b.comment, c.name, b.date
                FROM buy b
                LEFT JOIN categories c ON b.category_id = c.id
                WHERE b.product LIKE %s
            """
            params = (f"%{product}%",)
            if category:
                query += " AND c.name = %s"
                params = (f"%{product}%", category)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except Error as e:
            print(f"Ошибка поиска записей: {e}")
            return []

    def insert(self, product, price, comment, category_id, date):
        try:
            cursor = self.get_cursor()
            query = """
                INSERT INTO buy (product, price, comment, category_id, date)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (product, float(price), comment, category_id, date))
            self.connection.commit()
            cursor.close()
        except Error as e:
            print(f"Ошибка добавления записи: {e}")

    def update(self, id, product, price, comment, category_id, date):
        try:
            cursor = self.get_cursor()
            query = """
                UPDATE buy
                SET product = %s, price = %s, comment = %s, category_id = %s, date = %s
                WHERE id = %s
            """
            cursor.execute(query, (product, float(price), comment, category_id, date, id))
            self.connection.commit()
            cursor.close()
        except Error as e:
            print(f"Ошибка обновления записи: {e}")

    def delete(self, id):
        try:
            cursor = self.get_cursor()
            cursor.execute("DELETE FROM buy WHERE id = %s", (id,))
            self.connection.commit()
            cursor.close()
        except Error as e:
            print(f"Ошибка удаления записи: {e}")

    def get_total_spent(self):
        try:
            cursor = self.get_cursor()
            cursor.execute("SELECT SUM(price) FROM buy")
            total = cursor.fetchone()[0] or 0.0
            cursor.close()
            return float(total)
        except Error as e:
            print(f"Ошибка подсчета общей суммы: {e}")
            return 0.0

    def get_top_category(self):
        try:
            cursor = self.get_cursor()
            query = """
                SELECT c.name, SUM(b.price)
                FROM buy b
                LEFT JOIN categories c ON b.category_id = c.id
                GROUP BY c.name
                ORDER BY SUM(b.price) DESC
                LIMIT 1
            """
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            if result:
                return result[0] or "Нет данных", result[1] or 0.0
            return "Нет данных", 0.0
        except Error as e:
            print(f"Ошибка получения топ-категории: {e}")
            return "Нет данных", 0.0

    def __del__(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Подключение к MySQL закрыто")
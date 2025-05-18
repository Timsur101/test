import sqlite3
from datetime import datetime
from functools import wraps

def singleton(cls):
    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper

@singleton
class DB:
    def __init__(self):
        self.db_file = "mybooks.db"
        self._create_table()

    def _create_table(self):
        conn = self._get_connection()
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS categories ("
                "id INTEGER PRIMARY KEY, "
                "name TEXT UNIQUE)"
            )

            conn.execute(
                "CREATE TABLE IF NOT EXISTS buy ("
                "id INTEGER PRIMARY KEY, "
                "product TEXT, "
                "price TEXT, "
                "comment TEXT, "
                "category_id INTEGER, "
                "date TEXT, "
                "FOREIGN KEY(category_id) REFERENCES categories(id))"
            )

            conn.execute(
                "INSERT OR IGNORE INTO categories (name) VALUES "
                "('Продукты'), ('Транспорт'), ('Жилье'), ('Развлечения'), ('Другое')"
            )
            conn.commit()
        finally:
            conn.close()

    def _get_connection(self):
        return sqlite3.connect(self.db_file)

    def view(self):
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT buy.id, buy.product, buy.price, buy.comment, "
                "COALESCE(categories.name, 'Без категории') as category, "
                "buy.date "
                "FROM buy LEFT JOIN categories ON buy.category_id = categories.id"
            )
            return cur.fetchall()
        finally:
            conn.close()

    def get_categories(self):
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM categories")
            return cur.fetchall()
        finally:
            conn.close()

    def insert(self, product, price, comment, category_id, date):
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT INTO buy VALUES (NULL,?,?,?,?,?)",
                (product, price, comment, category_id, date)
            )
            conn.commit()
        finally:
            conn.close()

    def update(self, id, product, price, comment, category_id, date):
        conn = self._get_connection()
        try:
            conn.execute(
                "UPDATE buy SET product=?, price=?, comment=?, category_id=?, date=? WHERE id=?",
                (product, price, comment, category_id, date, id)
            )
            conn.commit()
        finally:
            conn.close()

    def delete(self, id):
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM buy WHERE id=?", (id,))
            conn.commit()
        finally:
            conn.close()

    def search(self, product="", category=""):
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            query = """
                SELECT buy.id, buy.product, buy.price, buy.comment, 
                       categories.name as category, buy.date
                FROM buy LEFT JOIN categories ON buy.category_id = categories.id
                WHERE buy.product LIKE ? 
                AND (categories.name LIKE ? OR ? = '')
            """
            cur.execute(query, (f"%{product}%", f"%{category}%", category))
            return cur.fetchall()
        finally:
            conn.close()

    def get_total_spent(self):
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT SUM(CAST(price AS REAL)) FROM buy")
            result = cur.fetchone()[0]
            return result if result else 0
        finally:
            conn.close()

    def get_top_category(self):
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT categories.name, SUM(CAST(buy.price AS REAL)) as total
                FROM buy LEFT JOIN categories ON buy.category_id = categories.id
                GROUP BY categories.name
                ORDER BY total DESC
                LIMIT 1
            """)
            result = cur.fetchone()
            return result if result else ("Нет данных", 0)
        finally:
            conn.close()

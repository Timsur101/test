import sqlite3
import flet as ft
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
                "date TEXT, "  # Добавляем поле для даты
                "FOREIGN KEY(category_id) REFERENCES categories(id))"
            )

            conn.execute(
                "INSERT OR IGNORE INTO categories (name) VALUES "
                "('Продукты'), ('Транспорт'), ('Жилье'), ('Развлечения'), ('Другое')"
            )
            conn.execute(
                "UPDATE buy SET category_id = (SELECT id FROM categories WHERE name = 'Другое') "
                "WHERE category_id IS NULL"
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


def main(page: ft.Page):
    primary_color = "#FFEE93"
    secondary_color = "#F4D35E"
    background_color = "#FFF9E6"
    card_color = "#FFFDF6"
    text_color = "#5E503F"
    accent_color = "#F7C548"

    page.title = "Бюджет 0.3 (с датами)"
    page.window_width = 800
    page.window_height = 600
    page.bgcolor = background_color
    page.padding = 20

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=secondary_color,  # Основной акцент (#F4D35E)
            on_primary=text_color,  # Цвет текста на акцентном фоне (#5E503F)
            surface=background_color,  # Фон (#FFF9E6)
            tertiary=accent_color,
        ),

    )

    db = DB()


    selected_tuple = None
    categories = db.get_categories()
    selected_date = None

    # Поля ввода
    product_text = ft.TextField(
        label="Название",
        border_color=secondary_color,
        filled=True,
        bgcolor=card_color,
        color=text_color,
        expand=True,
        label_style=ft.TextStyle(color=text_color))

    price_text = ft.TextField(
        label="Стоимость",
        border_color=secondary_color,
        filled=True,
        bgcolor=card_color,
        color=text_color,
        width=150,
        label_style=ft.TextStyle(color=text_color),
        keyboard_type=ft.KeyboardType.NUMBER)

    comment_text = ft.TextField(
        label="Комментарий",
        border_color=secondary_color,
        filled=True,
        bgcolor=card_color,
        color=text_color,
        expand=True,
        multiline=True,
        min_lines=1,
        max_lines=3,
        label_style=ft.TextStyle(color=text_color))

    # Поле для отображения выбранной даты
    date_text = ft.Text(
        "Дата не выбрана",
        size=14,
        color=text_color)

    # Функция для обработки выбора даты
    def handle_date_change(e):
        nonlocal selected_date
        selected_date = e.control.value
        date_text.value = selected_date.strftime("%d.%m.%Y")
        page.update()

    # Функция для открытия DatePicker
    def open_date_picker(e):
        date_picker = ft.DatePicker(
            first_date=datetime(2000, 1, 1),
            last_date=datetime(2030, 12, 31),
            on_change=handle_date_change,

        )

        page.open(date_picker)



    # Кнопка выбора даты
    date_button = ft.ElevatedButton(
        "Выбрать дату",
        icon=ft.Icons.CALENDAR_MONTH,
        style=ft.ButtonStyle(
            bgcolor=primary_color,
            color=text_color,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=open_date_picker)

    # Выпадающий список категорий
    category_dropdown = ft.Dropdown(
        hint_text="Выберите категорию для фильтрации",
        label="Категория",
        options=[ft.dropdown.Option("Все категории")] + [ft.dropdown.Option(cat[1]) for cat in categories],
        border_color=secondary_color,
        filled=False,
        fill_color=card_color,
        bgcolor="#FFFDF6",
        color=text_color,
        label_style=ft.TextStyle(color=text_color),
        expand=True,
        on_change=lambda e: search_command(e)
    )

    # Виджет статистики
    stats_text = ft.Text(
        "Статистика: загрузка...",
        size=14,
        color=text_color,
        weight=ft.FontWeight.BOLD)

    list_view = ft.ListView(expand=True, spacing=5)
    list_container = ft.Container(
        content=list_view,
        bgcolor=card_color,
        border_radius=10,
        padding=10,
        border=ft.border.all(1, secondary_color),
        expand=True)

    button_style = ft.ButtonStyle(
        bgcolor=primary_color,
        color=text_color,
        overlay_color=accent_color,
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        shape=ft.RoundedRectangleBorder(radius=8))

    buttons = ft.Column(
        controls=[
            ft.ElevatedButton(
                "Посмотреть все",
                style=button_style,
                icon=ft.Icons.LIST,
                on_click=lambda e: view_command(e)),
            ft.ElevatedButton(
                "Поиск",
                style=button_style,
                icon=ft.Icons.SEARCH,
                on_click=lambda e: search_command(e)),
            ft.ElevatedButton(
                "Добавить",
                style=button_style,
                icon=ft.Icons.ADD,
                on_click=lambda e: add_command(e)),
            ft.ElevatedButton(
                "Обновить",
                style=button_style,
                icon=ft.Icons.UPDATE,
                on_click=lambda e: update_command(e)),
            ft.ElevatedButton(
                "Удалить",
                style=ft.ButtonStyle(
                    bgcolor="#FFD166",
                    color=text_color,
                    overlay_color="#EF476F",
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    shape=ft.RoundedRectangleBorder(radius=8)),
                icon=ft.Icons.DELETE,
                on_click=lambda e: delete_command(e))],
        spacing=12,
        alignment=ft.MainAxisAlignment.CENTER)

    def update_stats():
        total = db.get_total_spent()
        top_category, top_amount = db.get_top_category()
        stats_text.value = (
            f"Всего потрачено: {total:.2f} руб. | "
            f"Больше всего потрачено на: {top_category} ({top_amount:.2f} руб.)"
        )
        page.update()

    def update_list():
        list_view.controls.clear()
        selected_category = category_dropdown.value if category_dropdown.value and category_dropdown.value != "Все категории" else ""

        rows = db.search(
            product=product_text.value if product_text.value else "",
            category=selected_category
        )

        for row in rows:
            date_str = datetime.strptime(row[5], "%Y-%m-%d").strftime("%d.%m.%Y") if row[5] else "Без даты"
            list_view.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.SHOPPING_CART, color=secondary_color),
                            title=ft.Text(
                                f"{row[1]}",
                                color=text_color,
                                weight=ft.FontWeight.BOLD,
                                size=16),
                            subtitle=ft.Text(
                                f"{row[2]} руб. • {date_str} • {row[3]} • {row[4]}",
                                size=14),
                            on_click=lambda e, row=row: select_row(row)),
                        padding=10,
                        bgcolor=card_color,
                        border_radius=8),
                    elevation=1,
                    color=secondary_color,
                    margin=ft.margin.symmetric(vertical=4)))

        update_stats()
        page.update()

    def select_row(row):
        nonlocal selected_tuple, selected_date
        selected_tuple = row
        product_text.value = row[1]
        price_text.value = row[2]
        comment_text.value = row[3]
        category_dropdown.value = row[4] if row[4] else ""

        if row[5]:
            selected_date = datetime.strptime(row[5], "%Y-%m-%d").date()
            date_text.value = selected_date.strftime("%d.%m.%Y")
        else:
            selected_date = None
            date_text.value = "Дата не выбрана"

        page.update()

    def view_command(e):
        category_dropdown.value = "Все категории"
        product_text.value = ""
        update_list()

    def search_command(e):
        update_list()

    def add_command(e):
        if product_text.value and price_text.value:
            if not selected_date:
                page.snack_bar = ft.SnackBar(ft.Text("Выберите дату!"))
                page.snack_bar.open = True
                page.update()
                return

            category_id = next((cat[0] for cat in categories if cat[1] == category_dropdown.value), None)
            db.insert(
                product_text.value,
                price_text.value,
                comment_text.value,
                category_id,
                selected_date.strftime("%Y-%m-%d")
            )
            update_list()
            clear_fields()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Заполните название и стоимость!"))
            page.snack_bar.open = True
            page.update()

    def delete_command(e):
        if selected_tuple:
            db.delete(selected_tuple[0])
            update_list()
            clear_fields()

    def update_command(e):
        if not selected_tuple:
            page.snack_bar = ft.SnackBar(ft.Text("Выберите запись для обновления!"))
            page.snack_bar.open = True
            page.update()
            return

        if not product_text.value or not price_text.value:
            page.snack_bar = ft.SnackBar(ft.Text("Название и стоимость обязательны!"))
            page.snack_bar.open = True
            page.update()
            return

        if not selected_date:
            page.snack_bar = ft.SnackBar(ft.Text("Выберите дату!"))
            page.snack_bar.open = True
            page.update()
            return

        if selected_tuple:
            category_id = next((cat[0] for cat in categories if cat[1] == category_dropdown.value), None)
            db.update(
                selected_tuple[0],
                product_text.value,
                price_text.value,
                comment_text.value,
                category_id,
                selected_date.strftime("%Y-%m-%d")
            )
            update_list()

    def clear_fields():
        nonlocal selected_date
        product_text.value = ""
        price_text.value = ""
        comment_text.value = ""
        category_dropdown.value = None
        selected_date = None
        date_text.value = "Дата не выбрана"
        page.update()

    page.add(
        ft.Column([
            ft.Text(
                "Каждый рубль на счету",
                size=24,
                color=text_color,
                weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, color=secondary_color),
            ft.Row(
                controls=[product_text, price_text],
                spacing=20),
            ft.Row(
                controls=[comment_text, category_dropdown],
                spacing=20),
            ft.Row(
                controls=[date_button, date_text],
                spacing=20),
            ft.Divider(height=20, color=secondary_color),
            stats_text,
            ft.Divider(height=20, color=secondary_color),
            ft.Row(
                controls=[
                    list_container,
                    buttons],
                spacing=20,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START)],
            expand=True))

    category_dropdown.value = "Все категории"
    update_list()


ft.app(target=main)

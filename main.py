import sqlite3
import flet as ft
from datetime import datetime


class DB:
    def __init__(self):
        self.db_file = "mybooks.db"
        self._create_table()

    def _create_table(self):
        conn = self._get_connection()
        try:
            # Создаем таблицу категорий (если не существует)
            conn.execute(
                "CREATE TABLE IF NOT EXISTS categories ("
                "id INTEGER PRIMARY KEY, "
                "name TEXT UNIQUE)"
            )

            # Создаем таблицу расходов с ссылкой на категорию
            conn.execute(
                "CREATE TABLE IF NOT EXISTS buy ("
                "id INTEGER PRIMARY KEY, "
                "product TEXT, "
                "price TEXT, "
                "comment TEXT, "
                "category_id INTEGER, "
                "FOREIGN KEY(category_id) REFERENCES categories(id))"
            )

            # Добавляем основные категории, если их нет
            conn.execute(
                "INSERT OR IGNORE INTO categories (name) VALUES "
                "('Продукты'), ('Транспорт'), ('Жилье'), ('Развлечения'), ('Другое')"
            )
            # Миграция: добавляем category_id к старым записям
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
                "COALESCE(categories.name, 'Без категории') as category "  # Если категории нет, подставим текст
                "FROM buy LEFT JOIN categories ON buy.category_id = categories.id"  # LEFT JOIN гарантирует выборку всех записей
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

    def insert(self, product, price, comment, category_id):
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT INTO buy VALUES (NULL,?,?,?,?)",
                (product, price, comment, category_id)
            )
            conn.commit()
        finally:
            conn.close()

    def update(self, id, product, price, comment, category_id):
        conn = self._get_connection()
        try:
            conn.execute(
                "UPDATE buy SET product=?, price=?, comment=?, category_id=? WHERE id=?",
                (product, price, comment, category_id, id)
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

    def search(self, product=""):
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT buy.id, buy.product, buy.price, buy.comment, "
                "categories.name as category "
                "FROM buy LEFT JOIN categories ON buy.category_id = categories.id "
                "WHERE buy.product LIKE ?", (f"%{product}%",)
            )
            return cur.fetchall()
        finally:
            conn.close()


def main(page: ft.Page):
    primary_color = "#FFEE93"
    secondary_color = "#F4D35E"
    background_color = "#FFF9E6"
    card_color = "#FFFDF6"
    text_color = "#5E503F"
    accent_color = "#F7C548"

    page.title = "Бюджет 0.2 (с категориями)"
    page.window_width = 800
    page.window_height = 600
    page.bgcolor = background_color
    page.padding = 20

    db = DB()
    selected_tuple = None
    categories = db.get_categories()

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

    # Выпадающий список категорий
    category_dropdown = ft.Dropdown(
        label="Категория",
        options=[ft.dropdown.Option(cat[1]) for cat in categories],
        border_color=secondary_color,
        filled=False,
        fill_color=card_color,
        bgcolor="#FFFDF6",
        color=text_color,

        label_style=ft.TextStyle(color=text_color),
        expand=True)

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

    def update_list():
        list_view.controls.clear()
        for row in db.view():
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
                                f"{row[2]} руб. • {row[4]} • {row[3]}",
                                size=14),
                            on_click=lambda e, row=row: select_row(row), ),
                        padding=10,
                        bgcolor=card_color,
                        border_radius=8),
                    elevation=1,
                    color=secondary_color,
                    margin=ft.margin.symmetric(vertical=4)))
        page.update()

    def select_row(row):
        nonlocal selected_tuple
        selected_tuple = row
        product_text.value = row[1]
        price_text.value = row[2]
        comment_text.value = row[3]
        category_dropdown.value = row[4] if row[4] else ""
        page.update()

    def view_command(e):
        update_list()

    def search_command(e):
        list_view.controls.clear()
        for row in db.search(product_text.value):
            list_view.controls.append(
                ft.Card(
                    content=ft.ListTile(
                        title=ft.Text(f"{row[1]} - {row[2]} руб."),
                        subtitle=ft.Text(f"{row[4]} • {row[3]}"),
                        on_click=lambda e, row=row: select_row(row)),
                    elevation=1,
                    color=secondary_color))
        page.update()

    def add_command(e):
        if product_text.value and price_text.value:
            category_id = next((cat[0] for cat in categories if cat[1] == category_dropdown.value), None)
            db.insert(product_text.value, price_text.value, comment_text.value, category_id)
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
        if selected_tuple:
            category_id = next((cat[0] for cat in categories if cat[1] == category_dropdown.value), None)
            db.update(selected_tuple[0], product_text.value, price_text.value, comment_text.value, category_id)

            update_list()

    def clear_fields():
        product_text.value = ""
        price_text.value = ""
        comment_text.value = ""
        category_dropdown.value = None
        page.update()

    page.add(
        ft.Column([
            ft.Text(
                "Учёт расходов с категориями",
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
            ft.Divider(height=20, color=secondary_color),
            ft.Row(
                controls=[
                    list_container,
                    buttons],
                spacing=20,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START)],
            expand=True))

    update_list()


ft.app(target=main)

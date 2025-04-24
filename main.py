import sqlite3
import flet as ft


class DB:
    def __init__(self):
        self.db_file = "mybooks.db"
        self._create_table()

    def _create_table(self):
        conn = self._get_connection()
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS buy (id INTEGER PRIMARY KEY, product TEXT, price TEXT, comment TEXT)"
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
            cur.execute("SELECT * FROM buy")
            return cur.fetchall()
        finally:
            conn.close()

    def insert(self, product, price, comment):
        conn = self._get_connection()
        try:
            conn.execute("INSERT INTO buy VALUES (NULL,?,?,?)", (product, price, comment))
            conn.commit()
        finally:
            conn.close()

    def update(self, id, product, price):
        conn = self._get_connection()
        try:
            conn.execute("UPDATE buy SET product=?, price=? WHERE id=?", (product, price, id))
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
            cur.execute("SELECT * FROM buy WHERE product=?", (product,))
            return cur.fetchall()
        finally:
            conn.close()


def main(page: ft.Page):
    page.title = "Бюджет 0.1"
    page.window_width = 800
    page.window_height = 600

    db = DB()
    selected_tuple = None

    # Поля ввода
    product_text = ft.TextField(label="Название")
    price_text = ft.TextField(label="Стоимость")
    comment_text = ft.TextField(label="Комментарий")

    # Список покупок
    list1 = ft.ListView(expand=True, spacing=10)

    def update_list():
        list1.controls.clear()
        for row in db.view():
            list1.controls.append(
                ft.ListTile(
                    title=ft.Text(f"{row[1]} - {row[2]} руб."),
                    subtitle=ft.Text(row[3]),
                    on_click=lambda e, row=row: select_row(row)
                )
            )
        page.update()

    def select_row(row):
        nonlocal selected_tuple
        selected_tuple = row
        product_text.value = row[1]
        price_text.value = row[2]
        comment_text.value = row[3]
        page.update()

    def view_command(e):
        update_list()

    def search_command(e):
        list1.controls.clear()
        for row in db.search(product_text.value):
            list1.controls.append(
                ft.ListTile(
                    title=ft.Text(f"{row[1]} - {row[2]} руб."),
                    subtitle=ft.Text(row[3]),
                    on_click=lambda e, row=row: select_row(row)
                )
            )
        page.update()

    def add_command(e):
        db.insert(product_text.value, price_text.value, comment_text.value)
        update_list()
        clear_fields()

    def delete_command(e):
        if selected_tuple:
            db.delete(selected_tuple[0])
            update_list()
            clear_fields()

    def update_command(e):
        if selected_tuple:
            db.update(selected_tuple[0], product_text.value, price_text.value)
            update_list()

    def clear_fields():
        product_text.value = ""
        price_text.value = ""
        comment_text.value = ""
        page.update()

    # Кнопки
    buttons = ft.Column(
        controls=[
            ft.ElevatedButton("Посмотреть все", on_click=view_command),
            ft.ElevatedButton("Поиск", on_click=search_command),
            ft.ElevatedButton("Добавить", on_click=add_command),
            ft.ElevatedButton("Обновить", on_click=update_command),
            ft.ElevatedButton("Удалить", on_click=delete_command),
            ft.ElevatedButton("Закрыть", on_click=lambda e: page.window_close()),
        ],
        spacing=10
    )

    # Основной макет
    page.add(
        ft.Row(
            controls=[
                product_text,
                price_text
            ],
            spacing=20
        ),
        comment_text,
        ft.Row(
            controls=[
                list1,
                buttons
            ],
            expand=True,
            spacing=20
        )
    )

    update_list()


ft.app(target=main)

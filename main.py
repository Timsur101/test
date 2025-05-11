import sqlite3
import flet as ft
#from flet import Colors


class DB:
    def __init__(self):
        # Имя файла базы данных
        self.db_file = "mybooks.db"
        # Создаем таблицу при инициализации
        self._create_table()

    # Создаёт таблицы 'buy', если она не существует
    def _create_table(self):
        conn = self._get_connection()
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS buy (id INTEGER PRIMARY KEY, product TEXT, price TEXT, comment TEXT)"
            )
            conn.commit()
        finally:
            conn.close()

    # Устанавливает соединения с базой данных
    def _get_connection(self):
        return sqlite3.connect(self.db_file)

    # Возвращает все записи из таблицы
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

    primary_color = "#FFEE93"  # Основной нежно-жёлтый
    secondary_color = "#F4D35E"  # Более насыщенный жёлтый
    background_color = "#FFF9E6"  # Очень светлый жёлтый фон
    card_color = "#FFFDF6"  # Почти белый с жёлтым оттенком
    text_color = "#5E503F"  # Тёмно-коричневый для текста
    accent_color = "#F7C548"  # Акцентный жёлтый

    # Настройка страницы
    page.title = "Бюджет 0.1"
    page.window_width = 800
    page.window_height = 600
    page.bgcolor = background_color
    page.padding = 20

    db = DB()
    selected_tuple = None

    # Поля ввода
    product_text = ft.TextField(
        label="Название",
        border_color=secondary_color,
        filled=True,
        bgcolor=card_color,
        color=text_color,
        expand=True,
        label_style=ft.TextStyle(color=text_color)
    )

    price_text = ft.TextField(
        label="Стоимость",
        border_color=secondary_color,
        filled=True,
        bgcolor=card_color,
        color=text_color,
        width=150,
        label_style=ft.TextStyle(color=text_color),
        keyboard_type=ft.KeyboardType.NUMBER
    )

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
        label_style=ft.TextStyle(color=text_color)
    )

    # Список покупок
    list_view = ft.ListView(expand=True, spacing=5) # Элемент управления прокрутки
    list_container = ft.Container(
        content=list_view,
        bgcolor=card_color,
        border_radius=10,
        padding=10,
        border=ft.border.all(1, secondary_color),
        expand=True
    )

    # Стиль для кнопок
    button_style = ft.ButtonStyle(
        bgcolor=primary_color,
        color=text_color,
        overlay_color=accent_color,
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        shape=ft.RoundedRectangleBorder(radius=8)
    )

    # Кнопки (вертикальный массив)
    buttons = ft.Column(
        controls=[
            ft.ElevatedButton(
                "Посмотреть все",
                style=button_style,
                icon=ft.Icons.VIEW_LIST,
                on_click=lambda e: view_command(e)
            ),
            ft.ElevatedButton(
                "Поиск",
                style=button_style,
                icon=ft.Icons.SEARCH,
                on_click=lambda e: search_command(e)
            ),
            ft.ElevatedButton(
                "Добавить",
                style=button_style,
                icon=ft.Icons.ADD,
                on_click=lambda e: add_command(e)
            ),
            ft.ElevatedButton(
                "Обновить",
                style=button_style,
                icon=ft.Icons.UPDATE,
                on_click=lambda e: update_command(e)
            ),
            ft.ElevatedButton(
                "Удалить",
                style=ft.ButtonStyle(
                    bgcolor="#FFD166",
                    color=text_color,
                    overlay_color="#EF476F",
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    shape=ft.RoundedRectangleBorder(radius=8)
                ),
                icon=ft.Icons.DELETE,
                on_click=lambda e: delete_command(e)
            ),
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.CENTER
    )

    # Обновляет отображение списка покупок
    def update_list():
        list_view.controls.clear()
        for row in db.view():
            list_view.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.SHOPPING_BAG, color=secondary_color),
                            title=ft.Text(
                                f"{row[1]}",
                                color=text_color,
                                weight=ft.FontWeight.BOLD,
                                size=16
                            ),
                            subtitle=ft.Text(
                                f"{row[2]} руб. • {row[3]}",
                                #color=ft.colors.GREY_600,
                                size=14
                            ),
                            on_click=lambda e, row=row: select_row(row),
                        ),
                        padding=10,
                        bgcolor=card_color,
                        border_radius=8
                    ),
                    elevation=1,
                    color=secondary_color,
                    margin=ft.margin.symmetric(vertical=4)
                )
            )
        page.update()

    # Заполняет поля ввода данными выбранной записи
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
        list_view.controls.clear()
        for row in db.search(product_text.value):
            list_view.controls.append(
                ft.Card(
                    content=ft.ListTile(
                        title=ft.Text(f"{row[1]} - {row[2]} руб."),
                        subtitle=ft.Text(row[3]),
                        on_click=lambda e, row=row: select_row(row)
                    ),
                    elevation=1,
                    color=secondary_color
                )
            )
        page.update()

    def add_command(e):
        if product_text.value and price_text.value:
            db.insert(product_text.value, price_text.value, comment_text.value)
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
        if selected_tuple:
            db.update(selected_tuple[0], product_text.value, price_text.value)
            update_list()

    # Очищает поля ввода
    def clear_fields():
        product_text.value = ""
        price_text.value = ""
        comment_text.value = ""
        page.update()

    # Компоновка интерфейса
    page.add(
        ft.Column([
            ft.Text(
                "Учёт расходов",
                size=24,
                color=text_color,
                weight=ft.FontWeight.BOLD
            ),
            ft.Divider(height=20, color=secondary_color),
            ft.Row(
                controls=[product_text, price_text],
                spacing=20
            ),
            comment_text,
            ft.Divider(height=20, color=secondary_color),
            ft.Row(
                controls=[
                    list_container,
                    buttons
                ],
                spacing=20,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START
            )
        ], expand=True)
    )

    update_list()


ft.app(target=main)

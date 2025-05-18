import flet as ft
from datetime import datetime


class BudgetView:
    def __init__(self, controller):
        self.controller = controller
        self.primary_color = "#FFEE93"
        self.secondary_color = "#F4D35E"
        self.background_color = "#FFF9E6"
        self.card_color = "#FFFDF6"
        self.text_color = "#5E503F"
        self.accent_color = "#F7C548"

        self.selected_tuple = None
        self.selected_date = None
        self.page = None

    def setup_ui(self, page: ft.Page):
        self.page = page
        page.title = "Бюджет 0.3 (с датами)"
        page.window_width = 800
        page.window_height = 600
        page.bgcolor = self.background_color
        page.padding = 20

        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=self.secondary_color,
                on_primary=self.text_color,
                surface=self.background_color,
                tertiary=self.accent_color,
            )
        )

        # Поля ввода
        self.product_text = ft.TextField(
            label="Название",
            border_color=self.secondary_color,
            filled=True,
            bgcolor=self.card_color,
            color=self.text_color,
            expand=True,
            label_style=ft.TextStyle(color=self.text_color))

        self.price_text = ft.TextField(
            label="Стоимость",
            border_color=self.secondary_color,
            filled=True,
            bgcolor=self.card_color,
            color=self.text_color,
            width=150,
            label_style=ft.TextStyle(color=self.text_color),
            keyboard_type=ft.KeyboardType.NUMBER)

        self.comment_text = ft.TextField(
            label="Комментарий",
            border_color=self.secondary_color,
            filled=True,
            bgcolor=self.card_color,
            color=self.text_color,
            expand=True,
            multiline=True,
            min_lines=1,
            max_lines=3,
            label_style=ft.TextStyle(color=self.text_color))

        # Дата
        self.date_text = ft.Text(
            "Дата не выбрана",
            size=14,
            color=self.text_color)

        self.date_button = ft.ElevatedButton(
            "Выбрать дату",
            icon=ft.Icons.CALENDAR_MONTH,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                color=self.text_color,
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                shape=ft.RoundedRectangleBorder(radius=8)),
            on_click=self.open_date_picker)

        # Категории
        self.category_dropdown = ft.Dropdown(
            hint_text="Выберите категорию для фильтрации",
            label="Категория",
            options=[ft.dropdown.Option("Все категории")],
            border_color=self.secondary_color,
            filled=False,
            fill_color=self.card_color,
            bgcolor="#FFFDF6",
            color=self.text_color,
            label_style=ft.TextStyle(color=self.text_color),
            expand=True,
            on_change=lambda e: self.controller.search_command(e)
        )

        # Статистика
        self.stats_text = ft.Text(
            "Статистика: загрузка...",
            size=14,
            color=self.text_color,
            weight=ft.FontWeight.BOLD)

        # Список покупок
        self.list_view = ft.ListView(expand=True, spacing=5)
        self.list_container = ft.Container(
            content=self.list_view,
            bgcolor=self.card_color,
            border_radius=10,
            padding=10,
            border=ft.border.all(1, self.secondary_color),
            expand=True)

        # Кнопки
        button_style = ft.ButtonStyle(
            bgcolor=self.primary_color,
            color=self.text_color,
            overlay_color=self.accent_color,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            shape=ft.RoundedRectangleBorder(radius=8))

        self.buttons = ft.Column(
            controls=[
                ft.ElevatedButton(
                    "Посмотреть все",
                    style=button_style,
                    icon=ft.Icons.LIST,
                    on_click=lambda e: self.controller.view_command(e)),
                ft.ElevatedButton(
                    "Поиск",
                    style=button_style,
                    icon=ft.Icons.SEARCH,
                    on_click=lambda e: self.controller.search_command(e)),
                ft.ElevatedButton(
                    "Добавить",
                    style=button_style,
                    icon=ft.Icons.ADD,
                    on_click=lambda e: self.controller.add_command(e)),
                ft.ElevatedButton(
                    "Обновить",
                    style=button_style,
                    icon=ft.Icons.UPDATE,
                    on_click=lambda e: self.controller.update_command(e)),
                ft.ElevatedButton(
                    "Удалить",
                    style=ft.ButtonStyle(
                        bgcolor="#FFD166",
                        color=self.text_color,
                        overlay_color="#EF476F",
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        shape=ft.RoundedRectangleBorder(radius=8)),
                    icon=ft.Icons.DELETE,
                    on_click=lambda e: self.controller.delete_command(e))],
            spacing=12,
            alignment=ft.MainAxisAlignment.CENTER)

        # Добавляем всё на страницу
        page.add(
            ft.Column([
                ft.Text(
                    "Каждый рубль на счету",
                    size=24,
                    color=self.text_color,
                    weight=ft.FontWeight.BOLD),
                ft.Divider(height=20, color=self.secondary_color),
                ft.Row(
                    controls=[self.product_text, self.price_text],
                    spacing=20),
                ft.Row(
                    controls=[self.comment_text, self.category_dropdown],
                    spacing=20),
                ft.Row(
                    controls=[self.date_button, self.date_text],
                    spacing=20),
                ft.Divider(height=20, color=self.secondary_color),
                self.stats_text,
                ft.Divider(height=20, color=self.secondary_color),
                ft.Row(
                    controls=[
                        self.list_container,
                        self.buttons],
                    spacing=20,
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.START)],
                expand=True))

        # Инициализация
        self.update_category_dropdown()
        self.controller.update_view()

    def open_date_picker(self, e):
        date_picker = ft.DatePicker(
            first_date=datetime(2000, 1, 1),
            last_date=datetime(2030, 12, 31),
            on_change=self.handle_date_change,
        )
        self.page.open(date_picker)

    def handle_date_change(self, e):
        self.selected_date = e.control.value
        self.date_text.value = self.selected_date.strftime("%d.%m.%Y")
        self.page.update()

    def update_category_dropdown(self):
        categories = self.controller.get_categories()
        self.category_dropdown.options = [ft.dropdown.Option("Все категории")] + [
            ft.dropdown.Option(cat[1]) for cat in categories
        ]
        self.page.update()

    def update_list(self, rows):
        self.list_view.controls.clear()
        for row in rows:
            date_str = datetime.strptime(row[5], "%Y-%m-%d").strftime("%d.%m.%Y") if row[5] else "Без даты"
            self.list_view.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.SHOPPING_CART, color=self.secondary_color),
                            title=ft.Text(
                                f"{row[1]}",
                                color=self.text_color,
                                weight=ft.FontWeight.BOLD,
                                size=16),
                            subtitle=ft.Text(
                                f"{row[2]} руб. • {date_str} • {row[3]} • {row[4]}",
                                size=14),
                            on_click=lambda e, row=row: self.controller.select_row(row)),
                        padding=10,
                        bgcolor=self.card_color,
                        border_radius=8),
                    elevation=1,
                    color=self.secondary_color,
                    margin=ft.margin.symmetric(vertical=4)))
        self.page.update()

    def update_stats(self, total, top_category, top_amount):
        self.stats_text.value = (
            f"Всего потрачено: {total:.2f} руб. | "
            f"Больше всего потрачено на: {top_category} ({top_amount:.2f} руб.)"
        )
        self.page.update()

    def select_row(self, row):
        self.selected_tuple = row
        self.product_text.value = row[1]
        self.price_text.value = row[2]
        self.comment_text.value = row[3]
        self.category_dropdown.value = row[4] if row[4] else ""

        if row[5]:
            self.selected_date = datetime.strptime(row[5], "%Y-%m-%d").date()
            self.date_text.value = self.selected_date.strftime("%d.%m.%Y")
        else:
            self.selected_date = None
            self.date_text.value = "Дата не выбрана"

        self.page.update()

    def clear_fields(self):
        self.selected_tuple = None
        self.selected_date = None
        self.product_text.value = ""
        self.price_text.value = ""
        self.comment_text.value = ""
        self.category_dropdown.value = None
        self.date_text.value = "Дата не выбрана"
        self.page.update()

    def show_snackbar(self, message):
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()

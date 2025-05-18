import flet as ft
from database import DB
from view import BudgetView
from controller import BudgetController


def main(page: ft.Page):
    # Создаем компоненты MVC
    model = DB()
    view = BudgetView(None)  # Контроллер будет установлен позже
    controller = BudgetController(model, view)

    # Настраиваем View
    view.setup_ui(page)


ft.app(target=main)

import flet as ft
from database import DB
from view import BudgetView
from registration_view import RegistrationView
from controller import BudgetController

def main(page: ft.Page):
    # Создаем компоненты MVC
    model = DB()
    registration_view = RegistrationView(None)  # Контроллер будет установлен позже
    view = BudgetView(None)  # Контроллер будет установлен позже
    controller = BudgetController(model, view, registration_view)

    # Устанавливаем текущую страницу
    controller.current_page = page

    # Настраиваем начальный интерфейс (регистрация)
    registration_view.setup_ui(page)

ft.app(target=main)
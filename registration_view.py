import flet as ft

class RegistrationView:
    def __init__(self, controller):
        self.controller = controller
        self.primary_color = "#FFEE93"
        self.secondary_color = "#F4D35E"
        self.background_color = "#FFF9E6"
        self.card_color = "#FFFDF6"
        self.text_color = "#5E503F"
        self.accent_color = "#F7C548"
        self.page = None

    def setup_ui(self, page: ft.Page):
        self.page = page
        page.title = "Регистрация"
        page.window_width = 400
        page.window_height = 500
        page.bgcolor = self.background_color
        page.padding = 20
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER

        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=self.secondary_color,
                on_primary=self.text_color,
                surface=self.background_color,
                tertiary=self.accent_color,
            )
        )

        # Поля ввода
        self.login_text = ft.TextField(
            label="Логин",
            border_color=self.secondary_color,
            filled=True,
            bgcolor=self.card_color,
            color=self.text_color,
            label_style=ft.TextStyle(color=self.text_color),
            width=300
        )

        self.email_text = ft.TextField(
            label="Email",
            border_color=self.secondary_color,
            filled=True,
            bgcolor=self.card_color,
            color=self.text_color,
            label_style=ft.TextStyle(color=self.text_color),
            width=300
        )

        self.password_text = ft.TextField(
            label="Пароль",
            border_color=self.secondary_color,
            filled=True,
            bgcolor=self.card_color,
            color=self.text_color,
            label_style=ft.TextStyle(color=self.text_color),
            password=True,
            can_reveal_password=True,
            width=300
        )

        # Кнопка регистрации
        button_style = ft.ButtonStyle(
            bgcolor=self.primary_color,
            color=self.text_color,
            overlay_color=self.accent_color,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            shape=ft.RoundedRectangleBorder(radius=8)
        )

        self.register_button = ft.ElevatedButton(
            "Зарегистрироваться",
            style=button_style,
            icon=ft.Icons.PERSON_ADD,
            on_click=self.controller.register_command
        )

        # Кнопка перехода к бюджету
        self.to_budget_button = ft.TextButton(
            "Уже есть аккаунт? Перейти к бюджету",
            style=ft.ButtonStyle(color=self.text_color),
            on_click=self.controller.switch_to_budget
        )

        # Макет страницы
        page.add(
            ft.Column(
                [
                    ft.Text(
                        "Регистрация",
                        size=24,
                        color=self.text_color,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Divider(height=20, color=self.secondary_color),
                    self.login_text,
                    self.email_text,
                    self.password_text,
                    self.register_button,
                    self.to_budget_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            )
        )

    def show_snackbar(self, message):
        """Отображает уведомление об ошибке или успехе."""
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()

    def clear_fields(self):
        """Очищает поля ввода."""
        self.login_text.value = ""
        self.email_text.value = ""
        self.password_text.value = ""
        self.page.update()
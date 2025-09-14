from datetime import datetime

class BudgetController:
    def __init__(self, model, view, registration_view=None):
        self.model = model
        self.view = view
        self.registration_view = registration_view
        self.view.controller = self
        if self.registration_view:
            self.registration_view.controller = self
        self.current_page = None

    def register_command(self, e):
        """Обрабатывает команду регистрации."""
        login = self.registration_view.login_text.value
        email = self.registration_view.email_text.value
        password = self.registration_view.password_text.value

        if not login or not email or not password:
            self.registration_view.show_snackbar("Заполните все поля!")
            return

        if self.model.check_user_exists(login, email):
            self.registration_view.show_snackbar("Логин или email уже заняты!")
            return

        if self.model.register_user(login, email, password):
            self.registration_view.show_snackbar("Регистрация успешна!")
            self.registration_view.clear_fields()
            self.switch_to_budget(None)  # Переход к основному интерфейсу
        else:
            self.registration_view.show_snackbar("Ошибка регистрации. Попробуйте снова.")

    def switch_to_budget(self, e):
        """Переключает на интерфейс бюджета."""
        if self.current_page:
            self.current_page.controls.clear()
            self.view.setup_ui(self.current_page)
            self.current_page.update()

    def get_categories(self):
        return self.model.get_categories()

    def view_command(self, e):
        self.view.category_dropdown.value = "Все категории"
        self.view.product_text.value = ""
        self.update_view()

    def search_command(self, e):
        self.update_view()

    def add_command(self, e):
        if not self.view.product_text.value or not self.view.price_text.value:
            self.view.show_snackbar("Заполните название и стоимость!")
            return

        if not self.view.selected_date:
            self.view.show_snackbar("Выберите дату!")
            return

        category_id = next((cat[0] for cat in self.get_categories()
                            if cat[1] == self.view.category_dropdown.value), None)

        self.model.insert(
            self.view.product_text.value,
            self.view.price_text.value,
            self.view.comment_text.value,
            category_id,
            self.view.selected_date.strftime("%Y-%m-%d")
        )

        self.update_view()
        self.view.clear_fields()

    def delete_command(self, e):
        if self.view.selected_tuple:
            self.model.delete(self.view.selected_tuple[0])
            self.update_view()
            self.view.clear_fields()

    def update_command(self, e):
        if not self.view.selected_tuple:
            self.view.show_snackbar("Выберите запись для обновления!")
            return

        if not self.view.product_text.value or not self.view.price_text.value:
            self.view.show_snackbar("Название и стоимость обязательны!")
            return

        if not self.view.selected_date:
            self.view.show_snackbar("Выберите дату!")
            return

        category_id = next((cat[0] for cat in self.get_categories()
                            if cat[1] == self.view.category_dropdown.value), None)

        self.model.update(
            self.view.selected_tuple[0],
            self.view.product_text.value,
            self.view.price_text.value,
            self.view.comment_text.value,
            category_id,
            self.view.selected_date.strftime("%Y-%m-%d")
        )

        self.update_view()

    def select_row(self, row):
        self.view.select_row(row)

    def update_view(self):
        selected_category = (self.view.category_dropdown.value
                             if self.view.category_dropdown.value and
                                self.view.category_dropdown.value != "Все категории"
                             else "")

        rows = self.model.search(
            product=self.view.product_text.value if self.view.product_text.value else "",
            category=selected_category
        )

        self.view.update_list(rows)

        total = self.model.get_total_spent()
        top_category, top_amount = self.model.get_top_category()
        self.view.update_stats(total, top_category, top_amount)
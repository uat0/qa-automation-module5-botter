import allure
from playwright.sync_api import expect
from pages.base_page import BasePage


class PracticeFormPage(BasePage):
    """All form locators and browser interactions belong to this Page Object."""
    def __init__(self, page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Practice Form", exact=True)
        self.form = page.locator("#userForm")
        self.first_name = page.locator("#firstName")
        self.last_name = page.locator("#lastName")
        self.email = page.locator("#userEmail")
        self.mobile = page.locator("#userNumber")
        self.submit_button = page.locator("#submit")
        self.modal = page.get_by_role("dialog")
        self.city_input = page.locator("#react-select-4-input")
        self.state_control = page.locator("#state")
        self.city_control = page.locator("#city")

    @allure.step("Открыть Practice Form")
    def open_form(self):
        self.open("/automation-practice-form")
        expect(self.heading).to_be_visible()

    @allure.step("Заполнить обязательные поля")
    def fill_required(self, first="Вадим", last="Боттер", mobile="9991234567", gender="Male"):
        self.first_name.fill(first)
        self.last_name.fill(last)
        self.mobile.fill(mobile)
        self.page.get_by_text(gender, exact=True).click()

    @allure.step("Ввести email {value}")
    def fill_email(self, value):
        self.email.fill(value)

    @allure.step("Отправить форму")
    def submit(self):
        self.submit_button.click()

    def assert_open(self):
        expect(self.first_name).to_be_visible()
        expect(self.last_name).to_be_visible()
        expect(self.submit_button).to_be_visible()

    def assert_submitted(self):
        expect(self.modal).to_be_visible()
        expect(self.modal).to_contain_text("Thanks for submitting the form")

    def assert_rejected(self):
        expect(self.modal).not_to_be_visible()
        assert self.form.evaluate("el => el.checkValidity()") is False

    def assert_result(self, label, value):
        row = self.modal.get_by_role("row").filter(has=self.page.get_by_role("cell", name=label, exact=True))
        expect(row.get_by_role("cell").nth(1)).to_have_text(value)

    def invalid_fields(self):
        return self.form.locator(":invalid").evaluate_all("els => els.map(e => e.id)")

    def assert_mobile(self, value):
        expect(self.mobile).to_have_value(value)

    def choose_state(self, value):
        self.state_control.click()
        self.page.get_by_text(value, exact=True).click()

    def choose_city(self, value):
        self.city_control.click()
        self.page.get_by_text(value, exact=True).click()

    def assert_city_disabled(self):
        expect(self.city_input).to_be_disabled()

    def assert_city_enabled(self):
        expect(self.city_input).to_be_enabled()

    def close_with_escape(self):
        self.page.keyboard.press("Escape")
        expect(self.modal).not_to_be_visible()

    def close_with_button(self):
        self.modal.get_by_role("button", name="Close", exact=True).click()
        expect(self.modal).not_to_be_visible(timeout=3000)

    def fill_address(self, value):
        self.page.locator("#currentAddress").fill(value)

    def assert_no_script_execution(self):
        assert self.page.evaluate("() => window.__botter_xss === undefined")

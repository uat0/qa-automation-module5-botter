import os
from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def open(self, path: str):
        self.page.goto(os.getenv("BASE_URL", "https://demoqa.com") + path, wait_until="domcontentloaded")

    def screenshot(self) -> bytes:
        return self.page.screenshot(full_page=True)

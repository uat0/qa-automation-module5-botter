import os
import re
import allure
from playwright.sync_api import sync_playwright
from pages.practice_form_page import PracticeFormPage


def before_all(context):
    context.playwright=sync_playwright().start()
    context.browser=getattr(context.playwright,os.getenv("BDD_BROWSER","chromium")).launch()


def before_scenario(context,scenario):
    context.browser_context=context.browser.new_context(viewport={"width":1440,"height":1000},locale="en-US")
    context.page=context.browser_context.new_page()
    context.page.set_default_timeout(10000)
    context.page.set_default_navigation_timeout(45000)
    context.page.route(re.compile(r".*(?:doubleclick\.net|googlesyndication\.com|google-analytics\.com|googletagmanager\.com)/.*"),lambda route:route.abort())
    context.form=PracticeFormPage(context.page)


def after_scenario(context,scenario):
    allure.attach(context.page.screenshot(full_page=True),name=scenario.name,attachment_type=allure.attachment_type.PNG)
    context.browser_context.close()


def after_all(context):
    context.browser.close()
    context.playwright.stop()

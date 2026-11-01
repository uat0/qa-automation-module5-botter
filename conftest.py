from datetime import date
from pathlib import Path
import json
import os
import re
import allure
import pytest
import requests
from pages.practice_form_page import PracticeFormPage


@pytest.fixture
def fixed_today():
    return date(2026, 11, 1)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport":{"width":1440,"height":1000}, "locale":"en-US"}


@pytest.fixture
def practice_form(page):
    page.set_default_timeout(10000)
    page.set_default_navigation_timeout(45000)
    # Only third-party ad requests are blocked; DemoQA DOM and validation are untouched.
    page.route(re.compile(r".*(?:doubleclick\.net|googlesyndication\.com|google-analytics\.com|adservice\.google\.com|googletagmanager\.com)/.*"), lambda route:route.abort())
    form = PracticeFormPage(page)
    form.open_form()
    return form


def redact(value):
    if isinstance(value,dict):
        return {k:("<redacted>" if k.lower() in {"password","token","authorization","expires"} else redact(v)) for k,v in value.items()}
    if isinstance(value,list):
        return [redact(v) for v in value]
    return value


@pytest.fixture
def api():
    with requests.Session() as session:
        def send(method, path, **kwargs):
            response = session.request(method, os.getenv("BASE_URL","https://demoqa.com")+path, timeout=30, **kwargs)
            try:
                body=response.json()
            except ValueError:
                body=response.text[:1000]
            evidence={"method":method,"path":path,"request":redact(kwargs),"status":response.status_code,"body":redact(body),"elapsed_seconds":response.elapsed.total_seconds()}
            allure.attach(json.dumps(evidence,ensure_ascii=False,indent=2), name=f"{method} {path}", attachment_type=allure.attachment_type.JSON)
            return response
        yield send


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and (report.failed or getattr(report,"wasxfail",None)):
        page=item.funcargs.get("page")
        if page and not page.is_closed():
            allure.attach(page.screenshot(full_page=True),name="Failure screenshot",attachment_type=allure.attachment_type.PNG)
            allure.attach(page.url,name="URL",attachment_type=allure.attachment_type.TEXT)


def pytest_sessionfinish(session, exitstatus):
    reporter=session.config.pluginmanager.get_plugin("terminalreporter")
    destination=Path(os.getenv("RESULTS_DIR","results/latest"))
    destination.mkdir(parents=True,exist_ok=True)
    records=[]
    for status in ("passed","failed","skipped","xfailed","xpassed","error"):
        for report in reporter.stats.get(status,[]):
            if report.when=="call" or status=="error":
                records.append({"id":report.nodeid,"status":status,"duration":report.duration})
    (destination/"pytest-results.json").write_text(json.dumps({"exitcode":int(exitstatus),"tests":records},ensure_ascii=False,indent=2),encoding="utf-8")

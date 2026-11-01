import csv
from pathlib import Path
import allure
import pytest

pytestmark = [pytest.mark.ui, allure.feature("Practice Form")]


def test_open_form(practice_form):
    """TC-01: smoke."""
    practice_form.assert_open()


def test_empty_form(practice_form):
    """TC-15: all four required fields are checked."""
    practice_form.submit()
    practice_form.assert_rejected()
    assert {"firstName","lastName","gender-radio-1","userNumber"} <= set(practice_form.invalid_fields())


@pytest.mark.ddt
@pytest.mark.parametrize("case", list(csv.DictReader((Path(__file__).parents[2]/"data/form_cases.csv").open(encoding="utf-8"))), ids=lambda c:c["id"])
def test_form_data(practice_form, case):
    practice_form.fill_required(case["first_name"], case["last_name"], case["mobile"])
    practice_form.fill_email(case["email"])
    practice_form.submit()
    if case["expected"] == "accepted":
        practice_form.assert_submitted()
        practice_form.assert_result("Student Name", f'{case["first_name"]} {case["last_name"]}')
        practice_form.assert_result("Mobile", case["mobile"])
        practice_form.assert_result("Student Email", case["email"])
    else:
        practice_form.assert_rejected()


def test_mobile_letters_rejected(practice_form):
    """TC-02."""
    practice_form.fill_required(mobile="abcdefghij")
    practice_form.submit()
    practice_form.assert_rejected()


def test_mobile_max_length(practice_form):
    """TC-08."""
    practice_form.fill_required(mobile="99912345678")
    practice_form.assert_mobile("9991234567")


def test_dependent_city(practice_form):
    """TC-20."""
    practice_form.assert_city_disabled()
    practice_form.choose_state("NCR")
    practice_form.assert_city_enabled()
    practice_form.choose_city("Delhi")
    practice_form.fill_required()
    practice_form.submit()
    practice_form.assert_result("State and City", "NCR Delhi")


def test_modal_escape(practice_form):
    """TC-17, TC-21: modal can be dismissed with Esc."""
    practice_form.fill_required()
    practice_form.submit()
    practice_form.assert_submitted()
    practice_form.close_with_escape()


def test_html_is_text(practice_form):
    """TC-25: local sentinel proves that submitted text was not executed."""
    payload = '<img src=x onerror="window.__botter_xss=1">'
    practice_form.fill_required()
    practice_form.fill_address(payload)
    practice_form.submit()
    practice_form.assert_result("Address", payload)
    practice_form.assert_no_script_execution()


@pytest.mark.xfail(strict=True, reason="BUG-03 / TC-10 from Module 4: email pattern restricts TLD to 2..5 characters", raises=AssertionError)
def test_long_tld_regression(practice_form):
    practice_form.fill_required()
    practice_form.fill_email("vadim.botter@mail.online")
    practice_form.submit()
    practice_form.assert_submitted()


@pytest.mark.xfail(strict=True, reason="BUG-01 / TC-18 from Module 4: Close button raises findDOMNode error", raises=AssertionError)
def test_close_button_regression(practice_form):
    practice_form.fill_required()
    practice_form.submit()
    practice_form.assert_submitted()
    practice_form.close_with_button()

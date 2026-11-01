from datetime import date
import allure
import pytest
from app.validators import validate_name, validate_email, validate_mobile, validate_age, validate_birth_date, normalize_name

pytestmark = [pytest.mark.unit, allure.feature("Reference validators")]


@pytest.mark.ddt
@pytest.mark.parametrize("value,expected", [
    ("", True), ("user@mail.ru", True), ("vadim.botter@mail.online", True),
    ("a+b@sub.example.com", True), ("user", False), ("a@@b.ru", False),
    ("@mail.ru", False), (".a@mail.ru", False), ("a.@mail.ru", False),
    ("a..b@mail.ru", False), ("a b@mail.ru", False), ("a@mail", False),
    ("a@mail.r", False), ("a@mail.123", False), ("a@-mail.ru", False),
    ("a@mail-.ru", False), ("a@mail..ru", False), ("a@x.ru", True),
])
def test_email(value, expected):
    assert validate_email(value) is expected


@pytest.mark.ddt
@pytest.mark.parametrize("value,expected", [("", False), ("   ", False), ("Вадим", True), ("Анна-Мария", True), ("Vadim Botter", True), ("12345", False), ("!@#", False)])
def test_name(value, expected):
    assert validate_name(value) is expected


@pytest.mark.ddt
@pytest.mark.parametrize("value,expected", [("", False), ("999123456", False), ("9991234567", True), ("99912345678", False), ("abcdefghij", False), ("١٢٣٤٥٦٧٨٩٠", False)])
def test_mobile(value, expected):
    assert validate_mobile(value) is expected


@pytest.mark.parametrize("value,expected", [(17,False),(18,True),(19,True),(99,True),(100,True),(101,False)])
def test_age(value, expected):
    assert validate_age(value) is expected


@pytest.mark.parametrize("value,expected", [(date(1899,12,31),False),(date(1900,1,1),True),(date(2026,11,1),True),(date(2026,11,2),False)])
def test_birth_date(value, expected, fixed_today):
    assert validate_birth_date(value, fixed_today) is expected


def test_normalize_name():
    assert normalize_name("  Вадим \t Боттер\n") == "Вадим Боттер"

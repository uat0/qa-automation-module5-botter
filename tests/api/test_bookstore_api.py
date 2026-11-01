import uuid
import allure
import pytest

pytestmark = [pytest.mark.api, allure.feature("Book Store API")]


def test_books_contract(api):
    response = api("GET", "/BookStore/v1/Books")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
    books = response.json()["books"]
    assert books
    assert len({b["isbn"] for b in books}) == len(books)
    assert all({"isbn", "title", "author", "publisher"} <= b.keys() for b in books)


def test_get_single_book(api):
    books = api("GET", "/BookStore/v1/Books").json()["books"]
    response = api("GET", "/BookStore/v1/Book", params={"ISBN":books[0]["isbn"]})
    assert response.status_code == 200
    assert response.json()["title"] == books[0]["title"]


def test_invalid_isbn(api):
    response = api("GET", "/BookStore/v1/Book", params={"ISBN":"invalid"})
    assert response.status_code == 400
    assert response.json()["code"] == "1205"


@pytest.mark.ddt
@pytest.mark.xfail(strict=True, reason="API-BUG-01: invalid Login returns HTTP 200 with an empty body instead of an error", raises=AssertionError)
@pytest.mark.parametrize("username,password", [("",""),("botter_missing_user_20261101","wrong")], ids=["empty","unknown-user"])
def test_login_negative(api, username, password):
    response = api("POST", "/Account/v1/Login", json={"userName":username,"password":password})
    assert 400 <= response.status_code < 500
    assert response.json()["code"]
    assert response.json()["message"]


def test_weak_password(api):
    response = api("POST", "/Account/v1/User", json={"userName":"botter_"+uuid.uuid4().hex,"password":"weak"})
    assert response.status_code == 400
    assert response.json()["code"] == "1300"


def test_user_registration_login_and_cleanup(api):
    payload = {"userName":"botter_m5_"+uuid.uuid4().hex,"password":"QaModule5!Test123"}
    created = api("POST", "/Account/v1/User", json=payload)
    assert created.status_code == 201, created.text
    user_id = created.json()["userID"]
    token = None
    try:
        token_response = api("POST", "/Account/v1/GenerateToken", json=payload)
        assert token_response.status_code == 200
        token = token_response.json()["token"]
        assert token
        login = api("POST", "/Account/v1/Login", json=payload)
        assert login.status_code == 200, login.text
        assert login.json()["userId"] == user_id
        assert login.json()["username"] == payload["userName"]
        authorized = api("POST", "/Account/v1/Authorized", json=payload)
        assert authorized.status_code == 200
        assert authorized.json() is True
    finally:
        if token is None:
            token = api("POST", "/Account/v1/GenerateToken", json=payload).json().get("token")
        removed = api("DELETE", f"/Account/v1/User/{user_id}", headers={"Authorization":f"Bearer {token}"})
        assert removed.status_code == 204, f"Cleanup failed for {user_id}: {removed.text}"

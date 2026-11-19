# The API's own tests. They pass from the start, and they must still pass when you're done:
# cleaning up the code never changes what the API answers.
# Run them with the exercise's checks: pytest (in the exercise folder, with the virtual
# environment on). Before every test, the fixture throwaway_database makes a new database file in
# pytest's tmp_path, runs the migrations on it, adds the starting rows, and tells the app to use
# that file instead of lost_and_found.db. You don't need to change this file.
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from database import get_db, migrate, open_db
from main import app

client = TestClient(app, raise_server_exceptions=False)

# The rows every test starts with: three items, and one claim, for item 2.
SEED = """
INSERT INTO items (id, name, found_at, found_on) VALUES
    (1, 'Blue umbrella', 'Library, 2nd floor', '2026-11-10'),
    (2, 'Calculator', 'Room 104', '2026-11-12'),
    (3, 'Water bottle', 'Gym lobby', '2026-11-13');
INSERT INTO claims (id, item_id, student, claimed_on) VALUES
    (1, 2, 'Priya', '2026-11-14');
"""

UMBRELLA = {
    "id": 1,
    "name": "Blue umbrella",
    "found_at": "Library, 2nd floor",
    "found_on": "2026-11-10",
    "claimed": False,
}


@pytest.fixture(autouse=True)
def throwaway_database(tmp_path: Path) -> Iterator[Path]:
    path = tmp_path / "lost_and_found_test.db"
    conn = open_db(path)
    migrate(conn)
    conn.executescript(SEED)
    conn.close()

    def get_test_db() -> Iterator[sqlite3.Connection]:
        conn = open_db(path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    app.dependency_overrides[get_db] = get_test_db
    yield path
    app.dependency_overrides.clear()


def check_status(response: Any, expected: int, request: str) -> None:
    """Fails with a message that says what came back, when the status code isn't expected."""
    assert response.status_code == expected, (
        f"{request} should answer {expected}, but it answered {response.status_code} "
        f"with {response.text}"
    )


def test_api_1_get_items_answers_200_with_all_3_items() -> None:
    response = client.get("/items")
    check_status(response, 200, "GET /items")
    assert [item["name"] for item in response.json()] == [
        "Blue umbrella",
        "Calculator",
        "Water bottle",
    ]


def test_api_2_get_item_1_answers_200_with_the_umbrella() -> None:
    response = client.get("/items/1")
    check_status(response, 200, "GET /items/1")
    assert response.json() == UMBRELLA


def test_api_3_get_item_99_answers_404() -> None:
    response = client.get("/items/99")
    check_status(response, 404, "GET /items/99")
    assert response.json() == {
        "status": 404,
        "title": "Not Found",
        "detail": "There's no item 99.",
    }


def test_api_4_post_items_answers_201_with_the_red_scarf() -> None:
    body = {"name": "Red scarf", "found_at": "Cafeteria", "found_on": "2026-11-16"}
    response = client.post("/items", json=body)
    check_status(response, 201, "POST /items")
    assert response.json() == {"id": 4, **body, "claimed": False}
    assert client.get("/items/4").json() == {"id": 4, **body, "claimed": False}


def test_api_5_post_items_without_found_on_answers_422() -> None:
    response = client.post("/items", json={"name": "Red scarf", "found_at": "Cafeteria"})
    check_status(response, 422, "POST /items with no found_on")
    assert response.json()["problems"] == [{"field": "found_on", "message": "Field required"}]


def test_api_6_claim_item_1_answers_201_and_marks_it_claimed() -> None:
    body = {"student": "Jun", "claimed_on": "2026-11-17"}
    response = client.post("/items/1/claims", json=body)
    check_status(response, 201, "POST /items/1/claims")
    assert response.json() == {"id": 2, "item_id": 1, **body}
    assert client.get("/items/1").json()["claimed"] is True


def test_api_7_claim_item_99_answers_404() -> None:
    body = {"student": "Jun", "claimed_on": "2026-11-17"}
    response = client.post("/items/99/claims", json=body)
    check_status(response, 404, "POST /items/99/claims")
    assert response.json()["detail"] == "There's no item 99."


def test_api_8_claim_item_2_again_answers_409() -> None:
    body = {"student": "Jun", "claimed_on": "2026-11-17"}
    response = client.post("/items/2/claims", json=body)
    check_status(response, 409, "POST /items/2/claims")
    assert response.json() == {
        "status": 409,
        "title": "Conflict",
        "detail": "Item 2 has already been claimed.",
    }

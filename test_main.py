import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_storage():
    main.items.clear()
    main.next_id = 1
    yield
    main.items.clear()


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_create_item_post():
    response = client.post(
        "/items",
        json={"name": "Book", "price": 12.5, "description": "FastAPI book"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Book"
    assert data["price"] == 12.5


def test_get_item_path_and_query():
    client.post("/items", json={"name": "Book", "price": 12.5})

    response = client.get("/items/1?verbose=true")

    assert response.status_code == 200
    data = response.json()
    assert data["item"]["name"] == "Book"
    assert data["source"] == "memory"


def test_list_items_query():
    client.post("/items", json={"name": "Book", "price": 12.5})
    client.post("/items", json={"name": "Pen", "price": 1.5})

    response = client.get("/items?limit=1&offset=0&q=book")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Book"


def test_get_item_404():
    response = client.get("/items/999")
    assert response.status_code == 404


def test_post_validation_error():
    response = client.post("/items", json={"name": "", "price": -1})
    assert response.status_code == 422
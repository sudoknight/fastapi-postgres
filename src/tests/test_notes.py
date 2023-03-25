import json
import logging

import pytest

from app.api import crud

logger = logging.getLogger(__name__)


# this test is used to test the post end point
# we mock the post crud method so that we dont send a call to the database
def test_create_note(test_app, monkeypatch):
    test_request_payload = {"title": "something", "description": "something else"}
    test_response_payload = {
        "id": 1,
        "title": "something",
        "description": "something else",
    }

    async def mock_post(payload):
        logger.info(f"mock_post called {payload}")
        return 1

    monkeypatch.setattr(crud, "post", mock_post)
    response = test_app.post(
        "/notes/",
        content=json.dumps(test_request_payload),
    )
    assert response.status_code == 201
    assert response.json() == test_response_payload


# this is used to test the post end point by sending a invalid input payload
def test_create_note_invalid_json(test_app):
    response = test_app.post("/notes/", content=json.dumps({"title": "something"}))
    assert response.status_code == 422


# this test is used to test the get end point
# we mock the get crud method so that we dont send a call to the database
def test_read_note(test_app, monkeypatch):
    test_data = {"id": 1, "title": "something", "description": "something else"}

    async def mock_get(id):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/notes/1")
    assert response.status_code == 200
    assert response.json() == test_data


# this test is used to test the get end point
# we mock the get crud method so that we dont send a call to the database
def test_read_note_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/notes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


# This test case is used to test the get all notes endpoint
# its mocks the get all method so that we don't read all the records from the database
def test_read_all_notes(test_app, monkeypatch):
    test_data = [
        {"title": "something", "description": "something else", "id": 1},
        {"title": "someone", "description": "someone else", "id": 2},
    ]

    async def mock_get_all():
        return test_data

    monkeypatch.setattr(crud, "get_all", mock_get_all)
    response = test_app.get("/notes/")
    assert response.status_code == 200  # if this cond is false, throw error
    assert response.json() == test_data  # if this cond is false, throw error


# This test case is used to test the update end point
# it mocks the db updated method, and get after updated method.
def test_update_note(test_app, monkeypatch):
    test_update_data = {"title": "someone", "description": "someone else", "id": 1}

    async def mock_get(id):
        return True

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_put(id, payload):
        return 1

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put("/notes/1/", content=json.dumps(test_update_data))
    assert response.status_code == 200
    assert (
        response.json() == test_update_data
    )  # if data after updated is not equal to the updated payload


# the below test case is used to test update, when the input payload is invalid
@pytest.mark.parametrize(
    "id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"description": "bar"}, 422],
        [999, {"title": "foo", "description": "bar"}, 404],
    ],
)
def test_update_not_invalid(test_app, monkeypatch, id, payload, status_code):
    def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)
    response = test_app.put(
        f"/notes/{id}/",
        content=json.dumps(payload),
    )
    assert response.status_code == status_code

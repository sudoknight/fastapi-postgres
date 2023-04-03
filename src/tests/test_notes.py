# This files contains test cases for the notes endpoints
# These test cases evaluate the workflow of each endpoint without making any call to the database.
# All the crud utility methods get, post put, get_all are mocked so that we don't use actuall call to database.
# Mocked method mimic the behavior of crud utility methods.


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
    # when one field is missing
    response = test_app.post("/notes/", content=json.dumps({"title": "something"}))
    assert response.status_code == 422

    # when input text does not meet the minimum length
    response = test_app.post("/notes/", content=json.dumps({"title": "1", "description": "2"}))
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


# this test is used to test the get end point when the input id is invalid
# we mock the get crud method so that we dont send a call to the database
def test_read_note_incorrect_id(test_app, monkeypatch):
    
    # when the input id is 999
    test_data = 999
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get(f"/notes/{test_data}")
    assert response.status_code == 404  # not found
    assert response.json()["detail"] == f"Note not found for id {test_data}"

    # when the input id 0 
    test_data = 0
    response = test_app.get(f"/notes/{test_data}")
    assert response.status_code == 422  # validation error


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


# the below test case is used to test update end point, when the input payload is invalid
# In the parametrize decorator, method input params and expected output value are passed for each test.
@pytest.mark.parametrize(
    "id, payload, status_code",
    [
        [1, {}, 422],  # all required fields missing
        [1, {"description": "bar"}, 422],  # some required fields missing
        [999, {"title": "foo", "description": "bar"}, 404],  # id not valid
        [1, {"title": "1", "description": "bar"}, 422],  # input text not meeting validation rules
        [1, {"title": "foo", "description": "1"}, 422],   # input text not meeting validation rules
        [0, {"title": "foo", "description": "bar"}, 422], # input id not meeting validation rules
    ],
)
def test_update_not_invalid(test_app, monkeypatch, id, payload, status_code):
    async def mock_get(id):
        return None

    monkeypatch.setattr(crud, "get", mock_get)
    response = test_app.put(
        f"/notes/{id}/",
        content=json.dumps(payload),
    )
    assert response.status_code == status_code


# The below test is to check the delete end point
# it mocks the db crud methods for get and delete.

def test_remove_note(test_app, monkeypatch):
    test_data = {"title": "something", "description": "something else", "id": 1}

    async def mock_get(id):
        return test_data
    
    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_delete(id):
        return id
    
    monkeypatch.setattr(crud, "delete", mock_delete)

    response = test_app.delete("/notes/1")
    assert response.status_code == 200
    assert response.json() == test_data


# The below test is to check the delete endpoint when the input id is invalid
def test_remove_note_incorrec_id(test_app, monkeypatch):
    
    # when the input id is 999
    test_data = 999
    async def mock_get(id):
        return None
    
    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.delete(f"/notes/{test_data}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Note not found for id {test_data}"

    # when the input id is 0
    test_data = 0
    response = test_app.delete(f"/notes/{test_data}")
    assert response.status_code == 422  # validation error


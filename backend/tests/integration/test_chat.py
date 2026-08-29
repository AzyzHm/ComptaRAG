import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from routes import chat


@pytest.fixture
def client():
    test_app = FastAPI()
    test_app.include_router(chat.router)
    return TestClient(test_app)


def test_chat_returns_answer_and_category_on_success(client, mocker):
    mocker.patch(
        "routes.chat.app.invoke",
        return_value={
            "answer": "IFRS 16 requires lessees to recognize a right-of-use asset.",
            "category": "ifrs",
        },
    )

    response = client.post("/chat/", json={"query": "What is IFRS 16?"})

    assert response.status_code == 200
    assert response.json() == {
        "response": "IFRS 16 requires lessees to recognize a right-of-use asset.",
        "category": "ifrs",
    }


def test_chat_passes_query_into_initial_graph_state(client, mocker):
    spy = mocker.patch(
        "routes.chat.app.invoke",
        return_value={"answer": "answer", "category": "tax_code"},
    )

    client.post("/chat/", json={"query": "Comment calculer la TVA ?"})

    spy.assert_called_once_with({"query": "Comment calculer la TVA ?"})


def test_chat_returns_null_category_when_missing_from_graph_result(client, mocker):
    mocker.patch("routes.chat.app.invoke", return_value={"answer": "answer only"})

    response = client.post("/chat/", json={"query": "q"})

    assert response.status_code == 200
    assert response.json() == {"response": "answer only", "category": None}


def test_chat_returns_500_with_error_detail_when_graph_raises(client, mocker):
    mocker.patch("routes.chat.app.invoke", side_effect=RuntimeError("LLM unavailable"))

    response = client.post("/chat/", json={"query": "q"})

    assert response.status_code == 500
    assert response.json() == {"detail": "LLM unavailable"}


def test_chat_returns_422_when_query_field_missing(client, mocker):
    spy = mocker.patch("routes.chat.app.invoke")

    response = client.post("/chat/", json={})

    assert response.status_code == 422
    spy.assert_not_called()


def test_chat_returns_422_when_query_is_wrong_type(client, mocker):
    spy = mocker.patch("routes.chat.app.invoke")

    response = client.post("/chat/", json={"query": 123})

    assert response.status_code == 422
    spy.assert_not_called()


def test_chat_accepts_empty_string_query(client, mocker):
    spy = mocker.patch(
        "routes.chat.app.invoke",
        return_value={"answer": "Please ask a question.", "category": "general_knowledge"},
    )

    response = client.post("/chat/", json={"query": ""})

    assert response.status_code == 200
    spy.assert_called_once_with({"query": ""})
import pytest

from media_auth.web import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index(client):
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"Media Authn" in rv.data


def test_api_sign_no_file(client):
    rv = client.post("/api/sign", data={})
    assert rv.status_code == 400
    assert b"No file part" in rv.data


def test_api_verify_missing(client):
    rv = client.post("/api/verify", data={})
    assert rv.status_code == 400
    assert b"Missing" in rv.data

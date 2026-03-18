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


def test_api_sign_success(client, mocker):
    mocker.patch("media_auth.web.sign_media", autospec=True)
    mocker.patch("media_auth.web.shutil.make_archive", autospec=True)
    mocker.patch("media_auth.web.shutil.rmtree", autospec=True)
    mocker.patch("media_auth.web.send_file", return_value="File sent")
    import io

    data = {
        "file": (io.BytesIO(b"my image data"), "test.jpg"),
        "keyid": "test_key",
    }
    rv = client.post("/api/sign", data=data, content_type="multipart/form-data")
    assert rv.status_code == 200
    assert rv.data == b"File sent"


def test_api_verify_success(client, mocker):
    mocker.patch("media_auth.web.verify_media", return_value=(True, "Success msg"))
    import io

    data = {
        "pubkey_file": (io.BytesIO(b"pubkey"), "pub.asc"),
        "sig_file": (io.BytesIO(b"sig"), "sig.asc"),
        "media_file": (io.BytesIO(b"media"), "media.jpg"),
    }
    rv = client.post("/api/verify", data=data, content_type="multipart/form-data")
    assert rv.status_code == 200
    assert b"Success msg" in rv.data

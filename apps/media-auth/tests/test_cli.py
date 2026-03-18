from unittest.mock import patch

import pytest

from media_auth.cli import main


def test_cli_sign(mocker):
    mock_sign = mocker.patch("media_auth.cli.sign_media")
    # Provide args
    with patch("sys.argv", ["media-auth", "sign", "in.png", "out.zip", "--keyid", "test"]):
        # Should exit 0 or just run and return
        main(["sign", "in.png", "out.zip", "--keyid", "test"])
    mock_sign.assert_called_once()


def test_cli_verify_success(mocker):
    mock_verify = mocker.patch("media_auth.cli.verify_media", return_value=(True, "Success"))
    with patch("sys.argv", ["media-auth", "verify", "out.zip", "in.png"]):
        with pytest.raises(SystemExit) as e:
            main(["verify", "out.zip", "in.png"])
        assert e.value.code == 0
    mock_verify.assert_called_once()


def test_cli_verify_fail(mocker):
    mock_verify = mocker.patch("media_auth.cli.verify_media", return_value=(False, "Fail"))
    with patch("sys.argv", ["media-auth", "verify", "out.zip", "in.png"]):
        with pytest.raises(SystemExit) as e:
            main(["verify", "out.zip", "in.png"])
        assert e.value.code == 1
    mock_verify.assert_called_once()

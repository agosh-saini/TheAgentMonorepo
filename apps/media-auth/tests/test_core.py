import os

import pytest
from PIL import Image

from media_auth.core import (
    hash_file,
    sign_media,
    verify_media,
)


def test_hash_file(mock_image):
    """Test deterministic file hashing."""
    hash1 = hash_file(mock_image)
    hash2 = hash_file(mock_image)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 length


def test_sign_media(mocker, temp_dir, mock_image, mock_gpg_home, gpg_mock):
    """Integration test for signing workflow."""
    out_folder = str(temp_dir / "output_folder")

    sign_media(mock_image, out_folder, mock_gpg_home, "test_key")

    assert os.path.exists(out_folder)
    assert os.path.isdir(out_folder)

    assert os.path.exists(os.path.join(out_folder, "original.png"))
    assert os.path.exists(os.path.join(out_folder, "public_key.asc"))
    assert os.path.exists(os.path.join(out_folder, "signature.asc"))

    with open(os.path.join(out_folder, "signature.asc"), "r") as f:
        sig_data = f.read()
    assert "BEGIN PGP SIGNATURE" in sig_data


def test_verify_media_success(mocker, temp_dir, mock_image, mock_gpg_home, gpg_mock):
    """Integration test for successful verification."""
    out_folder = str(temp_dir / "output_folder")
    sign_media(mock_image, out_folder, mock_gpg_home, "test_key")

    pubkey = os.path.join(out_folder, "public_key.asc")
    sig = os.path.join(out_folder, "signature.asc")
    valid, msg = verify_media(mock_image, pubkey, sig, mock_gpg_home)
    assert valid is True
    assert "Success" in msg


def test_verify_media_failure_altered(mocker, temp_dir, mock_image, mock_gpg_home, gpg_mock):
    """Integration test for verification failure due to altered media."""
    out_folder = str(temp_dir / "output_folder")
    sign_media(mock_image, out_folder, mock_gpg_home, "test_key")

    # Create an altered media file
    altered = temp_dir / "altered.png"
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(altered)

    pubkey = os.path.join(out_folder, "public_key.asc")
    sig = os.path.join(out_folder, "signature.asc")

    valid, msg = verify_media(str(altered), pubkey, sig, mock_gpg_home)
    assert valid is False
    assert "Hash mismatch" in msg


def test_verify_missing_signature(temp_dir, mock_image, mock_gpg_home):
    """Test verify with missing components in zip."""
    pubkey = str(temp_dir / "fake_pub.asc")
    sig = str(temp_dir / "fake_sig.asc")

    valid, msg = verify_media(mock_image, pubkey, sig, mock_gpg_home)
    assert valid is False
    assert "Provided signature or public key file does not exist" in msg


@pytest.mark.smoke
def test_smoke(mocker, temp_dir, mock_image, mock_gpg_home, gpg_mock):
    """Smoke test for fast full pipeline execution."""
    out_folder = str(temp_dir / "smoke_folder")

    # End-to-end execution with mocking
    sign_media(mock_image, out_folder, mock_gpg_home, "smoke_key")

    pubkey = os.path.join(out_folder, "public_key.asc")
    sig = os.path.join(out_folder, "signature.asc")

    # Verify the original
    valid1, msg1 = verify_media(mock_image, pubkey, sig, mock_gpg_home)
    assert valid1 is True

    # Alter the image and verify failure
    altered = temp_dir / "altered.png"
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(altered)

    valid2, msg2 = verify_media(str(altered), pubkey, sig, mock_gpg_home)
    assert valid2 is False

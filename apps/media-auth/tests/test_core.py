import os
import zipfile

import pytest
from PIL import Image

from media_auth.core import (
    hash_file,
    process_image,
    sign_media,
    verify_media,
)


def test_hash_file(mock_image):
    """Test deterministic file hashing."""
    hash1 = hash_file(mock_image)
    hash2 = hash_file(mock_image)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 length


def test_process_image(temp_dir, mock_image):
    """Test deterministic image cropping."""
    out1 = str(temp_dir / "out1.png")
    out2 = str(temp_dir / "out2.png")

    # Same seed should produce same output
    process_image(mock_image, out1, seed=42)
    process_image(mock_image, out2, seed=42)

    hash1 = hash_file(out1)
    hash2 = hash_file(out2)
    assert hash1 == hash2

    # Output should be smaller than original (100x100 -> 80x80)
    with Image.open(out1) as img:
        assert img.size == (80, 80)


def test_sign_media(mocker, temp_dir, mock_image, mock_gpg_home, gpg_mock):
    """Integration test for signing workflow."""
    out_zip = str(temp_dir / "output.zip")

    sign_media(mock_image, out_zip, mock_gpg_home, "test_key", seed=42)

    assert os.path.exists(out_zip)

    with zipfile.ZipFile(out_zip, "r") as zf:
        namelist = zf.namelist()
        assert "original.png" in namelist
        assert "cropped.png" in namelist
        assert "public_key.asc" in namelist
        assert "signature.asc" in namelist

        sig_data = zf.read("signature.asc").decode("utf-8")
        assert "BEGIN PGP SIGNATURE" in sig_data


def test_verify_media_success(mocker, temp_dir, mock_image, mock_gpg_home, gpg_mock):
    """Integration test for successful verification."""
    out_zip = str(temp_dir / "output.zip")
    sign_media(mock_image, out_zip, mock_gpg_home, "test_key", seed=42)

    valid, msg = verify_media(out_zip, mock_image, mock_gpg_home)
    assert valid is True
    assert "Success" in msg


def test_verify_media_failure_altered(mocker, temp_dir, mock_image, mock_gpg_home, gpg_mock):
    """Integration test for verification failure due to altered media."""
    out_zip = str(temp_dir / "output.zip")
    sign_media(mock_image, out_zip, mock_gpg_home, "test_key", seed=42)

    # Create an altered media file
    altered = temp_dir / "altered.png"
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(altered)

    valid, msg = verify_media(out_zip, str(altered), mock_gpg_home)
    assert valid is False
    assert "Hash mismatch" in msg


def test_verify_missing_signature(temp_dir, mock_image, mock_gpg_home):
    """Test verify with missing components in zip."""
    out_zip = str(temp_dir / "bad.zip")
    with zipfile.ZipFile(out_zip, "w") as zf:
        zf.write(mock_image, arcname="original.png")
        # Missing pubkey and signature

    valid, msg = verify_media(out_zip, mock_image, mock_gpg_home)
    assert valid is False
    assert "ZIP does not contain required signature or public key" in msg


@pytest.mark.smoke
def test_smoke(mocker, temp_dir, mock_image, mock_gpg_home, gpg_mock):
    """Smoke test for fast full pipeline execution."""
    out_zip = str(temp_dir / "smoke.zip")

    # End-to-end execution with mocking
    sign_media(mock_image, out_zip, mock_gpg_home, "smoke_key", seed=10)

    # Verify the original
    valid1, msg1 = verify_media(out_zip, mock_image, mock_gpg_home)
    assert valid1 is True

    # Extract cropped to test tampering
    extract_dir = temp_dir / "extract"
    with zipfile.ZipFile(out_zip, "r") as zf:
        zf.extractall(extract_dir)

    cropped_path = str(extract_dir / "cropped.png")

    # Verify the cropped (should fail because it's altered)
    valid2, msg2 = verify_media(out_zip, cropped_path, mock_gpg_home)
    assert valid2 is False

"""Core logic module."""

import hashlib
import os
import random
import shutil
import zipfile
from pathlib import Path
from typing import Optional, Tuple

import gnupg
from PIL import Image


def hash_file(filepath: str) -> str:
    """Calculate the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def process_image(filepath: str, outpath: str, seed: Optional[int] = None) -> None:
    """Randomly crop an image and save it."""
    if seed is not None:
        random.seed(seed)

    with Image.open(filepath) as img:
        width, height = img.size

        # Crop to 80% of original size
        new_width = int(width * 0.8)
        new_height = int(height * 0.8)

        # Ensure we don't go out of bounds
        max_x = max(0, width - new_width)
        max_y = max(0, height - new_height)

        left = random.randint(0, max_x) if max_x > 0 else 0
        top = random.randint(0, max_y) if max_y > 0 else 0
        right = left + new_width
        bottom = top + new_height

        cropped = img.crop((left, top, right, bottom))
        # Ensure we convert to RGB before saving as some formats (like JPEG) don't support RGBA
        if cropped.mode in ("RGBA", "P"):
            cropped = cropped.convert("RGB")
        cropped.save(outpath)


def init_gpg(gpg_home: str) -> gnupg.GPG:
    """Initialize GPG object."""
    os.makedirs(gpg_home, exist_ok=True)
    return gnupg.GPG(gnupghome=gpg_home)


def sign_hash(gpg: gnupg.GPG, data: str, keyid: Optional[str] = None) -> str:
    """Sign a string (hash) using GPG."""
    kwargs = {}
    if keyid:
        kwargs["keyid"] = keyid

    signed = gpg.sign(data, **kwargs)
    if not signed or not signed.data:
        raise ValueError(
            f"Failed to sign data. Make sure a private key is available. stderr: {signed.stderr}"
        )

    return str(signed)


def export_public_key(gpg: gnupg.GPG, keyid: str, outpath: str) -> None:
    """Export public key to a file."""
    key_data = gpg.export_keys(keyid)
    if not key_data:
        raise ValueError(f"Failed to export public key for {keyid}")

    with open(outpath, "w") as f:
        f.write(key_data)


def create_auth_zip(
    original_media: str, cropped_media: str, signature_data: str, pubkey_path: str, out_zip: str
) -> None:
    """Bundle everything into a ZIP file."""
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(original_media, arcname=f"original{Path(original_media).suffix}")
        zf.write(cropped_media, arcname=f"cropped{Path(cropped_media).suffix}")
        zf.write(pubkey_path, arcname="public_key.asc")
        zf.writestr("signature.asc", signature_data)


def sign_media(
    filepath: str, out_zip: str, gpg_home: str, keyid: str, seed: Optional[int] = None
) -> None:
    """High-level function to sign media and create zip."""
    gpg = init_gpg(gpg_home)

    file_hash = hash_file(filepath)
    signature = sign_hash(gpg, file_hash, keyid)

    # Create temp directory for intermediate files
    temp_dir = Path(out_zip).parent / f".tmp_{Path(out_zip).stem}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        cropped_path = str(temp_dir / f"cropped_{Path(filepath).name}")
        process_image(filepath, cropped_path, seed)

        pubkey_path = str(temp_dir / "public_key.asc")
        export_public_key(gpg, keyid, pubkey_path)

        create_auth_zip(filepath, cropped_path, signature, pubkey_path, out_zip)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def verify_media(
    zip_path: str, target_media_path: str, gpg_home: str, extract_dir: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Verify if target_media_path matches the signature in the zip.
    Extracts the zip, imports public key, verifies signature, compares hashes.
    Returns (True, message) if valid, (False, message) if invalid.
    """
    if extract_dir is None:
        extract_dir = str(Path(zip_path).parent / f".extract_{Path(zip_path).stem}")

    os.makedirs(extract_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        pubkey_path = os.path.join(extract_dir, "public_key.asc")
        sig_path = os.path.join(extract_dir, "signature.asc")

        if not os.path.exists(pubkey_path) or not os.path.exists(sig_path):
            return False, "ZIP does not contain required signature or public key."

        gpg = init_gpg(gpg_home)

        # Import the public key from the zip
        with open(pubkey_path, "r") as f:
            import_result = gpg.import_keys(f.read())
            if import_result.count == 0:
                # Key might already exist, which is fine
                pass

        # Verify the signature
        with open(sig_path, "rb") as f:
            verified = gpg.verify(f.read())

        if not verified:
            return False, "GPG signature verification failed."

        original_hash = verified.data.decode("utf-8").strip()

        # Hash the target media
        target_hash = hash_file(target_media_path)

        if target_hash == original_hash:
            return True, "Success! File is authentic and unaltered."
        else:
            return False, "Hash mismatch! File has been altered."

    finally:
        # Clean up if we auto-created the dir
        if str(Path(zip_path).parent / f".extract_{Path(zip_path).stem}") == extract_dir:
            shutil.rmtree(extract_dir, ignore_errors=True)

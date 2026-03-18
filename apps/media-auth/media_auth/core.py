import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def hash_file(filepath: str) -> str:
    """Calculate the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def _run_gpg(
    gpg_home: str, args: list, input_data: Optional[bytes] = None
) -> subprocess.CompletedProcess:
    """Helper to run gpg commands with a specific home directory."""
    os.makedirs(gpg_home, exist_ok=True)
    os.chmod(gpg_home, 0o700)

    cmd = ["gpg", "--homedir", gpg_home, "--batch", "--no-tty", "--yes"] + args
    return subprocess.run(cmd, input=input_data, capture_output=True)


def sign_hash(gpg_home: str, data: str, keyid: str) -> str:
    """Sign a string (hash) using GPG clearsign."""
    args = ["--clear-sign"]
    if keyid:
        args.extend(["--default-key", keyid])

    result = _run_gpg(gpg_home, args, input_data=data.encode("utf-8"))

    if result.returncode != 0:
        err_msg = result.stderr.decode("utf-8")
        raise ValueError(
            f"Failed to sign data. Make sure a private key is available. stderr: {err_msg}"
        )

    return result.stdout.decode("utf-8")


def export_public_key(gpg_home: str, keyid: str, outpath: str) -> None:
    """Export public key to a file."""
    args = ["--armor", "--export", keyid]
    result = _run_gpg(gpg_home, args)

    if result.returncode != 0 or not result.stdout:
        raise ValueError(
            f"Failed to export public key for {keyid}. stderr: {result.stderr.decode('utf-8')}"
        )

    with open(outpath, "wb") as f:
        f.write(result.stdout)


def sign_media(filepath: str, out_folder: str, gpg_home: str, keyid: str) -> None:
    """High-level function to sign media and create an auth folder."""
    file_hash = hash_file(filepath)
    signature = sign_hash(gpg_home, file_hash, keyid)

    out_dir = Path(out_folder)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        shutil.copy2(filepath, out_dir / f"original{Path(filepath).suffix}")

        with open(out_dir / "signature.asc", "w") as f:
            f.write(signature)

        pubkey_path = str(out_dir / "public_key.asc")
        export_public_key(gpg_home, keyid, pubkey_path)

    except Exception as e:
        shutil.rmtree(out_dir, ignore_errors=True)
        raise e


def verify_media(
    target_media_path: str, pubkey_path: str, sig_path: str, gpg_home: str
) -> Tuple[bool, str]:
    """
    Verify if target_media_path matches the signature.
    Imports public key, verifies signature, compares hashes.
    Returns (True, message) if valid, (False, message) if invalid.
    """
    if not os.path.exists(pubkey_path) or not os.path.exists(sig_path):
        return False, "Provided signature or public key file does not exist."

    try:
        import tempfile

        with tempfile.TemporaryDirectory() as temp_gpg_home:
            # Import the public key into an isolated temporary keyring
            _run_gpg(temp_gpg_home, ["--import", pubkey_path])

            # Verify the signature and extract the hash
            verify_result = _run_gpg(temp_gpg_home, ["--decrypt", sig_path])
            if verify_result.returncode != 0:
                err_msg = verify_result.stderr.decode("utf-8")
                return False, f"GPG signature verification failed. {err_msg}"

            original_hash = verify_result.stdout.decode("utf-8").strip()

        # Hash the target media
        target_hash = hash_file(target_media_path)

        if target_hash == original_hash:
            return True, "Success! File is authentic and unaltered."
        else:
            return False, "Hash mismatch! File has been altered."

    except Exception as e:
        return False, str(e)

import pytest
from PIL import Image


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def mock_image(temp_dir):
    """Create a simple deterministic image for testing."""
    img_path = temp_dir / "test_image.png"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)
    return str(img_path)


@pytest.fixture
def mock_gpg_home(temp_dir):
    """Create a temporary directory for mock GPG home."""
    gpg_home = temp_dir / ".gnupg"
    gpg_home.mkdir()
    return str(gpg_home)


@pytest.fixture
def gpg_mock(mocker):
    """Mock the subprocess.run inside core.py."""

    class MockProcess:
        def __init__(self, returncode, stdout, stderr=b""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def mock_run_gpg(gpg_home, args, input_data=None):
        if "--clear-sign" in args:
            data = input_data.decode("utf-8")
            out = f"-----BEGIN PGP SIGNATURE-----\n{data}\n-----END PGP SIGNATURE-----".encode(
                "utf-8"
            )
            return MockProcess(0, out)
        elif "--export" in args:
            return MockProcess(
                0,
                b"-----BEGIN PGP PUBLIC KEY BLOCK-----\n"
                b"MOCKKEY\n"
                b"-----END PGP PUBLIC KEY BLOCK-----",
            )
        elif "--import" in args:
            return MockProcess(0, b"")
        elif "--decrypt" in args:
            # signature path is the last arg
            sig_path = args[-1]
            try:
                with open(sig_path, "r") as f:
                    sig_data = f.read()
                lines = sig_data.split("\n")
                if len(lines) >= 3:
                    data = lines[1].encode("utf-8")
                    return MockProcess(0, data)
                return MockProcess(1, b"", b"Verification failed")
            except Exception:
                return MockProcess(1, b"", b"Read failed")
        return MockProcess(1, b"", b"Unknown command")

    return mocker.patch("media_auth.core._run_gpg", side_effect=mock_run_gpg)

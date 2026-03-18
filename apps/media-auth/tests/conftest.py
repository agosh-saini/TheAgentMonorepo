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
    """Mock the gnupg.GPG class."""
    mock = mocker.patch("media_auth.core.gnupg.GPG")
    instance = mock.return_value

    # Mock sign
    class MockSign:
        def __init__(self, data):
            self.data = (
                f"-----BEGIN PGP SIGNATURE-----\n{data}\n-----END PGP SIGNATURE-----".encode(
                    "utf-8"
                )
            )
            self.stderr = ""

        def __str__(self):
            return self.data.decode("utf-8")

    instance.sign.side_effect = lambda data, **kwargs: MockSign(data)

    # Mock export
    instance.export_keys.return_value = (
        "-----BEGIN PGP PUBLIC KEY BLOCK-----\nMOCKKEY\n-----END PGP PUBLIC KEY BLOCK-----"
    )

    # Mock import
    class MockImportResult:
        count = 1

    instance.import_keys.return_value = MockImportResult()

    # Mock verify
    class MockVerify:
        def __init__(self, sig_data):
            self.valid = True
            # Extract the hash data from the mock signature
            text = sig_data.decode("utf-8")
            lines = text.split("\n")
            if len(lines) >= 3:
                self.data = lines[1].encode("utf-8")
            else:
                self.data = b"wrong"
                self.valid = False

        def __bool__(self):
            return self.valid

    instance.verify.side_effect = lambda sig_data: MockVerify(sig_data)

    return instance

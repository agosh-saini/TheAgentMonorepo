# Media Authenticator (`media_auth`)

A Python CLI and Web application that securely hashes and signs media files (like images and video) using a GPG private key. It packages the signature along with the original and a heavily modified visual representation (cropped version) into a single ZIP archive. It then provides tools to verify if an incoming media frame genuinely matches the originally signed data.

## Requirements

- Python 3.9+
- `gnupg` (GnuPG must be installed on your system)
- An active GPG Private key in your keychain (You can use the sister project `gpg-gen` to create one securely).

## Setup & Testing

A `Makefile` is provided to handle virtual environments and testing tasks seamlessly.

```bash
make setup  # Creates a `.venv`, installs requirements, and links the local package
make check  # Runs ruff format, ruff lint, and pytest checks in the virtual environment
```

## CLI Usage

The tool provides an easy-to-use Command Line Interface. Note that `make setup` registers the `media-auth` command in the virtual environment.

### 1. Sign Media

```bash
media-auth sign path/to/image.png path/to/output.zip --keyid "your-email@example.com"
```
*(Tip: You can optionally pass `--gpg-home` or a `--seed` for reproducible cropping)*

### 2. Verify Media

```bash
media-auth verify path/to/output.zip path/to/test-image.png
```

### 3. Launch Web UI

You can launch a very beautiful dark-glassmorphism Web UI locally using Flask to handle these tasks graphically:

```bash
media-auth web --host 127.0.0.1 --port 5000
```
This will start a web server running at [http://127.0.0.1:5000](http://127.0.0.1:5000).

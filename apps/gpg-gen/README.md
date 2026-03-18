# GPG Gen Tool

A command-line tool written in Bash to generate a GPG key pair using the highest security standards (e.g., Ed25519 for signing/certifying and Cv25519 for encryption). It defensively configures GPG preferences, forces high entropy pools via user interactions (if required), and seamlessly exports a public key.

## Requirements
- `bash`
- `gpg` (GnuPG)

## Usage

You can use the script directly from your terminal.

```bash
./generate.sh --name "John Doe" --email "john@example.com"
```

### Options

- `--name <string>`: Full Name for the GPG key (required)
- `--email <string>`: Email for the GPG key (required)
- `--out <dir>`: Output directory for the exported public key (default: `./keys`)
- `--non-interactive`: Skip entropy gathering (useful for testing or automated environments)
- `--help`: Display usage instructions

## Development & Testing

This project comes with a Python wrapper test suite using Pytest for validation and CI gating. The tests run against a temporary isolated gpg mock environment to ensure no interference with your real keyring.

To run the checks:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make check
```

This will run code formatting (`ruff format`), linting (`ruff check`), and the test suite (`pytest`) checking code coverage.

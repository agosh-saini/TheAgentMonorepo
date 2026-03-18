# GPG Gen Tool

## What it does
A command-line tool written in Bash to generate a GPG key pair using the highest security standards (e.g., Ed25519 for signing/certifying and Cv25519 for encryption, or RSA-4096). To help guarantee a cryptographically secure foundation, the script interactively prompts the user to move their mouse, type random keys, or perform similar physical actions to gather robust system entropy during the generation phase.

## Stack
Bash

## Key features
- Generates keys with top-tier security standards, prioritizing modern ECC (Ed25519/Cv25519) or RSA-4096.
- Forces high-security algorithm preferences (e.g., SHA512, AES256) for future operations with the generated key.
- Interactively pauses and asks the user to generate randomness ("Please move your mouse or type randomly to build entropy pool...") to feed `/dev/random` before creating the keys.
- Handles non-interactive and batch GPG setup smoothly behind the scenes while keeping the entropy prompt interactive.
- Validates system dependencies (`gpg`, entropy-gathering tools) and fails fast with a clear error message if absent.
- Auto-exports the final public key to a designated directory for easy access.

## Notes
- Must be cross-platform (macOS/Linux compatible).
- Needs to be highly defensive with set `-e`, `-u`, and `-o pipefail`.
- Must not log or output the private key or passphrase.

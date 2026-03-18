# Media Authenticator (`media-auth`)

## What it does
A tool that cryptographically signs media files (images/videos) to prove their authenticity, and provides a verification mechanism to detect tampering. It takes an input media file, generates a hash, signs it using a GPG private key, and bundles the original file, a randomly modified (cropped) version, the cryptographic signature, and the public key into a single ZIP archive. The verification process checks a file's integrity by comparing its hash against the decrypted signature using the included public key.

## Stack
Python (using `Pillow` or `opencv-python` for media modification, and `python-gnupg` or `subprocess` for GPG operations).

## Key features
- **Sign Mode:**
  - Calculates a secure hash (e.g., SHA-256) of the input media file.
  - Signs the hash using the user's GPG private key.
  - Generates a randomly modified version of the original media (e.g., visually cropping it).
  - Packages everything into a ZIP file containing:
    1. The exported GPG public key.
    2. The signature file (signed hash).
    3. The original media file.
    4. The modified (cropped) media file.
- **Verify Mode:**
  - Extracts the ZIP archive.
  - Generates a hash of a target media file (to see if it matches the original or modified one).
  - Uses the bundled public key to verify the signature.
  - Confirms whether the target file is the unaltered original or if it has been edited/tampered with.

## Notes
- Must adhere strictly to the global testing and security rules (deterministic tests, isolated from real system GPG keychains during tests, high unit test coverage).
- Use temporary mock GPG home directories for all testing.
- Randomness (for cropping) should accept a seed for reproducibility during tests.
- CLI application structure separating business logic from entry endpoints.

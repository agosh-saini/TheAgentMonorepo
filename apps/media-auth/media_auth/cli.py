"""Media Authenticator CLI."""

import argparse
import logging
import sys
from typing import Optional

from media_auth.core import (
    sign_media,
    verify_media,
)
from media_auth.web import run_web_app

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def handle_sign(args: argparse.Namespace) -> None:
    """Handle sign command."""
    try:
        sign_media(
            filepath=args.input_file,
            out_zip=args.out_zip,
            gpg_home=args.gpg_home,
            keyid=args.keyid,
            seed=args.seed,
        )
        logger.info(f"Successfully signed media. Zip output at: {args.out_zip}")
    except Exception as e:
        logger.error(f"Sign failed: {str(e)}")
        sys.exit(1)


def handle_verify(args: argparse.Namespace) -> None:
    """Handle verify command."""
    try:
        valid, msg = verify_media(
            zip_path=args.zip_file, target_media_path=args.target_file, gpg_home=args.gpg_home
        )
        if valid:
            logger.info(msg)
            sys.exit(0)
        else:
            logger.error(msg)
            sys.exit(1)
    except Exception as e:
        logger.error(f"Verify failed: {str(e)}")
        sys.exit(1)


def main(args_list: Optional[list[str]] = None) -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Media Authenticator tool.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sign parser
    sign_parser = subparsers.add_parser("sign", help="Sign a media file and create a auth zip.")
    sign_parser.add_argument("input_file", help="Path to original media file.")
    sign_parser.add_argument("out_zip", help="Path to output zip file.")
    sign_parser.add_argument("--keyid", help="GPG Key ID to use for signing.")
    sign_parser.add_argument("--gpg-home", default="~/.gnupg", help="GPG home directory.")
    sign_parser.add_argument(
        "--seed", type=int, default=None, help="Deterministic seed for cropping."
    )

    # Verify parser
    verify_parser = subparsers.add_parser("verify", help="Verify a media file against an auth zip.")
    verify_parser.add_argument("zip_file", help="Path to auth zip file.")
    verify_parser.add_argument("target_file", help="Path to the media file to verify.")
    verify_parser.add_argument("--gpg-home", default="~/.gnupg", help="GPG home directory.")

    # Web parser
    web_parser = subparsers.add_parser("web", help="Start the web UI server.")
    web_parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    web_parser.add_argument("--port", type=int, default=5000, help="Port to bind.")

    args = parser.parse_args(args_list)

    # Expand user paths
    if hasattr(args, "gpg_home"):
        import os

        args.gpg_home = os.path.expanduser(args.gpg_home)

    if args.command == "sign":
        handle_sign(args)
    elif args.command == "verify":
        handle_verify(args)
    elif args.command == "web":
        run_web_app(host=args.host, port=args.port)


if __name__ == "__main__":
    main()

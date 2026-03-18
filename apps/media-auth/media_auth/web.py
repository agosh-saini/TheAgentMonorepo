"""Flask Web UI for Media Authenticator."""

import os
import secrets
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

from media_auth.core import sign_media, verify_media

# Configure Flask app, pointing to relative dirs
template_dir = os.path.join(os.path.dirname(__file__), "templates")
static_dir = os.path.join(os.path.dirname(__file__), "static")
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = secrets.token_hex(16)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

DEFAULT_GPG_HOME = os.path.expanduser("~/.gnupg")

# Empty state file to check if we can actually use sign features
has_gpg = os.path.exists(DEFAULT_GPG_HOME)


@app.route("/")
def index():
    """Render main UI."""
    return render_template("index.html")


@app.route("/api/sign", methods=["POST"])
def api_sign():
    """Handle signing request."""
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"}), 400

    keyid = request.form.get("keyid", "").strip()
    if not keyid:
        return jsonify({"success": False, "error": "GPG Key ID is required"}), 400

    try:
        # Save uploaded file
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # Determine output zip name
        out_zip = os.path.join(
            app.config["UPLOAD_FOLDER"], f"signed_{Path(file.filename).stem}.zip"
        )

        # Sign it using core logic
        sign_media(filepath=filepath, out_zip=out_zip, gpg_home=DEFAULT_GPG_HOME, keyid=keyid)

        # We can either return the file or just an info object
        # Returning the downloaded file via URL route is better, but this is a simple UI
        return send_file(
            out_zip, as_attachment=True, download_name=f"signed_{Path(file.filename).stem}.zip"
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/verify", methods=["POST"])
def api_verify():
    """Handle verification request."""
    if "zip_file" not in request.files or "media_file" not in request.files:
        return jsonify({"success": False, "error": "Missing zip_file or media_file"}), 400

    zip_file = request.files["zip_file"]
    media_file = request.files["media_file"]

    if zip_file.filename == "" or media_file.filename == "":
        return jsonify({"success": False, "error": "Both files must be selected"}), 400

    try:
        zip_path = os.path.join(app.config["UPLOAD_FOLDER"], zip_file.filename)
        media_path = os.path.join(app.config["UPLOAD_FOLDER"], media_file.filename)

        zip_file.save(zip_path)
        media_file.save(media_path)

        valid, msg = verify_media(
            zip_path=zip_path, target_media_path=media_path, gpg_home=DEFAULT_GPG_HOME
        )

        return jsonify({"success": True, "valid": valid, "message": msg})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def run_web_app(host="127.0.0.1", port=5000):
    """Run the Flask development server."""
    app.run(host=host, port=port, debug=True)

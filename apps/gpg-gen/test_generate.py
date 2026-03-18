import subprocess
import os
import shutil
import tempfile
import stat
import pytest

SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "generate.sh"))

@pytest.fixture
def mock_env():
    """Provides an isolated environment with a mocked gpg."""
    temp_dir = tempfile.mkdtemp()
    
    # Create a mock gpg executable
    mock_gpg_path = os.path.join(temp_dir, "gpg")
    with open(mock_gpg_path, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write("if [[ \"$*\" == *\"--export\"* ]]; then \n")
        f.write("  # Extract the requested export path from args using robust loop\n")
        f.write("  last_arg=\"${@:-1}\"\n")
        f.write("  # In our script, the mock just touches the pubkey path provided to --output\n")
        f.write("  for arg in \"$@\"; do\n")
        f.write("    if [[ \"$arg\" == *.asc ]]; then\n")
        f.write("      touch \"$arg\"\n")
        f.write("    fi\n")
        f.write("  done\n")
        f.write("fi\n")
        f.write("exit 0\n")
    
    # Make executable
    os.chmod(mock_gpg_path, stat.S_IRWXU)
    
    env = os.environ.copy()
    env["PATH"] = f"{temp_dir}:{env.get('PATH', '')}"
    env["HOME"] = temp_dir
    env["GNUPGHOME"] = os.path.join(temp_dir, ".gnupg")
    
    yield env, temp_dir
    
    shutil.rmtree(temp_dir)

# --- Unit Tests ---
def test_missing_args(mock_env):
    """Test behavior when required arguments are missing."""
    env, _ = mock_env
    result = subprocess.run([SCRIPT_PATH], capture_output=True, text=True, env=env)
    assert result.returncode == 1
    assert "Error:" in result.stderr

def test_missing_value_for_arg(mock_env):
    """Test behavior when an argument is missing its value."""
    env, _ = mock_env
    result = subprocess.run([SCRIPT_PATH, "--name"], capture_output=True, text=True, env=env)
    assert result.returncode == 1
    assert "Error:" in result.stderr

def test_help_flag(mock_env):
    """Test that the help output works correctly."""
    env, _ = mock_env
    result = subprocess.run([SCRIPT_PATH, "--help"], capture_output=True, text=True, env=env)
    assert result.returncode == 0
    assert "Usage: ./generate.sh [OPTIONS]" in result.stdout

# --- Integration Tests ---
def test_integration_generate(mock_env):
    """Test generating a key pair mock flow using non-interactive flag."""
    env, temp_dir = mock_env
    out_dir = os.path.join(temp_dir, "keys")
    
    result = subprocess.run([
        SCRIPT_PATH, 
        "--name", "Integration User", 
        "--email", "integration@test.local", 
        "--out", out_dir,
        "--non-interactive"
    ], capture_output=True, text=True, env=env)
    
    # The return code should be 0 signifying success
    assert result.returncode == 0
    assert "Success! Public key auto-exported" in result.stdout
    
    # Check if config was generated
    assert os.path.exists(os.path.join(env["GNUPGHOME"], "gpg.conf"))
    # Check if mock exported key exists
    assert os.path.exists(os.path.join(out_dir, "integration@test.local_pub.asc"))

# --- Smoke Test ---
@pytest.mark.smoke
def test_smoke_real_gpg():
    """Test actual execution of the GPG CLI if it exists on the host system."""
    if shutil.which("gpg") is None:
        pytest.skip("GPG not installed on host, skipping smoke test")
    
    temp_dir = tempfile.mkdtemp()
    env = os.environ.copy()
    env["HOME"] = temp_dir
    env["GNUPGHOME"] = os.path.join(temp_dir, ".gnupg")
    
    out_dir = os.path.join(temp_dir, "smoke_keys")
    
    try:
        result = subprocess.run([
            SCRIPT_PATH, 
            "--name", "Smoke User", 
            "--email", "smoke@example.com", 
            "--out", out_dir,
            "--non-interactive"
        ], capture_output=True, text=True, env=env)
        
        assert result.returncode == 0
        assert "Generating standard Ed25519/Cv25519 keys" in result.stdout
        assert "Success! Public key auto-exported" in result.stdout
        
        pubkey_path = os.path.join(out_dir, "smoke@example.com_pub.asc")
        assert os.path.exists(pubkey_path)
        
        # Look for armor string inside
        with open(pubkey_path) as f:
            content = f.read()
            assert "-----BEGIN PGP PUBLIC KEY BLOCK-----" in content
            
    finally:
        shutil.rmtree(temp_dir)

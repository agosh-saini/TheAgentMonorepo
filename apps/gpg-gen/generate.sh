#!/usr/bin/env bash
set -euo pipefail

# Security defaults to enforce on GNUPG environment
GPG_CONF_APPEND="personal-cipher-preferences AES256 AES192 AES
personal-digest-preferences SHA512 SHA384 SHA256
personal-compress-preferences ZLIB BZIP2 ZIP Uncompressed
default-preference-list SHA512 SHA384 SHA256 AES256 AES192 AES ZLIB BZIP2 ZIP Uncompressed
cert-digest-algo SHA512
s2k-cipher-algo AES256
s2k-digest-algo SHA512"

function display_usage() {
    echo "Usage: ./generate.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --name <string>      Full Name for the GPG key (required)"
    echo "  --email <string>     Email for the GPG key (required)"
    echo "  --out <dir>          Output directory for the exported public key (default: ./keys)"
    echo "  --non-interactive    Skip entropy gathering (useful for testing or automated environments)"
    echo "  --help               Display this help message"
}

function gather_entropy() {
    local non_interactive="${1:-0}"
    if [[ "${non_interactive}" == "1" ]]; then
        return 0
    fi
    echo -e "\n[SECURITY] To ensure a cryptographically secure foundation, we need to gather entropy."
    echo "Please move your mouse around vigorously or type some random keys..."
    
    local entropy_keys
    read -rsn 20 -p "Press any 20 random keys...: " entropy_keys
    echo -e "\n\nSuccess! Entropy gathered."
}

function check_dependencies() {
    if ! command -v gpg >/dev/null 2>&1; then
        echo "Error: 'gpg' is not installed. Please install GnuPG to use this tool." >&2
        return 1
    fi
    return 0
}

function configure_gpg_security() {
    local gnupg_home="${1}"
    mkdir -p "${gnupg_home}"
    chmod 700 "${gnupg_home}"
    local conf_file="${gnupg_home}/gpg.conf"
    
    # Check if preferences already exist
    if [[ ! -f "${conf_file}" ]] || ! grep -q "personal-cipher-preferences" "${conf_file}" 2>/dev/null; then
        echo "$GPG_CONF_APPEND" >> "${conf_file}"
    fi
}

function generate_key() {
    local name="${1}"
    local email="${2}"
    local out_dir="${3}"
    local non_interactive="${4}"

    local gpg_home="${HOME}/.gnupg"
    export GNUPGHOME="${gpg_home}"

    if ! check_dependencies; then
        exit 1
    fi
    configure_gpg_security "${gpg_home}"
    gather_entropy "${non_interactive}"

    local spec_tmp
    spec_tmp=$(mktemp)
    
    cat <<EOF > "${spec_tmp}"
Key-Type: EDDSA
Key-Curve: ed25519
Key-Usage: sign
Subkey-Type: ECDH
Subkey-Curve: cv25519
Subkey-Usage: encrypt
Name-Real: ${name}
Name-Email: ${email}
Expire-Date: 0
%no-protection
%commit
EOF

    echo -e "\nGenerating standard Ed25519/Cv25519 keys for ${name} <${email}>..."
    # Suppress most output but keep errors
    gpg --batch --generate-key "${spec_tmp}" >/dev/null

    rm -f "${spec_tmp}"

    mkdir -p "${out_dir}"
    local pubkey_path="${out_dir}/${email}_pub.asc"
    gpg --output "${pubkey_path}" --armor --export "${email}" >/dev/null
    
    echo -e "\nSuccess! Public key auto-exported to: ${pubkey_path}"
    echo "Note: The private key is securely stored in your active GPG keyring (${GNUPGHOME})."
}

function main() {
    local name=""
    local email=""
    local out_dir="./keys"
    local non_interactive="0"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --name) 
                name="${2:-}"
                if [[ -z "${name}" || "${name}" == --* ]]; then
                    echo "Error: --name requires a non-empty string." >&2
                    exit 1
                fi
                shift 2 
                ;;
            --email) 
                email="${2:-}"
                if [[ -z "${email}" || "${email}" == --* ]]; then
                    echo "Error: --email requires a non-empty string." >&2
                    exit 1
                fi
                shift 2 
                ;;
            --out) 
                out_dir="${2:-}"
                shift 2 
                ;;
            --non-interactive) 
                non_interactive="1"
                shift 1 
                ;;
            --help)
                display_usage
                exit 0
                ;;
            *) 
                echo "Unknown parameter: ${1}" >&2
                display_usage >&2
                exit 1 
                ;;
        esac
    done

    # Validation
    if [[ -z "${name}" || -z "${email}" ]]; then
        echo "Error: Both --name and --email are required." >&2
        display_usage >&2
        exit 1
    fi

    generate_key "${name}" "${email}" "${out_dir}" "${non_interactive}"
}

# Run main if the script is executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

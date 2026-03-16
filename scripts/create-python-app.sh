#!/usr/bin/env bash
# Usage: bash scripts/create-python-app.sh <project-name>
set -e

NAME="${1:?Usage: create-python-app.sh <project-name>}"
DEST="apps/python/$NAME"

if [ -d "$DEST" ]; then
  echo "Error: $DEST already exists" && exit 1
fi

mkdir -p "$DEST/src/$NAME" "$DEST/tests"
touch "$DEST/src/$NAME/__init__.py" "$DEST/tests/__init__.py"

cat > "$DEST/README.md" <<EOF
# $NAME

> Describe what this project does.

## Run

\`\`\`bash
cd $DEST
uv sync
uv run python src/$NAME/main.py
\`\`\`

## Test

\`\`\`bash
uv run pytest tests/
\`\`\`
EOF

cat > "$DEST/.env.example" <<EOF
ANTHROPIC_API_KEY=
EOF

cd "$DEST" && uv init --python 3.11 --name "$NAME" 2>/dev/null || true
echo "Created $DEST"

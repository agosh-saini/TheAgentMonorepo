#!/usr/bin/env bash
# Usage: bash scripts/create-fullstack-app.sh <project-name>
set -e

NAME="${1:?Usage: create-fullstack-app.sh <project-name>}"
DEST="apps/fullstack/$NAME"

if [ -d "$DEST" ]; then
  echo "Error: $DEST already exists" && exit 1
fi

mkdir -p "$DEST/backend/src" "$DEST/backend/tests"
mkdir -p "$DEST/frontend/src/app" "$DEST/frontend/tests"
touch "$DEST/backend/src/.gitkeep" "$DEST/backend/tests/.gitkeep"
touch "$DEST/frontend/src/app/.gitkeep" "$DEST/frontend/tests/.gitkeep"

cat > "$DEST/README.md" <<EOF
# $NAME

> Describe what this project does.

## Backend

\`\`\`bash
cd $DEST/backend && uv sync && uv run python src/main.py
\`\`\`

## Frontend

\`\`\`bash
cd $DEST/frontend && npm install && npm run dev
\`\`\`
EOF

cat > "$DEST/.env.example" <<EOF
ANTHROPIC_API_KEY=
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

echo "Created $DEST"

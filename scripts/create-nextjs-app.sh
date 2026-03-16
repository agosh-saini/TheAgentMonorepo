#!/usr/bin/env bash
# Usage: bash scripts/create-nextjs-app.sh <project-name>
set -e

NAME="${1:?Usage: create-nextjs-app.sh <project-name>}"
DEST="apps/nextjs/$NAME"

if [ -d "$DEST" ]; then
  echo "Error: $DEST already exists" && exit 1
fi

mkdir -p "$DEST/src/app" "$DEST/tests"
touch "$DEST/src/app/.gitkeep" "$DEST/tests/.gitkeep"

cat > "$DEST/README.md" <<EOF
# $NAME

> Describe what this project does.

## Run

\`\`\`bash
cd $DEST
npm install
npm run dev
\`\`\`
EOF

cat > "$DEST/.env.example" <<EOF
ANTHROPIC_API_KEY=
NEXT_PUBLIC_APP_NAME=$NAME
EOF

echo "Created $DEST"
echo "Run: cd $DEST && npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --no-git"

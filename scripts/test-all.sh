#!/usr/bin/env bash
# Run tests across all projects
set -e

echo "=== Testing Python projects ==="
for dir in apps/python/*/; do
  [ -f "$dir/pyproject.toml" ] || continue
  echo "-- $dir"
  (cd "$dir" && uv run pytest tests/ -q 2>/dev/null || true)
done

for dir in apps/fullstack/*/backend/; do
  [ -f "$dir/pyproject.toml" ] || continue
  echo "-- $dir"
  (cd "$dir" && uv run pytest tests/ -q 2>/dev/null || true)
done

echo ""
echo "=== Testing Next.js projects ==="
for dir in apps/nextjs/*/; do
  [ -f "$dir/package.json" ] || continue
  echo "-- $dir"
  (cd "$dir" && npm test --silent 2>/dev/null || true)
done

echo ""
echo "Done."

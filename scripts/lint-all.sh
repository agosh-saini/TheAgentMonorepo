#!/usr/bin/env bash
# Lint all Python and Next.js projects
set -e

echo "=== Linting Python projects ==="
for dir in apps/python/*/; do
  [ -f "$dir/pyproject.toml" ] || continue
  echo "-- $dir"
  (cd "$dir" && uv run ruff check src/ tests/ 2>/dev/null || true)
done

for dir in apps/fullstack/*/backend/; do
  [ -f "$dir/pyproject.toml" ] || continue
  echo "-- $dir"
  (cd "$dir" && uv run ruff check src/ tests/ 2>/dev/null || true)
done

echo ""
echo "=== Linting Next.js projects ==="
for dir in apps/nextjs/*/; do
  [ -f "$dir/package.json" ] || continue
  echo "-- $dir"
  (cd "$dir" && npm run lint --silent 2>/dev/null || true)
done

for dir in apps/fullstack/*/frontend/; do
  [ -f "$dir/package.json" ] || continue
  echo "-- $dir"
  (cd "$dir" && npm run lint --silent 2>/dev/null || true)
done

echo ""
echo "Done."

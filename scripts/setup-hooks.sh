#!/bin/bash
# Setup script for pre-commit hooks (backend and frontend)

set -e

echo "=========================================="
echo "Setting up pre-commit hooks"
echo "=========================================="

# Check if running from project root
if [ ! -f "compose.yaml" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Setup backend pre-commit hooks
echo ""
echo "1. Setting up backend pre-commit hooks..."
echo "----------------------------------------"

if command -v pip &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit

    echo "Installing pre-commit hooks..."
    pre-commit install

    echo "Running pre-commit on all files (first time)..."
    pre-commit run --all-files || true

    echo "✓ Backend pre-commit hooks installed successfully"
else
    echo "Warning: pip not found. Skipping backend pre-commit setup."
    echo "Please install Python and pip, then run: pip install pre-commit && pre-commit install"
fi

# Setup frontend husky hooks
echo ""
echo "2. Setting up frontend husky hooks..."
echo "----------------------------------------"

if command -v npm &> /dev/null; then
    echo "Installing husky and lint-staged..."
    cd ui
    npm install

    echo "Initializing husky..."
    npm run prepare

    echo "✓ Frontend husky hooks installed successfully"
    cd ..
else
    echo "Warning: npm not found. Skipping frontend husky setup."
    echo "Please install Node.js and npm, then run: cd ui && npm install && npm run prepare"
fi

echo ""
echo "=========================================="
echo "Pre-commit hooks setup completed!"
echo "=========================================="
echo ""
echo "Backend: pre-commit will run Ruff (linter/formatter) and mypy (type checker)"
echo "Frontend: husky will run ESLint and Prettier via lint-staged"
echo ""
echo "To manually run hooks:"
echo "  Backend: pre-commit run --all-files"
echo "  Frontend: cd ui && npx lint-staged"
echo ""

# Development Environment Setup

**Last Updated**: 2025-12-28

## Purpose

This document describes the setup process for the development environment of the Minecraft Server Dashboard project.

## Prerequisites

Before setting up the development environment, ensure you have the following installed:

### Required

- **Docker**: Version 20.10+ with Docker Compose V2
- **Git**: Version 2.30+
- **Text Editor/IDE**: VS Code, IntelliJ IDEA, or similar

### Optional (for local development without Docker)

- **Python**: 3.13+
- **uv**: Latest version (Python package manager)
- **Node.js**: 20.0+
- **npm**: 10.0+
- **PostgreSQL**: 16+

## Project Structure

```
mc-server-dashboard/
├── api/                          # Backend (Python + FastAPI)
│   ├── src/app/                  # Application code
│   ├── tests/                    # Test code
│   ├── alembic/                  # Database migrations
│   ├── pyproject.toml            # Python dependencies and tool configs
│   ├── alembic.ini               # Alembic configuration
│   ├── Dockerfile                # Backend container definition
│   └── .dockerignore
│
├── ui/                           # Frontend (Next.js + React)
│   ├── src/app/                  # App Router structure
│   ├── public/                   # Static files
│   ├── package.json              # npm dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   ├── next.config.ts            # Next.js configuration
│   ├── .eslintrc.json            # ESLint configuration
│   ├── .prettierrc.json          # Prettier configuration
│   ├── vitest.config.ts          # Vitest configuration
│   ├── Dockerfile                # Frontend container definition
│   └── .dockerignore
│
├── docs/                         # Documentation
├── compose.yaml                  # Docker Compose V2 configuration
├── .env.example                  # Environment variable template
└── .gitignore
```

## Quick Start (Docker Compose - Recommended)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mc-server-dashboard
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and update values as needed (optional for development).

### 3. Start All Services

```bash
docker compose up -d
```

This will start:
- **PostgreSQL** on port 5432
- **Backend API** on port 8000
- **Frontend UI** on port 3000

### 4. Verify Services

```bash
docker compose ps
```

All services should show "Up" status.

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 6. View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f ui
```

### 7. Stop Services

```bash
docker compose down
```

To remove volumes as well (database data):

```bash
docker compose down -v
```

---

## Local Development Setup (Without Docker)

### Backend (Python + FastAPI)

#### 1. Navigate to API Directory

```bash
cd api
```

#### 2. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 3. Create Virtual Environment and Install Dependencies

```bash
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

uv pip install -e ".[dev]"
```

#### 4. Set Environment Variables

```bash
export DATABASE_URL="postgresql+asyncpg://mcadmin:mcpassword@localhost:5432/mc_dashboard"
export SECRET_KEY="your-secret-key-change-in-production"
```

#### 5. Start PostgreSQL (if not using Docker)

Ensure PostgreSQL 16+ is running locally on port 5432.

#### 6. Run Database Migrations

```bash
alembic upgrade head
```

#### 7. Start Development Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 8. Run Tests

```bash
pytest
```

#### 9. Run Linter and Formatter

```bash
ruff check .
ruff format .
```

#### 10. Type Checking

```bash
mypy app
```

---

### Frontend (Next.js + React)

#### 1. Navigate to UI Directory

```bash
cd ui
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Set Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 4. Start Development Server

```bash
npm run dev
```

#### 5. Run Tests

```bash
npm run test
```

#### 6. Run Linter

```bash
npm run lint
```

#### 7. Run Formatter

```bash
npm run format
```

#### 8. Type Checking

```bash
npm run type-check
```

#### 9. Build for Production

```bash
npm run build
npm start
```

---

## Database Management

### Access PostgreSQL

```bash
# Using Docker Compose
docker compose exec postgres psql -U mcadmin -d mc_dashboard

# Local PostgreSQL
psql -U mcadmin -d mc_dashboard
```

### Create New Migration

```bash
cd api
alembic revision --autogenerate -m "description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

---

## Common Development Tasks

### Rebuild Docker Images

```bash
docker compose build
docker compose up -d
```

### Reset Database

```bash
docker compose down -v
docker compose up -d
```

### Add Python Dependency

```bash
cd api
uv pip install <package-name>
# Update pyproject.toml manually
```

### Add npm Dependency

```bash
cd ui
npm install <package-name>
```

---

## Troubleshooting

### Port Already in Use

If ports 3000, 5432, or 8000 are already in use, you can change them in `.env`:

```bash
API_PORT=8001
UI_PORT=3001
POSTGRES_PORT=5433
```

### Docker Socket Permission Denied

Ensure your user is in the `docker` group:

```bash
sudo usermod -aG docker $USER
```

Then log out and log back in.

### Database Connection Refused

Ensure PostgreSQL is running and accessible:

```bash
docker compose ps postgres
docker compose logs postgres
```

### Hot Reload Not Working

If file changes aren't detected in Docker:

```bash
# Rebuild and restart
docker compose down
docker compose build
docker compose up -d
```

---

## IDE Setup Recommendations

### VS Code

Recommended extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- Docker (ms-azuretools.vscode-docker)

### PyCharm / IntelliJ IDEA

1. Enable Python plugin
2. Set Python interpreter to `.venv/bin/python`
3. Enable Ruff for formatting and linting
4. Enable Prettier for TypeScript formatting

---

## CI Environment Setup

### Pre-commit Hooks

Pre-commit hooks ensure code quality before commits. They run linters, formatters, and type checkers automatically.

#### Automated Setup (Recommended)

Run the setup script from the project root:

```bash
./scripts/setup-hooks.sh
```

This script will:
1. Install and configure backend pre-commit hooks (Ruff, mypy)
2. Install and configure frontend husky hooks (ESLint, Prettier)
3. Run initial checks on all files

#### Manual Setup

**Backend (pre-commit):**

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run on all files (optional)
pre-commit run --all-files
```

**Frontend (husky + lint-staged):**

```bash
cd ui

# Install dependencies (includes husky and lint-staged)
npm install

# Initialize husky
npm run prepare
```

### What Gets Checked

**Backend (on commit):**
- Ruff linter and formatter (Python code style)
- mypy type checker (static type checking)
- General file checks (trailing whitespace, YAML/JSON syntax)

**Frontend (on commit):**
- ESLint (TypeScript/React linting)
- Prettier (code formatting)
- Only staged files are checked

### GitHub Actions CI

All pushes and pull requests trigger automated CI checks:

#### Backend CI (`backend-ci.yml`)
- Linting with Ruff
- Type checking with mypy
- Unit tests with pytest
- Coverage check (≥75% required)

#### Frontend CI (`frontend-ci.yml`)
- Linting with ESLint
- Format checking with Prettier
- Type checking with TypeScript
- Unit tests with Vitest
- Coverage check (≥75% required)
- Build verification with Next.js

#### Docker CI (`docker-ci.yml`)
- Docker Compose build verification
- Service health checks (API, UI, PostgreSQL)
- Dockerfile linting with hadolint

### Running CI Checks Locally

**Backend:**

```bash
cd api

# Linting
ruff check .

# Formatting check
ruff format --check .

# Type checking
mypy src/

# Tests with coverage
pytest --cov --cov-report=term-missing
```

**Frontend:**

```bash
cd ui

# Linting
npm run lint

# Format checking
npm run format:check

# Type checking
npm run type-check

# Tests with coverage
npm run test:coverage

# Build
npm run build
```

**Docker:**

```bash
# Build and verify all services
docker compose build
docker compose up -d

# Check health
curl http://localhost:8000/health
curl http://localhost:3000

# View logs
docker compose logs

# Cleanup
docker compose down -v
```

### Coverage Requirements

- **Target**: 95% (aspirational goal from ARCHITECTURE.md)
- **CI Minimum**: 75% (enforced in GitHub Actions)
- **Current Reality**: 75-80% (per CLAUDE.md)

Coverage below 75% will cause CI to fail.

### Troubleshooting CI

**Pre-commit hooks failing:**

```bash
# Update hooks to latest version
pre-commit autoupdate

# Clear cache and retry
pre-commit clean
pre-commit run --all-files
```

**Husky not running:**

```bash
cd ui
rm -rf .husky
npm run prepare
```

**CI failing but passes locally:**

- Ensure you've committed all changes
- Check that dependencies in `pyproject.toml` and `package.json` are up to date
- Verify `.github/workflows/*.yml` syntax

---

## Next Steps

After setting up the development environment:

1. Review [PHILOSOPHY.md](PHILOSOPHY.md) to understand project values
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) to learn about system design
3. Check [CODING_STANDARDS.md](CODING_STANDARDS.md) for code conventions
4. Follow [WORKFLOW.md](WORKFLOW.md) for Git workflow and branching strategy
5. Start implementing features based on specifications in `docs/`

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Status

**IMPORTANT**: This is a **documentation-first** repository. Implementation has NOT begun yet. All code examples in documentation are specifications for future implementation, not actual code.

**Purpose**: Complete redesign and reimplementation of Minecraft Server Dashboard with improved architecture, maintainability, and extensibility.

**Current Phase**: Architecture and specification documentation
**Next Phase**: Implementation will begin once documentation is complete and approved

## Documentation Structure

### Bilingual Requirement

**CRITICAL**: All documentation MUST exist in both English and Japanese with identical structure.

**Naming convention**:
- English: `DOCUMENT_NAME.md`
- Japanese: `DOCUMENT_NAME.ja.md`

**Structural requirements**:
- Main sections (##) must match in count and order
- Subsections (###) numbered 1-N must be identical across languages
- Line counts should be similar (minor variations acceptable for translation)
- "Last Updated" dates must match between language pairs

### Documentation Files

Located in `docs/`:

1. **INDEX.md / INDEX.ja.md** - Documentation index and reading order
2. **PHILOSOPHY.md / PHILOSOPHY.ja.md** - Core values and design principles (158 lines)
3. **ARCHITECTURE.md / ARCHITECTURE.ja.md** - System architecture (1357-1358 lines)
   - 15 main sections (##)
   - 16 numbered feature subsections (###)
   - Includes: Java compatibility matrix, PBAC system (38 permissions), state machine, graceful shutdown
4. **CODING_STANDARDS.md / CODING_STANDARDS.ja.md** - Coding conventions (731 lines)
5. **WORKFLOW.md / WORKFLOW.ja.md** - Git workflow and development process (576 lines)
6. **DEVELOPMENT.md / DEVELOPMENT.ja.md** - Development environment setup (689 lines)
7. **IMPLEMENTATION_GUIDE.md / IMPLEMENTATION_GUIDE.ja.md** - Implementation workflow (878 lines)
   - **CRITICAL for implementation tasks**: Read this before starting any feature implementation
   - Step-by-step workflow from task understanding to merge
   - API-first development (API and UI completely separate)
   - Concrete example: User Registration API implementation

### Verification Commands

Check documentation consistency:

```bash
# Count main sections in all docs (should match per language pair)
grep -c "^## " docs/ARCHITECTURE.md docs/ARCHITECTURE.ja.md

# Count subsections 1-16 in ARCHITECTURE
grep "^### [0-9]" docs/ARCHITECTURE.md | wc -l
grep "^### [0-9]" docs/ARCHITECTURE.ja.md | wc -l

# Verify Last Updated dates match
grep "Last Updated" docs/*.md
grep "最終更新日" docs/*.ja.md
```

## Key Architectural Decisions (Already Documented)

These are **specifications**, not implementation:

### Technology Stack

- **Backend**: Python 3.13+ + FastAPI 0.115+
- **Frontend**: Next.js 15+ (App Router) + React 19+ + TypeScript
- **Database**: PostgreSQL 16+
- **Deployment**: Docker Compose (V2 format - no `version:` field)

### Architecture Patterns

1. **3-tier Architecture**: Complete API/Frontend separation
2. **Strategy Pattern**:
   - Server Launch Strategies: HostProcessStrategy, DockerInDockerStrategy, DockerOutOfDockerStrategy
   - System-wide configuration (not per-server)
3. **Permission-Based Access Control (PBAC)**:
   - 38 permissions across 7 categories
   - Permission calculation: `(Role Permissions ∪ User Granted) - User Denied`
4. **Server State Machine**: 5 states (stopped, starting, running, stopping, unknown) - NO error state
5. **Unified Snapshot System**: Common versioning for files and world backups

### Critical Implementation Requirements

- **Package Manager**: uv (Python package management)
- **Test Coverage**: Target ≥95% (current reality: 75-80%)
- **Type Safety**: Required for all Python functions, strict TypeScript mode
- **Code Formatting**: Ruff (Python), Prettier (TypeScript) - line length 100
- **Linting**: Ruff (Python), ESLint (TypeScript)
- **Java Compatibility Matrix**: Only applies to HostProcessStrategy (5 Java versions: 7, 8, 16, 17, 21)

## Git Workflow

### Branching Strategy: Release Flow

- `main` - Active development (functional but not production-ready)
- `feature/*`, `fix/*`, `docs/*`, `refactor/*`, `test/*` - Short-lived branches
- `release/x.y.z` - Stable releases (long-lived, never deleted)

**Branch naming**: `<type>/<brief-description>` (lowercase, hyphen-separated)

### Commit Convention: Conventional Commits

Format: `<type>(<scope>): <description>`

**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`

**Auto-appended footer** (for all commits):
```
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

Use HEREDOC for multi-line commit messages:
```bash
git commit -m "$(cat <<'EOF'
docs(architecture): description here

Details...

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

## Common Development Commands

### Environment Setup

```bash
# Start all services (recommended for development)
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f          # All services
docker compose logs -f api      # Backend only
docker compose logs -f ui       # Frontend only

# Stop all services
docker compose down

# Stop and remove volumes (reset database)
docker compose down -v
```

### Backend (Python/FastAPI)

```bash
cd api

# Code quality checks (run before commit)
ruff check .                    # Linting
ruff format .                   # Formatting
mypy src/                       # Type checking

# Testing
pytest                          # Run all tests
pytest --cov                    # With coverage report
pytest --cov --cov-fail-under=75  # Enforce 75% minimum coverage
pytest tests/test_auth.py       # Run single test file
pytest tests/test_auth.py::test_register_success  # Run single test

# Database migrations
alembic revision --autogenerate -m "description"  # Create migration
alembic upgrade head            # Apply migrations
alembic downgrade -1            # Rollback one migration
alembic history                 # List all migrations

# Development server (if not using Docker)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Next.js/React/TypeScript)

```bash
cd ui

# Code quality checks (run before commit)
npm run lint                    # ESLint
npm run format                  # Prettier
npm run type-check              # TypeScript

# Testing
npm run test                    # Run all tests
npm run test:coverage           # With coverage report
npm run test -- path/to/test.tsx  # Run single test

# Build
npm run build                   # Production build
npm run start                   # Start production server

# Development server (if not using Docker)
npm run dev
```

### Documentation Verification

```bash
# Verify bilingual documentation structure
grep -c "^## " docs/IMPLEMENTATION_GUIDE.md docs/IMPLEMENTATION_GUIDE.ja.md

# Check line counts (should be similar)
wc -l docs/IMPLEMENTATION_GUIDE.md docs/IMPLEMENTATION_GUIDE.ja.md

# Verify Last Updated dates match
grep "Last Updated\|最終更新日" docs/IMPLEMENTATION_GUIDE.md docs/IMPLEMENTATION_GUIDE.ja.md
```

## Implementation Workflow Overview

**CRITICAL**: Before implementing any feature, follow the workflow in `docs/IMPLEMENTATION_GUIDE.md`.

### Quick Reference

**When you receive an implementation task** (e.g., "Create user registration API"):

1. **Step 0: Task Understanding** (MUST DO FIRST)
   - Check current Git branch (`git branch`) - never work on `main`
   - Create/switch to feature branch: `git checkout -b feature/api-<name>`
   - Clarify requirements - ask questions if anything is unclear
   - Review ARCHITECTURE.md for specifications
   - Search for existing similar implementations
   - Confirm scope with stakeholder

2. **Step 1: Task Analysis**
   - Determine: API only / UI only / Both (separate PRs)
   - Check if database migration needed
   - Identify dependencies

3. **Step 2: API Implementation** (if applicable)
   - Branch: `feature/api-<name>`
   - Create Alembic migration (if needed)
   - Implement: Pydantic schemas → DB models → Services → Endpoints → Tests
   - Target 95% coverage (minimum 75%)
   - Run quality checks: `ruff check . && ruff format . && mypy src/ && pytest --cov`
   - Create PR, wait for CI, merge with "Squash and merge"

4. **Step 3: UI Implementation** (separate task, separate PR)
   - Branch: `feature/ui-<name>`
   - Wait for API PR to be merged first
   - Implement: TypeScript types → API client → Components → Tests
   - Run quality checks: `npm run lint && npm run format && npm run type-check && npm run test`
   - Create PR, wait for CI, merge with "Squash and merge"

5. **Step 4: Integration**
   - Manual testing with `docker compose up -d`
   - Update documentation if needed

**Key Principles**:
- Never guess requirements - always ask when uncertain
- API and UI are completely separate (different branches, different PRs)
- ARCHITECTURE.md is the source of truth
- Tests are mandatory (minimum 75%, aim for 95%)
- Never commit directly to `main`

## External Reference Repositories

**CRITICAL UNDERSTANDING**: Two symlinked directories exist for **reference purposes ONLY**:

- `mc-server-dashboard-api/` → [External Python/FastAPI repo](https://github.com/mmiura-2351/mc-server-dashboard-api)
- `mc-server-dashboard-ui/` → [External Next.js/React repo](https://github.com/mmiura-2351/mc-server-dashboard-ui)

**These are used ONLY to**:
- Verify existing feature specifications
- Provide feature list reference

**These are NOT used for**:
- Design decisions in this project
- Architectural patterns
- Implementation references

**This project is designed and implemented completely from scratch**, independent of external repositories.

## Documentation Editing Guidelines

### When modifying ARCHITECTURE.md or ARCHITECTURE.ja.md

1. **Always update both language versions** with equivalent content
2. **Maintain section numbering**: Features are numbered 1-16
3. **Update "Last Updated" date** to current date (YYYY-MM-DD)
4. **Verify structure consistency** after changes:
   ```bash
   # Should output identical counts
   grep -c "^## " docs/ARCHITECTURE.md docs/ARCHITECTURE.ja.md
   ```

### When adding new documentation

1. **Create both .md and .ja.md versions simultaneously**
2. **Update INDEX.md and INDEX.ja.md** to include the new document
3. **Update README.md** if the new doc is important for getting started

### Docker Compose

- Use V2 format (NO `version: '3.8'` field)
- Example in ARCHITECTURE.md sections use clean format:
  ```yaml
  services:
    postgres:
      image: postgres:16
  ```

## Common Pitfalls to Avoid

1. **DO NOT work directly on `main` branch** - always create a feature branch first
2. **DO NOT assume code exists** - treat all code examples in docs as specifications
3. **DO NOT reference the external repositories** for design decisions
4. **DO NOT modify only one language version** - always update pairs
5. **DO NOT implement API and UI in the same branch/PR** - separate branches, separate PRs
6. **DO NOT skip Step 0 (Task Understanding)** - always clarify requirements before coding
7. **DO NOT guess requirements** - ask questions when uncertain

## Philosophy and Design Principles

**Read PHILOSOPHY.md first** to understand:
- Why we are reimplementing (insufficient design in previous version)
- Core values: Maintainability > Extensibility > Performance > Reliability
- Testability-first approach
- Code consistency via automated tooling

**Key principle**: "Sufficient time and effort spent on initial design and planning" - this documentation phase is critical to avoid previous mistakes.

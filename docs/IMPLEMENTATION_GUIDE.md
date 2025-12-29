# Implementation Guide

**Last Updated**: 2025-12-30

## Purpose

This document provides a step-by-step guide for implementing features in the Minecraft Server Dashboard project. It defines the workflow from receiving a task to merging the implementation, with emphasis on understanding requirements before coding.

## Core Principles

1. **Understand before implementing**: Always clarify requirements and review current state before writing code
2. **API-first development**: Implement and merge API before UI (complete separation)
3. **Ask when uncertain**: Never proceed based on assumptions - always ask for clarification
4. **Follow specifications**: ARCHITECTURE.md is the source of truth for feature specifications
5. **Test coverage matters**: Aim for 95% coverage (minimum 75% enforced by CI)

## Implementation Workflow

### Step 0: Task Understanding and Current State Review

**This is a REQUIRED step before any implementation.**

#### 0-1. Clarify the Task

Before starting implementation, ensure you understand:

- [ ] **Purpose**: Why is this feature needed? What problem does it solve?
- [ ] **Requirements**: What exactly needs to be implemented?
- [ ] **Definition of Done**: What constitutes completion of this task?
- [ ] **Scope**: What is included/excluded from this task?
- [ ] **Constraints**: Are there any technical constraints or dependencies?

**IMPORTANT**: If anything is unclear, **ask questions immediately**. Do not guess or assume.

#### 0-2. Review Current State

**Check Git Branch Status**:
```bash
# Check current branch
git branch

# Check repository status
git status

# Check for uncommitted changes
git diff
git diff --staged
```

- [ ] What branch am I currently on?
  - ❌ On `main` → **STOP! Never commit directly to main**
  - ❌ On wrong feature branch → Switch to correct branch or create new one
  - ✅ On correct feature branch → Proceed with implementation
  - ✅ On `main` but need to create new branch → Create feature branch (see below)

- [ ] Are there uncommitted changes?
  - ✅ Yes, from current task → Good, continue working
  - ❌ Yes, from different task → Commit or stash them first
  - ✅ No changes → Clean state, ready to start

**Create or switch to appropriate branch** (if needed):
```bash
# If on main and need to create new feature branch
git checkout main
git pull origin main
git checkout -b feature/api-<feature-name>

# If need to switch to existing branch
git checkout feature/api-<feature-name>
git pull origin feature/api-<feature-name>  # Get latest changes if pushed

# If have uncommitted changes and need to switch branches
git stash                          # Temporarily save changes
git checkout <target-branch>
git stash pop                      # Restore changes (if applicable)
```

**Branch naming reference** (from WORKFLOW.md):
- `feature/<brief-description>` - New features
- `fix/<brief-description>` - Bug fixes
- `refactor/<brief-description>` - Code refactoring
- `docs/<brief-description>` - Documentation updates
- `test/<brief-description>` - Test improvements

**Check Specifications**:
```bash
# Review ARCHITECTURE.md for feature specifications
grep -n "<feature-keyword>" docs/ARCHITECTURE.md

# Check if feature is already documented
grep -rn "<feature-keyword>" docs/
```

- [ ] Is this feature specified in ARCHITECTURE.md?
  - ✅ Yes → Follow the specification exactly
  - ❌ No → Request specification before implementation

**Check Existing Code**:
```bash
# Search for related implementations (backend)
grep -rn "<feature-keyword>" api/src/

# Search for related implementations (frontend)
grep -rn "<feature-keyword>" ui/src/

# Check existing database schema
ls -la api/alembic/versions/
```

- [ ] Are there similar features already implemented?
  - ✅ Yes → Follow existing patterns (naming, structure, testing)
  - ❌ No → This is a new pattern (ensure alignment with architecture)

**Check Database State**:
```bash
# List existing migrations
alembic history

# Check current schema
docker compose exec postgres psql -U mcadmin -d mc_dashboard -c "\dt"
```

- [ ] Does the required database table/column exist?
  - ✅ Yes → Reuse existing schema
  - ❌ No → Migration creation required

**Check Dependencies**:

- [ ] Does this feature depend on other features?
  - ✅ Yes → Ensure dependencies are implemented first
  - ❌ No → Proceed with implementation

#### 0-3. Confirm Scope with Stakeholders

Based on your review, confirm the implementation scope:

```markdown
Task: Implement <feature-name>

Current State:
- ARCHITECTURE.md specification: [Found/Not Found]
- Existing related code: [List files]
- Database schema: [Exists/Needs creation]

Proposed Scope:
1. [Task component 1]
2. [Task component 2]
3. [Task component 3]

Questions:
1. [Question 1]
2. [Question 2]

Is this scope correct?
```

### Step 1: Task Analysis

After understanding the task, analyze the implementation approach:

#### 1-1. Determine Implementation Type

- [ ] **API only**: Backend implementation (Python/FastAPI)
- [ ] **UI only**: Frontend implementation (Next.js/React/TypeScript)
- [ ] **Both**: API first, then UI (separate branches, separate PRs)

**IMPORTANT**: API and UI are **completely separate**. Never implement both in the same branch/PR.

#### 1-2. Check Database Changes

- [ ] **New table required**: Create Alembic migration
- [ ] **New column required**: Create Alembic migration
- [ ] **No database changes**: Skip migration creation
- [ ] **Only application logic**: No database work needed

Database schema design is **not a mandatory step** - only required when database changes are needed.

#### 1-3. Identify Dependencies

- [ ] Does this feature require other features to be implemented first?
- [ ] Will this feature be a dependency for future features?
- [ ] Are there any external library dependencies to add?

### Step 2: API Implementation (if applicable)

**Branch naming**: `feature/api-<feature-name>` or `fix/api-<issue-description>`

#### 2-1. Create Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/api-user-registration
```

#### 2-2. Database Migration (if needed)

```bash
cd api

# Create migration
alembic revision --autogenerate -m "add users table for authentication"

# Review generated migration
cat alembic/versions/<revision-id>_add_users_table_for_authentication.py

# Apply migration locally
alembic upgrade head

# Verify schema
docker compose exec postgres psql -U mcadmin -d mc_dashboard -c "\d users"
```

#### 2-3. Implement API Components

**Order of implementation**:

1. **Pydantic models** (`api/src/app/schemas/`)
   - Request schemas (validation)
   - Response schemas (serialization)
   - Add comprehensive field validation

2. **Database models** (`api/src/app/models/`) - if migration created
   - SQLAlchemy models
   - Relationships and constraints

3. **Business logic** (`api/src/app/services/`)
   - Service layer functions
   - Error handling
   - Business rule validation

4. **API endpoints** (`api/src/app/routers/`)
   - FastAPI route handlers
   - OpenAPI documentation
   - HTTP status codes

5. **Unit tests** (`api/tests/`)
   - Test all service functions
   - Test all endpoints
   - Test validation and error cases
   - Target: 95% coverage (minimum 75%)

#### 2-4. Code Quality Checks

```bash
cd api

# Linting
ruff check .

# Formatting
ruff format .

# Type checking
mypy src/

# Run tests with coverage
pytest --cov --cov-report=term-missing

# Ensure coverage is ≥75%
pytest --cov --cov-report=term --cov-fail-under=75
```

#### 2-5. Create Pull Request

```bash
# Commit changes
git add .
git commit -m "$(cat <<'EOF'
feat(api): add user registration endpoint

Implements POST /api/auth/register with:
- User data validation (email, password, username)
- Password hashing with bcrypt
- Admin approval workflow (pending → approved)
- Duplicate email prevention

Database migration: users, roles, permissions tables
Test coverage: 96%

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# Push to remote
git push origin feature/api-user-registration
```

Create PR on GitHub:
- Base branch: `main`
- Title: `feat(api): add user registration endpoint`
- Description: Follow PR template in WORKFLOW.md
- Wait for CI to pass
- Merge using **Squash and merge**
- Delete branch after merge

### Step 3: UI Implementation (if applicable)

**IMPORTANT**: UI implementation is a **separate task** with a **separate branch and PR**.

Only start UI implementation **after** the API PR is merged to `main`.

**Branch naming**: `feature/ui-<feature-name>` or `fix/ui-<issue-description>`

#### 3-1. Create Branch

```bash
git checkout main
git pull origin main  # Get latest API changes
git checkout -b feature/ui-registration-form
```

#### 3-2. Implement UI Components

**Order of implementation**:

1. **TypeScript types** (`ui/src/types/`)
   - API request/response types
   - Component prop types
   - Match backend Pydantic schemas

2. **API client** (`ui/src/lib/api/`)
   - Fetch wrapper functions
   - Error handling
   - Type-safe API calls

3. **React components** (`ui/src/components/`)
   - UI components
   - Form validation
   - Error display

4. **Page integration** (`ui/src/app/`)
   - Integrate components into pages
   - Routing setup
   - Layout updates

5. **Unit tests** (`ui/src/__tests__/`)
   - Component tests
   - API client tests
   - User interaction tests
   - Target: 95% coverage (minimum 75%)

#### 3-3. Code Quality Checks

```bash
cd ui

# Linting
npm run lint

# Formatting
npm run format

# Type checking
npm run type-check

# Run tests with coverage
npm run test:coverage

# Build verification
npm run build
```

#### 3-4. Create Pull Request

```bash
# Commit changes
git add .
git commit -m "$(cat <<'EOF'
feat(ui): add user registration form

Implements registration form with:
- Email, password, username validation
- Password strength indicator
- Error message display
- Success confirmation

Integrates with POST /api/auth/register
Test coverage: 94%

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# Push to remote
git push origin feature/ui-registration-form
```

Create PR on GitHub:
- Base branch: `main`
- Title: `feat(ui): add user registration form`
- Description: Follow PR template
- Wait for CI to pass
- Merge using **Squash and merge**
- Delete branch after merge

### Step 4: Integration and Completion

#### 4-1. Integration Testing (if both API and UI implemented)

After both PRs are merged:

```bash
# Pull latest changes
git checkout main
git pull origin main

# Start all services
docker compose up -d

# Manual testing
# 1. Open http://localhost:3000
# 2. Test the registration flow end-to-end
# 3. Verify database entries
# 4. Check API logs for errors
```

#### 4-2. Documentation Updates

If the feature requires documentation updates:

```bash
git checkout -b docs/update-registration-docs

# Update relevant documentation
# - ARCHITECTURE.md (if architecture changed)
# - README.md (if user-facing feature)
# - API documentation (if new endpoints)

git commit -m "docs: update registration feature documentation"
git push origin docs/update-registration-docs
```

Create PR following the same workflow.

## Concrete Example: User Registration API

Let's walk through a complete example: **"Create a user registration API"**

### Step 0: Task Understanding

**Received task**: "アカウント作成APIを作成してください" (Create a user registration API)

**Clarification questions**:

```
1. Requirements Clarification:
   - What user information is required for registration?
     (email, password, username, display_name, etc.)
   - Is admin approval workflow required?
     (ARCHITECTURE.md mentions user approval workflow)
   - What are the password validation rules?
     (minimum length, character requirements, etc.)

2. Current State Review:
   - ARCHITECTURE.md check: ✅ PBAC system specification found
   - Existing code: ❌ No authentication code exists
   - Database: ❌ No users table exists (alembic/versions/ is empty)

3. Proposed Scope:
   a. Database schema (users, roles, permissions tables)
   b. POST /api/auth/register endpoint
   c. Password hashing and validation
   d. Admin approval workflow (pending → approved)
   e. Unit tests (95% coverage)

   OR should I implement only basic registration first (without approval workflow)?
```

**Stakeholder response** (example):
```
Start with basic registration (no approval workflow for now).
Required fields: email, password, username
Password rules: minimum 8 characters, must include letters and numbers
```

### Step 1: Task Analysis

- **Implementation type**: API only (UI will be separate task)
- **Database changes**: New tables required (users, roles, permissions)
- **Dependencies**: None (this is the foundation for authentication)

### Step 2: Implementation

#### 2-1. Create Branch

```bash
git checkout -b feature/api-user-registration
```

#### 2-2. Create Database Migration

```bash
cd api
alembic revision --autogenerate -m "add users roles and permissions tables"
```

Edit the generated migration to add:
- `users` table (id, email, password_hash, username, created_at, etc.)
- `roles` table (id, name, description)
- `permissions` table (id, name, category, description)
- `role_permissions` table (role_id, permission_id)
- `user_permissions` table (user_id, permission_id, grant_type)

```bash
alembic upgrade head
```

#### 2-3. Implement Components

**File**: `api/src/app/schemas/auth.py`
```python
from pydantic import BaseModel, EmailStr, Field

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=3, max_length=50)

class UserRegisterResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
```

**File**: `api/src/app/models/user.py`
```python
from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

**File**: `api/src/app/services/auth.py`
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def register_user(db: AsyncSession, user_data: UserRegisterRequest) -> User:
    # Check if email exists
    # Hash password
    # Create user
    # Return user object
    pass
```

**File**: `api/src/app/routers/auth.py`
```python
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=UserRegisterResponse, status_code=201)
async def register(user_data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    # Call service function
    # Handle errors
    # Return response
    pass
```

**File**: `api/tests/test_auth.py`
```python
import pytest

@pytest.mark.asyncio
async def test_register_success():
    # Test successful registration
    pass

@pytest.mark.asyncio
async def test_register_duplicate_email():
    # Test duplicate email error
    pass

@pytest.mark.asyncio
async def test_register_weak_password():
    # Test password validation
    pass
```

#### 2-4. Run Quality Checks

```bash
ruff check . && ruff format .
mypy src/
pytest --cov --cov-fail-under=75
```

#### 2-5. Create PR

```bash
git add .
git commit -m "$(cat <<'EOF'
feat(api): add user registration endpoint

Implements POST /api/auth/register with:
- Email, password, username validation
- Password hashing with bcrypt
- Duplicate email/username prevention
- Database schema for users, roles, permissions

Test coverage: 96%
Closes #123

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
git push origin feature/api-user-registration
```

Merge after CI passes.

### Step 3: UI Implementation (Separate Task)

**New task**: "Create user registration form UI"

```bash
git checkout main
git pull origin main
git checkout -b feature/ui-registration-form
```

Implement frontend following Step 3 workflow above.

## Implementation Checklist

Use this checklist for every implementation task:

### Pre-Implementation
- [ ] Checked current Git branch (not on `main`)
- [ ] Created or switched to appropriate feature branch
- [ ] No uncommitted changes from other tasks
- [ ] Task purpose and requirements are clear
- [ ] Clarified all ambiguities with stakeholders
- [ ] Reviewed ARCHITECTURE.md for specifications
- [ ] Searched for existing similar implementations
- [ ] Checked database schema state
- [ ] Identified dependencies
- [ ] Confirmed implementation scope

### API Implementation
- [ ] Created feature branch from latest `main`
- [ ] Created database migration (if needed)
- [ ] Implemented Pydantic schemas with validation
- [ ] Implemented database models (if needed)
- [ ] Implemented service layer functions
- [ ] Implemented FastAPI endpoints
- [ ] Added comprehensive error handling
- [ ] Wrote unit tests (≥75% coverage, aim for 95%)
- [ ] Ran linter (ruff check)
- [ ] Ran formatter (ruff format)
- [ ] Ran type checker (mypy)
- [ ] All tests pass locally
- [ ] Created PR with clear description
- [ ] CI/CD passes
- [ ] PR merged and branch deleted

### UI Implementation
- [ ] API implementation is merged to `main`
- [ ] Created feature branch from latest `main`
- [ ] Implemented TypeScript types
- [ ] Implemented API client functions
- [ ] Implemented React components
- [ ] Integrated components into pages
- [ ] Added form validation and error handling
- [ ] Wrote unit tests (≥75% coverage, aim for 95%)
- [ ] Ran linter (npm run lint)
- [ ] Ran formatter (npm run format)
- [ ] Ran type checker (npm run type-check)
- [ ] Build succeeds (npm run build)
- [ ] All tests pass locally
- [ ] Created PR with clear description
- [ ] CI/CD passes
- [ ] PR merged and branch deleted

### Post-Implementation
- [ ] Integration testing completed
- [ ] Documentation updated (if needed)
- [ ] Stakeholders notified of completion

## Task Prioritization Guide

When multiple tasks are available, prioritize in this order:

### Priority 1: Database Foundation
- Database schema design
- Core table creation (users, servers, etc.)
- Migration infrastructure setup

**Rationale**: All features depend on database schema.

### Priority 2: Authentication and Authorization
- User registration and login
- JWT token management
- PBAC (Permission-Based Access Control) system

**Rationale**: Most features require authentication/authorization.

### Priority 3: Core Features
- Server management (start, stop, status)
- File management (upload, download, snapshot)
- Log viewing

**Rationale**: These are the primary value-add features.

### Priority 4: Supporting Features
- WebSocket notifications
- Admin user management
- Audit logging

**Rationale**: Enhance core features but not blocking.

### Priority 5: UI/UX Enhancements
- Dashboard polish
- Responsive design improvements
- Accessibility features

**Rationale**: Implement after core functionality is stable.

## When to Ask Questions

**ALWAYS ask questions** in these situations:

### Specification Uncertainty
- [ ] Feature is not documented in ARCHITECTURE.md
- [ ] Specification contradicts existing implementation
- [ ] Multiple valid interpretations exist

### Technical Uncertainty
- [ ] Multiple implementation approaches are possible
- [ ] Security implications are involved (passwords, auth, permissions)
- [ ] Performance/scalability concerns exist
- [ ] Existing design patterns don't fit the requirement

### Scope Uncertainty
- [ ] Task scope is ambiguous or overly broad
- [ ] Unclear what constitutes "done"
- [ ] Unclear whether to implement API, UI, or both
- [ ] Dependencies are unclear

### Examples of Good Questions

```markdown
Question: User Registration API - Approval Workflow

I'm implementing the user registration API and found that ARCHITECTURE.md
mentions an "admin approval workflow". Should I implement this now or
in a separate task?

Options:
A. Implement full workflow now (users start as 'pending', admin approves)
B. Skip approval for now (users are auto-approved)
C. Add database support but no API endpoint yet

Which approach should I take?
```

```markdown
Question: Password Validation Rules

The task says "add password validation" but doesn't specify rules.
What are the requirements?

- Minimum length?
- Character requirements (uppercase, numbers, symbols)?
- Maximum length?
- Forbidden patterns (common passwords, username in password)?

Should I follow OWASP recommendations or are there specific requirements?
```

## Best Practices

### Do's ✅

- **Read ARCHITECTURE.md first** - It's the source of truth
- **Ask questions early** - Don't wait until you're stuck
- **Follow existing patterns** - Check how similar features are implemented
- **Write tests first** - TDD helps clarify requirements
- **Keep PRs small** - Easier to review and merge
- **Update documentation** - Keep docs in sync with code
- **Run CI checks locally** - Don't rely on GitHub Actions to find issues

### Don'ts ❌

- **Don't guess requirements** - Always clarify with stakeholders
- **Don't implement API and UI together** - Separate branches, separate PRs
- **Don't skip tests** - 75% minimum coverage is enforced
- **Don't skip code quality checks** - Linting, formatting, type checking are mandatory
- **Don't create migrations manually** - Use `alembic revision --autogenerate`
- **Don't commit without running tests locally** - CI failures waste time
- **Don't merge PRs with failing CI** - Fix issues first

## Common Pitfalls

### Pitfall 0: Working directly on main branch

**Problem**: Making commits directly to `main` branch instead of using feature branches.

**Solution**:
- Always check your current branch with `git branch` before starting work
- Never commit directly to `main` (branch protection should prevent this)
- Create a feature branch: `git checkout -b feature/api-<name>`
- If accidentally on `main`, switch immediately and create a proper branch

### Pitfall 1: Implementing without understanding

**Problem**: Starting to code immediately without reviewing specifications or existing code.

**Solution**: Always complete Step 0 (Task Understanding) before writing any code.

### Pitfall 2: Mixing API and UI implementation

**Problem**: Implementing both backend and frontend in the same branch/PR.

**Solution**: API first (merge to `main`), then UI in a separate branch/PR.

### Pitfall 3: Skipping database schema review

**Problem**: Creating migrations without checking if tables/columns already exist.

**Solution**: Always run `alembic history` and check existing schema first.

### Pitfall 4: Assuming requirements

**Problem**: Making assumptions about validation rules, error handling, or business logic.

**Solution**: Ask clarifying questions. Reference ARCHITECTURE.md specifications.

### Pitfall 5: Insufficient test coverage

**Problem**: Writing minimal tests and failing the 75% coverage requirement.

**Solution**: Write tests for all code paths. Aim for 95% coverage.

### Pitfall 6: Ignoring existing patterns

**Problem**: Implementing features differently from existing code (naming, structure, error handling).

**Solution**: Search for similar features with Grep/Glob. Follow established patterns.

### Pitfall 7: Skipping local CI checks

**Problem**: Pushing code without running linter, formatter, type checker, or tests locally.

**Solution**: Run all checks locally before pushing. Use pre-commit hooks.

## Summary

**Implementation workflow in one sentence**:
> Understand the task and current state (Step 0), analyze the approach (Step 1), implement API first (Step 2), implement UI separately (Step 3), and verify integration (Step 4).

**Key principles**:
1. **Never guess** - Always ask when uncertain
2. **API and UI are separate** - Different branches, different PRs
3. **ARCHITECTURE.md is the source of truth** - Follow specifications
4. **Tests are mandatory** - Minimum 75%, aim for 95%
5. **Code quality matters** - Linting, formatting, type checking are required

**Remember**: It's better to ask questions and clarify requirements than to implement the wrong feature. Taking time to understand the task saves time in the long run.

---

**Last Updated**: 2025-12-30

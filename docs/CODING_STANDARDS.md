# Coding Standards

## Purpose

This document defines coding conventions, naming rules, and code style guidelines for the Minecraft Server Dashboard project. These standards ensure code consistency, maintainability, and adherence to the project's core values.

## Core Principles

All code must align with the project philosophy:

1. **Testability-first**: Write testable code with clear dependencies
2. **Code consistency**: Strict enforcement via automated tools
3. **Type safety**: Leverage static typing (Python type hints, TypeScript)
4. **Readability**: Code is read more often than written

---

## Python (Backend)

### Code Style

**Formatter**: [Black](https://black.readthedocs.io/) (line length: 100)
**Linter**: [Ruff](https://docs.astral.sh/ruff/)
**Import Sorting**: [isort](https://pycqa.github.io/isort/) (Black-compatible profile)

**Configuration** (`pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py313']

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.isort]
profile = "black"
line_length = 100
```

**Automated enforcement**: Pre-commit hooks and CI checks

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| **Variables** | `snake_case` | `server_id`, `backup_count` |
| **Functions** | `snake_case` | `create_server()`, `get_user_by_id()` |
| **Classes** | `PascalCase` | `ServerManager`, `BackupScheduler` |
| **Constants** | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_PORT` |
| **Private members** | `_leading_underscore` | `_internal_method()`, `_cache` |
| **Type variables** | `PascalCase` with `T` prefix | `TModel`, `TResponse` |
| **Files** | `snake_case.py` | `server_manager.py`, `backup_service.py` |
| **Packages** | `lowercase` (no underscores) | `services/`, `models/` |

### Type Hints

**Required**: All function signatures and public APIs must have type hints.

```python
# Good
async def create_server(
    config: ServerConfig,
    user_id: int,
    strategy: ServerLaunchStrategy,
) -> Server:
    ...

# Bad (missing type hints)
async def create_server(config, user_id, strategy):
    ...
```

**Complex types**: Use `typing` module for clarity.

```python
from typing import Optional, Dict, List, Any
from collections.abc import Sequence

def process_players(
    players: Sequence[str],
    metadata: Optional[Dict[str, Any]] = None,
) -> List[Player]:
    ...
```

**Type checking**: Use `mypy` in strict mode.

```toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
```

### Import Organization

**Order** (enforced by `isort`):
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
# Standard library
import asyncio
from pathlib import Path
from typing import Optional

# Third-party
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

# Local
from app.core.config import settings
from app.models.server import Server
from app.services.server_manager import ServerManager
```

**Grouping**: Separate groups with blank lines.

**Absolute imports**: Prefer absolute imports over relative.

```python
# Good
from app.services.server_manager import ServerManager

# Avoid
from ..services.server_manager import ServerManager
```

### Docstrings

**Style**: Google-style docstrings
**Required**: All public modules, classes, and functions

```python
async def create_backup(
    server_id: str,
    snapshot_type: SnapshotType,
    created_by: int,
) -> Snapshot:
    """Create a backup snapshot for a Minecraft server.

    Args:
        server_id: Unique identifier of the server.
        snapshot_type: Type of snapshot (manual, scheduled, auto_save).
        created_by: User ID who initiated the backup.

    Returns:
        Created snapshot object with metadata.

    Raises:
        ServerNotFoundError: If server does not exist.
        InsufficientStorageError: If storage quota exceeded.
    """
    ...
```

**Module docstrings**:

```python
"""Server launch strategy implementations.

This module provides concrete implementations of the ServerLaunchStrategy
interface for different server launch methods (Host, DinD, DooD).
"""
```

### Code Organization

**File structure**:
```
backend/
├── api/              # API endpoints (FastAPI routes)
├── services/         # Business logic
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas (request/response)
├── core/             # Core utilities (config, security, db)
└── tests/            # Test files (mirror structure)
```

**One class per file** (unless closely related).

**Function length**: Max 50 lines (guideline, not strict).

**Class method order**:
1. `__init__`
2. Public methods
3. Private methods
4. Properties
5. Magic methods (except `__init__`)

### Error Handling

**Custom exceptions**: Inherit from base exception classes.

```python
# core/exceptions.py
class ApplicationError(Exception):
    """Base exception for all application errors."""

class ServerNotFoundError(ApplicationError):
    """Raised when server is not found."""
```

**Avoid bare `except`**: Always specify exception types.

```python
# Good
try:
    result = await perform_operation()
except (ConnectionError, TimeoutError) as e:
    logger.error(f"Operation failed: {e}")
    raise

# Bad
try:
    result = await perform_operation()
except:  # Too broad
    pass
```

---

## TypeScript/React (Frontend)

### Code Style

**Formatter**: [Prettier](https://prettier.io/)
**Linter**: [ESLint](https://eslint.org/) with TypeScript and React plugins

**Configuration** (`.prettierrc.json`):
```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "always"
}
```

**ESLint** (`.eslintrc.json`):
```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "error"
  }
}
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| **Variables** | `camelCase` | `serverId`, `backupCount` |
| **Functions** | `camelCase` | `createServer()`, `getUserById()` |
| **Components** | `PascalCase` | `ServerCard`, `BackupScheduler` |
| **Interfaces** | `PascalCase` (no `I` prefix) | `Server`, `BackupConfig` |
| **Types** | `PascalCase` | `ServerStatus`, `UserRole` |
| **Enums** | `PascalCase` | `ServerType`, `SnapshotType` |
| **Constants** | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `API_BASE_URL` |
| **Files (components)** | `PascalCase.tsx` | `ServerCard.tsx`, `BackupList.tsx` |
| **Files (utilities)** | `kebab-case.ts` | `api-client.ts`, `token-manager.ts` |
| **CSS Modules** | `PascalCase.module.css` | `ServerCard.module.css` |

### Type Definitions

**Explicit return types**: Required for all functions.

```typescript
// Good
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Bad (implicit return type)
function calculateTotal(items: Item[]) {
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

**Interface vs Type**:
- Use `interface` for object shapes (can be extended)
- Use `type` for unions, intersections, primitives

```typescript
// Interface (preferred for objects)
interface Server {
  id: string;
  name: string;
  status: ServerStatus;
}

// Type (for unions/intersections)
type ServerStatus = 'running' | 'stopped' | 'starting';
type UpdateableServer = Partial<Server> & { id: string };
```

**Avoid `any`**: Use `unknown` or specific types.

```typescript
// Good
function parseResponse(data: unknown): Server {
  if (isServer(data)) {
    return data;
  }
  throw new Error('Invalid server data');
}

// Bad
function parseResponse(data: any): Server {
  return data;  // No type safety
}
```

### Import Organization

**Order**:
1. React/Next.js imports
2. Third-party libraries
3. Internal modules (absolute paths via `@/`)
4. Relative imports
5. CSS modules (last)

```typescript
// React/Next.js
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// Third-party
import { Result } from 'neverthrow';

// Internal (absolute paths)
import { useAuth } from '@/contexts/auth';
import { ServerService } from '@/services/server';
import type { Server } from '@/types/server';

// Relative
import { ServerCard } from './ServerCard';

// CSS
import styles from './ServerList.module.css';
```

### React Component Guidelines

**Function components**: Use function declarations (not arrow functions).

```typescript
// Good
export function ServerCard({ server }: ServerCardProps) {
  return <div>{server.name}</div>;
}

// Avoid
export const ServerCard = ({ server }: ServerCardProps) => {
  return <div>{server.name}</div>;
};
```

**Props interface**: Define explicitly, suffix with `Props`.

```typescript
interface ServerCardProps {
  server: Server;
  onDelete?: (id: string) => void;
  className?: string;
}

export function ServerCard({ server, onDelete, className }: ServerCardProps) {
  // ...
}
```

**Destructure props**: In function signature (as shown above).

**Hooks order**:
1. Context hooks (`useAuth`, `useLanguage`)
2. State hooks (`useState`)
3. Effect hooks (`useEffect`)
4. Custom hooks
5. Event handlers
6. Render logic

**File structure** (component file):
```typescript
// Imports
import { useState } from 'react';
import styles from './Component.module.css';

// Types
interface ComponentProps {
  // ...
}

// Component
export function Component({ prop }: ComponentProps) {
  // Context hooks
  const { user } = useAuth();

  // State hooks
  const [data, setData] = useState<Data | null>(null);

  // Effects
  useEffect(() => {
    // ...
  }, []);

  // Event handlers
  const handleClick = () => {
    // ...
  };

  // Render
  return <div>...</div>;
}
```

### CSS Modules

**File naming**: `ComponentName.module.css`

**Class naming**: `camelCase` in CSS, accessed as object properties in TypeScript.

```css
/* ServerCard.module.css */
.container {
  padding: 1rem;
}

.titlePrimary {
  font-size: 1.5rem;
}
```

```typescript
import styles from './ServerCard.module.css';

export function ServerCard() {
  return (
    <div className={styles.container}>
      <h2 className={styles.titlePrimary}>Server Name</h2>
    </div>
  );
}
```

**Avoid global styles**: Use CSS Modules for component-scoped styles.

### Comments and Documentation

**JSDoc**: Use for complex functions and utilities.

```typescript
/**
 * Fetches server details from the API.
 *
 * @param id - Server unique identifier
 * @returns Promise resolving to Server object or error
 * @throws {ApiError} If server not found or network error
 */
async function fetchServer(id: string): Promise<Result<Server, ApiError>> {
  // ...
}
```

**Inline comments**: Explain "why", not "what".

```typescript
// Good (explains rationale)
// Debounce search to avoid excessive API calls
const debouncedSearch = debounce(handleSearch, 300);

// Bad (states the obvious)
// Set loading to true
setLoading(true);
```

---

## SQL and Database

### Schema Naming

**Tables**: `snake_case`, plural form

```sql
CREATE TABLE servers (...);
CREATE TABLE backup_schedules (...);
```

**Columns**: `snake_case`

```sql
CREATE TABLE servers (
  id UUID PRIMARY KEY,
  server_name VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE
);
```

**Foreign keys**: `<table>_<column>` or descriptive name

```sql
server_id UUID REFERENCES servers(id),
owner_id INTEGER REFERENCES users(id)
```

**Indexes**: `idx_<table>_<columns>`

```sql
CREATE INDEX idx_servers_owner_id ON servers(owner_id);
CREATE INDEX idx_backups_server_created ON backups(server_id, created_at);
```

### Migrations (Alembic)

**File naming**: Auto-generated by Alembic
**Message format**: Descriptive, imperative mood

```bash
# Good
alembic revision -m "add server subdomain column"
alembic revision -m "create backup schedules table"

# Bad
alembic revision -m "changes"
alembic revision -m "update"
```

**Migration structure**:
- One logical change per migration
- Include both `upgrade()` and `downgrade()`
- Test rollback capability

---

## Testing

### File Naming and Location

**Backend**:
```
backend/
├── app/
│   └── services/
│       └── server_manager.py
└── tests/
    └── services/
        └── test_server_manager.py  # Mirror structure, prefix with "test_"
```

**Frontend**:
```
frontend/
├── components/
│   └── ServerCard.tsx
└── __tests__/
    └── components/
        └── ServerCard.test.tsx  # Mirror structure, suffix with ".test.tsx"
```

### Test Naming

**Test functions**: Descriptive, start with `test_` (Python) or `it` (TypeScript).

```python
# Python (pytest)
def test_create_server_with_valid_config():
    ...

def test_create_server_raises_error_when_user_not_approved():
    ...
```

```typescript
// TypeScript (Vitest)
describe('ServerCard', () => {
  it('renders server name correctly', () => {
    // ...
  });

  it('calls onDelete when delete button is clicked', () => {
    // ...
  });
});
```

### Test Structure

**AAA Pattern**: Arrange, Act, Assert

```python
def test_backup_scheduler_creates_snapshot():
    # Arrange
    server = create_test_server()
    scheduler = BackupScheduler()

    # Act
    snapshot = await scheduler.create_backup(server.id)

    # Assert
    assert snapshot is not None
    assert snapshot.server_id == server.id
    assert snapshot.snapshot_type == SnapshotType.SCHEDULED
```

---

## Git Commit Messages

See [WORKFLOW.md](./WORKFLOW.md) for detailed commit message conventions.

**Quick reference**:
- Format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Imperative mood: "add feature" not "added feature"
- Max 72 characters for subject line

---

## Editor Configuration

**EditorConfig** (`.editorconfig`):
```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4

[*.{ts,tsx,js,jsx,json,css}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

---

## Enforcement

### Pre-commit Hooks

**Backend** (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.15
    hooks:
      - id: ruff
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
```

**Frontend**: Configured in `package.json`:
```json
{
  "scripts": {
    "lint": "eslint . --ext .ts,.tsx",
    "format": "prettier --write .",
    "type-check": "tsc --noEmit"
  },
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged"
    }
  },
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"]
  }
}
```

### CI Checks

Required checks before merge (see [WORKFLOW.md](./WORKFLOW.md)):
- ✅ Linter (Ruff, ESLint)
- ✅ Type checking (mypy, TypeScript)
- ✅ Unit tests
- ✅ Code formatting (Black, Prettier)
- ✅ Build success

---

## Additional Resources

- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

**Last Updated**: 2025-12-26

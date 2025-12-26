# Development Workflow

## Purpose

This document defines the development workflow, Git practices, and collaboration processes for the Minecraft Server Dashboard project.

## Branching Strategy

We use a **hybrid approach** between Git Flow and GitHub Flow, optimized for continuous development with stable releases.

### Branch Types

#### `main` - Production Branch
- **Purpose**: Always deployable, represents the latest release
- **Protection**: Branch protection enabled
- **Direct commits**: ❌ Not allowed
- **Merges from**: `develop` only (via Pull Request)
- **Tagged**: Every merge creates a GitHub Release

#### `develop` - Development Branch
- **Purpose**: Integration branch for ongoing development
- **Protection**: No branch protection (allows flexibility)
- **Direct commits**: ❌ Not recommended
- **Merges from**: `feature/*`, `fix/*`, `refactor/*`, etc.
- **Base for**: All feature branches

#### `feature/*` - Feature Branches
- **Purpose**: New features or enhancements
- **Base**: `develop`
- **Naming**: `feature/brief-description` (e.g., `feature/user-authentication`)
- **Lifespan**: Short-lived (delete after merge)
- **Example**: `feature/server-status-dashboard`

#### `fix/*` - Bug Fix Branches
- **Purpose**: Bug fixes (including hotfixes)
- **Base**: `develop`
- **Naming**: `fix/brief-description` (e.g., `fix/login-error`)
- **Lifespan**: Short-lived (delete after merge)
- **Note**: Even urgent hotfixes branch from `develop` and go through a quick release

#### `refactor/*` - Refactoring Branches
- **Purpose**: Code refactoring without feature changes
- **Base**: `develop`
- **Naming**: `refactor/brief-description`
- **Lifespan**: Short-lived (delete after merge)

#### `docs/*` - Documentation Branches
- **Purpose**: Documentation updates
- **Base**: `develop`
- **Naming**: `docs/brief-description`
- **Lifespan**: Short-lived (delete after merge)

#### `test/*` - Test Improvement Branches
- **Purpose**: Adding or improving tests
- **Base**: `develop`
- **Naming**: `test/brief-description`
- **Lifespan**: Short-lived (delete after merge)

### Branch Naming Rules

**Format**: `<type>/<brief-description>`

**Rules**:
- Use lowercase
- Use hyphens to separate words
- Keep it concise but descriptive
- No issue numbers in branch names (link in PR instead)

**Examples**:
- ✅ `feature/websocket-notifications`
- ✅ `fix/memory-leak-logs`
- ✅ `refactor/api-error-handling`
- ❌ `feature/issue-123` (don't include issue numbers)
- ❌ `Feature/WebSocket-Notifications` (use lowercase)
- ❌ `new_feature` (use type prefix)

## Commit Message Convention

We use **Conventional Commits** specification.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring (no feature change or bug fix)
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Build system or external dependency changes
- **ci**: CI/CD configuration changes
- **chore**: Other changes that don't modify src or test files

### Scope (optional)

The scope specifies what part of the codebase is affected:
- `api`: Backend API
- `ui`: Frontend UI
- `db`: Database
- `auth`: Authentication
- `server`: Server management logic
- etc.

### Examples

```
feat(api): add server status endpoint

Implements real-time server status monitoring via WebSocket.
Closes #123
```

```
fix(ui): resolve memory leak in dashboard component

The dashboard was not properly cleaning up event listeners.
```

```
docs: update API documentation for v2 endpoints
```

```
refactor(auth): simplify JWT token validation logic
```

### Commit Message Rules

- Use imperative mood ("add" not "added" or "adds")
- First line should be ≤ 72 characters
- Capitalize the first letter of description
- No period at the end of the description
- Use body to explain "what" and "why", not "how"
- Reference issues and PRs in the footer

## Pull Request Workflow

### Creating a Pull Request

1. **Create a branch** from `develop`
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/my-feature
   ```

2. **Make changes** with proper commits
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

3. **Keep branch updated** with develop
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

4. **Push to remote**
   ```bash
   git push origin feature/my-feature
   ```

5. **Create Pull Request** on GitHub
   - Base: `develop`
   - Title: Clear, descriptive summary
   - Description: Context, changes, testing notes
   - Link related issues

### Pull Request Title

PR titles should follow Conventional Commits format:
```
<type>(<scope>): <description>
```

Example: `feat(api): add server status endpoint`

### Pull Request Description Template

```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Testing
How to test these changes

## Related Issues
Closes #123
```

### Draft Pull Requests

Use **Draft PRs** for work-in-progress:
- Early feedback on approach
- CI/CD checks validation
- Team awareness of ongoing work

Convert to "Ready for Review" when complete.

## Code Review Process

### Requirements for Merge

All Pull Requests must meet these requirements:

#### Automated Checks (Required)
- ✅ **Unit tests pass** (95%+ coverage maintained)
- ✅ **Linter passes** (zero warnings)
- ✅ **Type checking passes** (strict mode)
- ✅ **Build succeeds** (no errors)

#### Manual Review (Optional but Recommended)
- Code review by team member(s)
- Approval from at least 1 reviewer for major changes

### Review Focus Areas

Reviewers should focus on:
1. **Alignment with PHILOSOPHY.md** principles
2. **Testability**: Can this code be easily tested?
3. **Maintainability**: Is the code clear and well-documented?
4. **Architecture**: Does it fit the overall design?
5. **Security**: Any security concerns?

### Review Response Time

- Initial review within 24-48 hours (best effort)
- For urgent fixes, notify the team

## Merge Strategy

### Method: Squash and Merge

All PRs are merged using **Squash and Merge**:
- Multiple commits are combined into one
- Clean, linear history in `develop` and `main`
- Commit message follows Conventional Commits

### Squash Commit Message

The squashed commit message should:
- Use the PR title as the commit message
- Include PR number in the footer
- Preserve important details from PR description

Example:
```
feat(api): add server status endpoint (#123)

Implements real-time server status monitoring via WebSocket.
```

### After Merge

- **Delete the feature branch** (automatic on GitHub)
- **Close related issues** (automatic if using "Closes #123")

## Release Process

### From `develop` to `main`

1. **Prepare for release**
   - Ensure all intended features are merged to `develop`
   - Verify all CI checks pass on `develop`
   - Update version number if needed

2. **Create Release PR**
   ```
   From: develop
   To: main
   Title: "release: version X.Y.Z"
   ```

3. **Review and merge**
   - All automated checks must pass
   - Review changelog/release notes
   - Squash and merge to `main`

4. **Create GitHub Release**
   - Tag: `vX.Y.Z`
   - Title: `Version X.Y.Z`
   - Description: Release notes (features, fixes, breaking changes)
   - Attach binaries if applicable

5. **Post-release**
   - Verify deployment
   - Monitor for issues

### Hotfix Process

For urgent production fixes:

1. **Create fix branch** from `develop` (not `main`)
   ```bash
   git checkout develop
   git checkout -b fix/critical-bug
   ```

2. **Implement and test** the fix
   - Keep changes minimal and focused
   - Ensure tests cover the fix

3. **Create PR to `develop`**
   - Mark as urgent/hotfix
   - Fast-track review if needed

4. **After merge to `develop`**
   - Immediately create release PR to `main`
   - Create emergency GitHub Release

## Branch Protection Rules

### `main` Branch

- ✅ Require pull request before merging
- ✅ Require status checks to pass:
  - Unit tests
  - Linter
  - Type checking
  - Build
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings
- ❌ Require approvals: Optional (rely on automated checks)
- ❌ Require linear history: No (we use squash merge)

### `develop` Branch

- No branch protection (allows flexibility)
- All merges still require passing CI checks (enforced via PR process)

## Continuous Integration (CI/CD)

### Automated Checks

Run on every push to any branch:

1. **Unit Tests**
   - Execute all test suites
   - Verify minimum 95% coverage
   - Report coverage changes

2. **Linter**
   - ESLint (JavaScript/TypeScript)
   - Pylint/Flake8 (Python)
   - Zero warnings policy

3. **Type Checking**
   - TypeScript: strict mode
   - Python: mypy with strict settings

4. **Build**
   - Backend build
   - Frontend build
   - Docker image build (if applicable)

### CI Configuration

- **Platform**: GitHub Actions (recommended)
- **Run on**: All branches, all PRs
- **Fail fast**: Stop on first failure
- **Cache**: Dependencies for faster runs

### Example Workflow

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: npm test -- --coverage
      - name: Check coverage
        run: npm run coverage:check

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run linter
        run: npm run lint

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Type check
        run: npm run typecheck

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build
        run: npm run build
```

## Dependency Management

### Automated Dependency Updates

Use **Dependabot** (or similar) for automatic dependency updates:

- **Schedule**: Weekly
- **Auto-merge**: Patch and minor updates (after CI passes)
- **Manual review**: Major version updates
- **Security updates**: Immediate, high priority

### Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

## Best Practices

### Do's ✅

- Keep branches short-lived (< 1 week if possible)
- Commit frequently with clear messages
- Rebase on `develop` regularly to avoid conflicts
- Write tests for all new code
- Update documentation with code changes
- Delete branches after merge
- Use draft PRs for early feedback

### Don'ts ❌

- Don't commit directly to `main` or `develop`
- Don't force push to shared branches
- Don't merge without passing CI checks
- Don't merge with unresolved conversations
- Don't leave stale branches open
- Don't commit secrets or sensitive data
- Don't skip writing tests

## Troubleshooting

### Merge Conflicts

```bash
# Update your branch with latest develop
git fetch origin
git rebase origin/develop

# Resolve conflicts
# Edit conflicted files
git add <resolved-files>
git rebase --continue

# Force push (safe for feature branches)
git push --force-with-lease
```

### Failed CI Checks

1. **Pull latest changes** and run checks locally
2. **Fix issues** in new commits
3. **Push** to update the PR
4. CI will automatically re-run

### Accidental Commit to Wrong Branch

```bash
# If not pushed yet
git reset HEAD~1  # Undo last commit, keep changes
git stash         # Save changes
git checkout correct-branch
git stash pop     # Apply changes

# If already pushed
# Create new PR from correct branch
```

---

**Last Updated**: 2025-12-25

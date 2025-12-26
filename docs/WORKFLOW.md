# Development Workflow

## Purpose

This document defines the development workflow, Git practices, and collaboration processes for the Minecraft Server Dashboard project.

## Branching Strategy

We use **Release Flow**, a branching strategy developed by Microsoft that optimizes continuous development with stable releases.

**Philosophy**: `main` is the active development branch. Stable releases are maintained in long-lived `release/x.y.z` branches.

**Reference**: [Microsoft Release Flow](https://devblogs.microsoft.com/devops/release-flow-how-we-do-branching-on-the-vsts-team/)

### Branch Types

#### `main` - Active Development Branch
- **Purpose**: Continuous integration and development (基本機能が動作するレベル)
- **Protection**: Branch protection enabled
- **Direct commits**: ❌ Not allowed
- **Merges from**: `feature/*`, `fix/*`, `refactor/*`, `docs/*`, `test/*` (via Pull Request)
- **Status**: Should be functional but not necessarily production-ready
- **CI**: All checks must pass before merge

#### `release/x.y.z` - Stable Release Branches
- **Purpose**: Production-ready stable versions with full functionality guarantee
- **Protection**: Branch protection enabled, tags immutable
- **Created from**: `main` when ready for release
- **Lifespan**: Long-lived (maintained for hotfixes)
- **Naming**: `release/1.0.0`, `release/1.1.0`, `release/2.0.0`
- **Tagged**: Each release branch is tagged (`v1.0.0`, `v1.0.1`, etc.)
- **Deletion**: ❌ Never delete (preserved for history)

**Examples**:
- `release/1.0.0` → tag `v1.0.0` (initial stable release)
- `release/1.0.1` → tag `v1.0.1` (hotfix on 1.0.0)
- `release/1.1.0` → tag `v1.1.0` (new features)

#### `feature/*` - Feature Branches
- **Purpose**: New features or enhancements
- **Base**: `main`
- **Naming**: `feature/brief-description` (e.g., `feature/user-authentication`)
- **Lifespan**: Short-lived (delete after merge)
- **Merge to**: `main` (via Squash and merge)
- **Example**: `feature/server-status-dashboard`

#### `fix/*` - Bug Fix Branches
- **Purpose**: Bug fixes for main branch
- **Base**: `main` (for ongoing development bugs)
- **Naming**: `fix/brief-description` (e.g., `fix/login-error`)
- **Lifespan**: Short-lived (delete after merge)
- **Merge to**: `main`
- **Note**: For hotfixes on releases, see Hotfix Workflow below

#### `refactor/*` - Refactoring Branches
- **Purpose**: Code refactoring without feature changes
- **Base**: `main`
- **Naming**: `refactor/brief-description`
- **Lifespan**: Short-lived (delete after merge)
- **Merge to**: `main`

#### `docs/*` - Documentation Branches
- **Purpose**: Documentation updates
- **Base**: `main`
- **Naming**: `docs/brief-description`
- **Lifespan**: Short-lived (delete after merge)
- **Merge to**: `main`

#### `test/*` - Test Improvement Branches
- **Purpose**: Adding or improving tests
- **Base**: `main`
- **Naming**: `test/brief-description`
- **Lifespan**: Short-lived (delete after merge)
- **Merge to**: `main`

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

## Development Workflows

### Feature Development Workflow

1. **Create a branch** from `main`
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/my-feature
   ```

2. **Make changes** with proper commits
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

3. **Keep branch updated** with main
   ```bash
   git fetch origin
   git rebase origin/main
   ```

4. **Push to remote**
   ```bash
   git push origin feature/my-feature
   ```

5. **Create Pull Request** on GitHub
   - Base: `main`
   - Title: Clear, descriptive summary (Conventional Commits format)
   - Description: Context, changes, testing notes
   - Link related issues

6. **Merge** after CI passes and review (if applicable)
   - Method: **Squash and merge**
   - Delete feature branch after merge

### Release Workflow

**When to create a release**: When `main` reaches a stable state with planned features complete.

1. **Prepare release branch** from `main`
   ```bash
   git checkout main
   git pull origin main
   git checkout -b release/1.0.0
   ```

2. **Finalize release** (if needed)
   ```bash
   # Update version numbers (package.json, pyproject.toml, etc.)
   # Update CHANGELOG.md
   git commit -m "chore: prepare v1.0.0 release"
   ```

3. **Tag the release**
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0 - Description"
   ```

4. **Push release branch and tag**
   ```bash
   git push origin release/1.0.0 --tags
   ```

5. **Create GitHub Release**
   - Tag: `v1.0.0`
   - Title: `v1.0.0 - Release Name`
   - Description: Release notes from CHANGELOG.md
   - Attach binaries if applicable

**Release Criteria**:
- ✅ All planned features implemented
- ✅ Manual testing confirms core functionality works
- ✅ All CI checks pass
- ✅ Documentation updated
- ✅ CHANGELOG.md updated

### Hotfix Workflow

**For critical bugs in production releases**:

1. **Create hotfix branch** from release branch
   ```bash
   git checkout release/1.0.0
   git pull origin release/1.0.0
   git checkout -b fix/critical-security-issue
   ```

2. **Fix the bug**
   ```bash
   git commit -m "fix: patch critical security vulnerability"
   ```

3. **Create new patch release**
   ```bash
   git checkout -b release/1.0.1
   git merge fix/critical-security-issue
   git tag -a v1.0.1 -m "Hotfix v1.0.1 - Security patch"
   git push origin release/1.0.1 --tags
   ```

4. **Backport to main**
   ```bash
   git checkout main
   git cherry-pick <commit-hash>
   git push origin main
   ```

5. **Create GitHub Release** for the patch version

### Pull Request Creation

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
- Clean, linear history in `main`
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

## Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/):

**Format**: `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)

- **MAJOR** (X.0.0): Incompatible API changes (breaking changes)
- **MINOR** (0.X.0): New features (backward-compatible)
- **PATCH** (0.0.X): Bug fixes (backward-compatible)

**Examples**:
- `1.0.0` → `1.0.1`: Bug fix (patch)
- `1.0.1` → `1.1.0`: New feature (minor)
- `1.9.0` → `2.0.0`: Breaking change (major)

**Pre-release versions**:
- `1.0.0-alpha.1`: Alpha release
- `1.0.0-beta.2`: Beta release
- `1.0.0-rc.1`: Release candidate

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
- ❌ Require approvals: Optional (rely on automated checks for solo development)
- ❌ Require linear history: No (we use squash merge)

### `release/*` Branches

- ✅ Require pull request before merging (for hotfixes)
- ✅ Do not allow branch deletion
- ✅ Require tag immutability (tags cannot be deleted or overwritten)
- ✅ Require status checks to pass (same as main)
- ❌ Direct pushes: Allowed only for release preparation commits

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

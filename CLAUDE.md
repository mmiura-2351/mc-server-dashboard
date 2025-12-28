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
2. **PHILOSOPHY.md / PHILOSOPHY.ja.md** - Core values and design principles
3. **ARCHITECTURE.md / ARCHITECTURE.ja.md** - System architecture (1357-1358 lines)
   - 15 main sections (##)
   - 16 numbered feature subsections (###)
   - Includes: Java compatibility matrix, PBAC system (38 permissions), state machine, graceful shutdown
4. **CODING_STANDARDS.md / CODING_STANDARDS.ja.md** - Coding conventions
5. **WORKFLOW.md / WORKFLOW.ja.md** - Git workflow and development process

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

- **Test Coverage**: Target ≥95% (current reality: 75-80%)
- **Type Safety**: Required for all Python functions, strict TypeScript mode
- **Code Formatting**: Black (Python), Prettier (TypeScript) - line length 100
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

1. **DO NOT create implementation-specific documentation** (e.g., detailed setup guides) until implementation begins
2. **DO NOT assume code exists** - treat all code examples as specifications
3. **DO NOT reference the external repositories** for design decisions
4. **DO NOT modify only one language version** - always update pairs
5. **DO NOT add `error` state to server state machine** - this was explicitly rejected (see ARCHITECTURE.md section 4)

## Philosophy and Design Principles

**Read PHILOSOPHY.md first** to understand:
- Why we are reimplementing (insufficient design in previous version)
- Core values: Maintainability > Extensibility > Performance > Reliability
- Testability-first approach
- Code consistency via automated tooling

**Key principle**: "Sufficient time and effort spent on initial design and planning" - this documentation phase is critical to avoid previous mistakes.

# Documentation Index

This directory contains all project documentation for the Minecraft Server Dashboard.

## Available Languages

All documents are available in both English and Japanese:
- English: `DOCUMENT_NAME.md`
- Japanese: `DOCUMENT_NAME.ja.md`

## Documents

### 1. Project Philosophy and Principles

**Purpose**: Defines the core values, design principles, and decision-making framework for the entire project.

**Files**:
- English: [PHILOSOPHY.md](./PHILOSOPHY.md)
- Japanese: [PHILOSOPHY.ja.md](./PHILOSOPHY.ja.md)

**Key Topics**:
- Why we are reimplementing
- Core values (Maintainability, Extensibility, Performance, Reliability)
- Design principles (Testability-first, Code consistency)
- Quality standards and requirements

---

### 2. Architecture Design

**Purpose**: Describes the overall system architecture, technology stack, and component structure.

**Files**:
- English: [ARCHITECTURE.md](./ARCHITECTURE.md)
- Japanese: [ARCHITECTURE.ja.md](./ARCHITECTURE.ja.md)

**Key Topics**:
- 3-tier architecture with complete API/Frontend separation
- Technology stack (NestJS, Next.js, PostgreSQL, Redis)
- Minecraft server management (process/Docker control)
- Network layer design for subdomain-based routing (future)
- Component architecture and data flow
- Deployment architecture (Docker/Kubernetes)
- Security and scalability considerations

---

### 3. Coding Standards

**Purpose**: Defines coding conventions, naming rules, and code style guidelines.

**Files**:
- English: [CODING_STANDARDS.md](./CODING_STANDARDS.md)
- Japanese: [CODING_STANDARDS.ja.md](./CODING_STANDARDS.ja.md)

**Key Topics**:
- Python code style (Black, Ruff, type hints)
- TypeScript/React conventions (Prettier, ESLint)
- Naming conventions (variables, functions, classes, files)
- Comment and documentation rules (docstrings, JSDoc)
- Import ordering and organization
- Testing conventions
- Database and SQL naming
- Automated enforcement (pre-commit hooks, CI)

---

### 4. Development Workflow

**Purpose**: Outlines the development process, Git workflow, and collaboration guidelines.

**Files**:
- English: [WORKFLOW.md](./WORKFLOW.md)
- Japanese: [WORKFLOW.ja.md](./WORKFLOW.ja.md)

**Key Topics**:
- Git branching strategy (Release Flow)
- Commit message conventions (Conventional Commits)
- Pull request and review process
- CI/CD requirements and automation
- Release process and GitHub Releases
- Dependency management (Dependabot)

---

### 5. Development Environment Setup

**Purpose**: Provides step-by-step instructions for setting up the development environment.

**Files**:
- English: [DEVELOPMENT.md](./DEVELOPMENT.md)
- Japanese: [DEVELOPMENT.ja.md](./DEVELOPMENT.ja.md)

**Key Topics**:
- Prerequisites (Docker, Git, Python, Node.js)
- Project structure overview
- Quick start with Docker Compose
- Local development setup (without Docker)
- Database management and migrations
- Common development tasks
- Troubleshooting
- IDE setup recommendations

---

### 6. Implementation Guide

**Purpose**: Provides step-by-step workflow for implementing features from task understanding to merge.

**Files**:
- English: [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)
- Japanese: [IMPLEMENTATION_GUIDE.ja.md](./IMPLEMENTATION_GUIDE.ja.md)

**Key Topics**:
- Task understanding and current state review
- API-first development approach (API and UI separation)
- Database migration workflow
- Implementation checklist and best practices
- When to ask questions (never assume requirements)
- Task prioritization guide
- Concrete example: User Registration API

---

## Reading Order

For new contributors or team members, we recommend reading the documentation in this order:

1. **[PHILOSOPHY.md](./PHILOSOPHY.md)** - Understand the project's core values and principles
2. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Learn the overall system structure and technology stack
3. **[CODING_STANDARDS.md](./CODING_STANDARDS.md)** - Familiarize yourself with code conventions
4. **[WORKFLOW.md](./WORKFLOW.md)** - Understand the development process
5. **[DEVELOPMENT.md](./DEVELOPMENT.md)** - Set up your development environment
6. **[IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)** - Learn the implementation workflow for tasks

---

**Last Updated**: 2025-12-30

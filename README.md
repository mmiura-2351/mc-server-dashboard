# Minecraft Server Dashboard

A comprehensive management application for Minecraft servers.

## Overview

This project is a complete redesign and reimplementation of an existing Minecraft server management system. The goal is to build a production-ready application with:

- **Multiple server launch strategies** (Host process, Docker-in-Docker, Docker-out-of-Docker)
- **Version management** with rollback capabilities
- **Multi-user support** with role-based access control
- **Automated backups** with configurable retention policies
- **Cross-platform support** (Linux, Windows)

## About This Repository

This repository contains the **reimplementation** of the Minecraft Server Dashboard, designed with improved architecture, maintainability, and extensibility.

### External Reference Repositories

The following external repositories are linked **for reference purposes only**:

- [Backend API (Python/FastAPI)](https://github.com/mmiura-2351/mc-server-dashboard-api)
- [Frontend UI (Next.js/React)](https://github.com/mmiura-2351/mc-server-dashboard-ui)

**Important**: These repositories serve solely to:
- Verify existing feature specifications
- Provide a feature list reference

They are **NOT** used for:
- Design decisions in this project
- Architectural patterns
- Implementation references

This project is designed and implemented **completely from scratch**, independent of the external repositories.

## Documentation

📚 **[Documentation Index (docs/INDEX.md)](docs/INDEX.md)**

All project documentation is organized in the [`docs/`](docs/) directory. The Documentation Index provides:

- Complete list of available documents with descriptions
- Recommended reading order for new contributors
- Language options (English and Japanese)

Start with the index to navigate the full documentation suite covering project philosophy, architecture, development workflow, and implementation analysis.

## Getting Started

### Quick Start with Docker Compose

```bash
# Clone the repository
git clone <repository-url>
cd mc-server-dashboard

# Create environment file
cp .env.example .env

# Start all services
docker compose up -d

# Access the application
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
```

### Development Setup

For detailed setup instructions, see **[DEVELOPMENT.md](docs/DEVELOPMENT.md)**.

### Current Implementation Status

**Minimal implementation available for Docker/CI verification:**
- ✅ Backend API with health check endpoints
- ✅ Frontend UI with API status monitoring
- ✅ Basic test suites for both frontend and backend
- ⏳ Feature implementation in progress (following specifications in `docs/`)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

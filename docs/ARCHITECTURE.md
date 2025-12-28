# Architecture Design

## Purpose

This document describes the overall system architecture, technology stack, component structure, and design decisions for the Minecraft Server Dashboard.

## System Overview

The Minecraft Server Dashboard is a web-based management application designed to:
- Manage multiple Minecraft servers (start/stop/command execution)
- Support multiple server launch strategies (Host process, Docker-in-Docker, Docker-out-of-Docker)
- Provide version management with rollback capabilities
- Support multiple users with role-based access control and approval workflow
- Handle automated backups with configurable retention policies
- Manage player groups (OP/Whitelist) with RCON synchronization
- Cache Minecraft version information for fast server creation
- Route Minecraft traffic via subdomain-based networking (future feature)

### Target Scale
- **Concurrent users**: 10-100 users (medium scale)
- **Managed servers**: Multiple Minecraft servers per instance
- **Deployment**: Docker/Kubernetes and local machines

### Platform Support

**Operating Systems**:
- **Linux**: Full support (primary platform)
- **Windows**: Partial support
  - ✅ **Docker-out-of-Docker (DooD)**: Supported (via Docker Desktop for Windows with named pipe)
  - ✅ **Host Process**: Supported (with Windows-specific path handling)
  - ⚠️ **Docker-in-Docker (DinD)**: Lower priority (WSL2 backend required, privileged mode limitations)

**Windows Implementation Notes**:
- **Path Handling**: Cross-platform path separators (`/` vs `\`)
- **Docker Socket**: Unix socket (`/var/run/docker.sock`) vs Named pipe (`//./pipe/docker_engine`)
- **Process Management**: Windows service instead of systemd daemon

**Priority**: DoD and Host Process strategies receive Windows support first; DinD is deferred.

### Client Support

**Web UI Responsive Design**:
- **Desktop**: Full functionality (primary target)
- **Tablet**: Moderate support (basic operations)
- **Mobile**: Low priority (view-only features recommended)

**Design Philosophy**: Desktop-first approach
- Complex operations (file editing, advanced configuration) optimized for desktop
- Simple operations (server start/stop, status monitoring) accessible on all devices

## Architecture Style

**3-Tier Architecture with Complete Separation**

```
┌─────────────────────────────────────────────────────────────┐
│                         Clients                              │
│            (Web Browsers, Mobile Devices)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐            ┌──────────────────┐
│   Frontend SSR  │            │  Minecraft       │
│   (Next.js)     │            │  Clients         │
└────────┬────────┘            └────────┬─────────┘
         │                               │
         │ REST API + Polling            │
         │                               │
         ▼                               │
┌─────────────────────────────────────────┐
│        Backend API Server               │
│        (FastAPI + Python)               │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Network Layer (Future)          │  │
│  │  - Subdomain Routing             │  │
│  │  - Minecraft Protocol Proxy      │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Minecraft Server Manager        │◄─┘
│  │  (Strategy Pattern)              │
│  │  - Host Process Launch           │
│  │  - Docker-in-Docker Launch       │
│  │  - Docker-out-of-Docker Launch   │
│  │  - RCON Communication            │
│  │  - Log Monitoring                │
│  └──────────────────────────────────┘  │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│        Data Layer                       │
│  ┌──────────────────────────────────┐  │
│  │         PostgreSQL               │  │
│  │  (Primary DB, Version History,   │  │
│  │   User Data, Backup Schedules)   │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Technology Stack

### Backend API

**Framework**: Python 3.13+ + FastAPI 0.115+

**Rationale**:
- **Async-first**: Native asyncio support for high-performance I/O
- **Proven solution**: Existing implementation is production-ready
- **Fast development**: Pythonic simplicity with automatic API documentation
- **Type safety**: Pydantic models enforce data validation
- **Process management**: Excellent subprocess and daemon process support

**Key Libraries**:
- `fastapi`: Async web framework
- `uvicorn`: ASGI server
- `sqlalchemy`: Database ORM with async support
- `alembic`: Database migration tool
- `pydantic`: Data validation and settings management
- `python-jose`: JWT token handling
- `passlib[bcrypt]`: Password hashing
- `modern-rcon`: RCON protocol client
- `docker`: Docker API client for container management
- `psutil`: Process monitoring and system information
- `aiofiles`: Async file operations

### Frontend

**Framework**: Next.js 15+ (App Router) + React 19+ + TypeScript

**Rationale**:
- **SSR + CSR hybrid**: Server-side rendering with client-side interactivity
- **Type safety**: TypeScript for maintainability
- **Developer experience**: Excellent tooling and ecosystem
- **Production-ready**: Built-in optimizations

**Key Libraries**:
- `react`: UI library
- `typescript`: Type safety
- `neverthrow`: Result type for error handling
- Custom Context API for state management (auth, connection, language)
- CSS Modules: Component-scoped styling
- `DOMPurify`: XSS prevention

**State Management**:
- React Context API (lightweight, no Redux/Zustand needed)
- Three contexts: Auth, Connection Monitoring, Language (i18n)

### Database

**Primary Database**: PostgreSQL 16+

**Rationale**:
- **Relational data**: Users, servers, permissions, version history
- **ACID compliance**: Reliable for critical data
- **Scalability**: Handles medium scale (10-100 users) easily
- **Rich features**: JSON columns, full-text search, advanced indexing
- **Production-grade**: Better than SQLite for multi-user environments

**Schema Highlights**:
- User management with approval workflow (`is_approved` flag)
- Refresh token storage for secure authentication
- Version history for files and world backups (unified snapshot system)
- Backup schedules with retention policies
- Group management (OP/Whitelist) with RCON sync
- Minecraft version cache (Vanilla, Paper, Forge)
- Java compatibility matrix (conditional, based on launch strategy)

**Migration Tool**: Alembic
- Version-controlled schema changes
- Automatic migration generation from models
- Rollback support

### Minecraft Server Container

**Docker Image**: `itzg/minecraft-server`

**Rationale**:
- **Multi-type support**: Vanilla, Paper, Forge, Fabric, Spigot, Bukkit, and more
- **Version flexibility**: Any Minecraft version via environment variables
- **Well-maintained**: Active community support and regular updates
- **Feature-rich**: Extensive configuration options via environment variables

**Usage**:
```bash
docker run -e TYPE=PAPER -e VERSION=1.20.4 itzg/minecraft-server
```

**Supported Server Types** (via `TYPE` environment variable):
- `VANILLA`: Official Mojang server
- `PAPER`: Paper (high-performance fork)
- `FORGE`: Forge (mod support)
- `FABRIC`: Fabric (lightweight mod support)
- `SPIGOT`: Spigot
- `PURPUR`: Purpur
- Others: Mohist, Magma, etc.

### Real-Time Communication

**Approach**: Polling-based (not WebSocket)

**Rationale**:
- Simpler deployment (no WebSocket upgrade handling)
- Sufficient for current use case (status updates, log streaming)
- Existing implementation works well with 2-second polling during transitions

**Future Consideration**: WebSocket can be added later if needed

---

## Component Architecture

### Backend Components

```
backend/
├── api/                    # REST API endpoints
│   ├── auth/              # Authentication & authorization
│   ├── users/             # User management (approval workflow)
│   ├── servers/           # Minecraft server CRUD
│   ├── logs/              # Log retrieval
│   ├── backups/           # Backup management
│   ├── groups/            # OP/Whitelist groups
│   ├── versions/          # Minecraft version cache
│   └── snapshots/         # Version history (files + worlds)
├── services/              # Business logic layer
│   ├── server_manager/    # Server lifecycle management
│   ├── launch_strategy/   # Strategy pattern for server launching
│   │   ├── host_process.py      # Direct host process launch
│   │   ├── docker_in_docker.py  # DinD launch
│   │   └── docker_out_docker.py # DooD launch
│   ├── backup_scheduler/  # Scheduled backup service
│   ├── version_cache/     # Minecraft version management
│   ├── snapshot_service/  # Unified versioning system
│   └── group_sync/        # RCON group synchronization
├── models/                # Database models
│   ├── user.py           # User, RefreshToken
│   ├── server.py         # Server, ServerConfig
│   ├── snapshot.py       # Unified version history
│   ├── backup.py         # Backup, BackupSchedule
│   ├── group.py          # Group, ServerGroup
│   └── version.py        # MinecraftVersion
├── core/                  # Core utilities
│   ├── config.py         # Environment configuration
│   ├── database.py       # DB connection management
│   ├── security.py       # Path validation, sanitization
│   └── exceptions.py     # Custom exceptions
└── middleware/            # (Minimal - no performance monitoring)
    └── cors.py           # CORS handling
```

### Frontend Components

```
frontend/
├── app/                   # Next.js App Router
│   ├── (auth)/           # Auth pages (login, register)
│   ├── dashboard/        # Main dashboard
│   ├── servers/          # Server management pages
│   │   ├── [id]/        # Individual server detail
│   │   └── new/         # Create new server
│   ├── groups/           # Group management
│   ├── users/            # User management (admin)
│   └── settings/         # Settings
├── components/           # Reusable components
│   ├── ui/              # Basic UI components
│   ├── server/          # Server-related components
│   ├── groups/          # Group management UI
│   └── snapshots/       # Version history UI
├── contexts/             # React Context implementations
│   ├── auth.tsx         # Authentication + approval status
│   ├── connection.tsx   # API connection monitoring (minimal)
│   └── language.tsx     # i18n (English + Japanese)
├── services/             # API communication
│   ├── api.ts           # Base fetch wrapper with Result type
│   ├── server.ts        # Server API calls
│   ├── auth.ts          # Auth API calls
│   ├── groups.ts        # Group management API
│   └── snapshots.ts     # Version history API
├── utils/                # Utilities
│   ├── token-manager.ts # JWT token lifecycle
│   ├── input-sanitizer.ts # XSS/injection prevention
│   └── secure-storage.ts  # Safe localStorage wrapper
└── i18n/                 # Internationalization
    └── messages/         # English + Japanese translations
        ├── en.json
        └── ja.json
```

---

## Key Features & Design Decisions

### 1. Minecraft Server Launch Strategies (Strategy Pattern)

**Critical Feature**: Support multiple launch methods

```python
class ServerLaunchStrategy(ABC):
    @abstractmethod
    async def start(self, server_config: ServerConfig) -> Process:
        """Start Minecraft server"""
        pass

    @abstractmethod
    async def stop(self, server_id: str) -> None:
        """Stop Minecraft server"""
        pass

    @abstractmethod
    async def get_status(self, server_id: str) -> ServerStatus:
        """Get server status"""
        pass

class HostProcessStrategy(ServerLaunchStrategy):
    """Launch as host process (double-fork daemon)"""
    # PID file tracking, survives API restart

class DockerInDockerStrategy(ServerLaunchStrategy):
    """Launch Docker container inside API container"""
    # Requires privileged mode

class DockerOutOfDockerStrategy(ServerLaunchStrategy):
    """Launch Docker container on host via socket mount"""
    # Mount /var/run/docker.sock
```

**Selection Logic**:
- **System-wide configuration**: One launch strategy for the entire application
- Configured via environment variable: `DEFAULT_LAUNCH_STRATEGY=host|dind|dood`
- All servers use the same strategy (no per-server selection in initial implementation)
- **Strategy change**: Future feature (simple flag change in DB, applied on next server start)

**Java Compatibility**:
- Java compatibility matrix applies only to HostProcessStrategy
- Docker strategies (DinD/DooD) use Java included in `itzg/minecraft-server` image

---

### 2. Java Compatibility Matrix (HostProcessStrategy Only)

**Purpose**: Automatic Java version selection for Minecraft servers launched as host processes

**Minecraft Version → Java Version Mapping**:
```
Minecraft Version    | Required Java Version
---------------------|---------------------
~ 1.7.9             | Java 7
1.7.10 ~ 1.16.5     | Java 8
1.17 ~ 1.17.1       | Java 16
1.18 ~ 1.20.4       | Java 17
1.20.5 ~            | Java 21
```

**Java Detection Logic** (HostProcessStrategy only):
1. Check `.env` configuration first:
   ```bash
   JAVA_8_PATH=/usr/lib/jvm/java-8-openjdk-amd64/bin/java
   JAVA_16_PATH=/usr/lib/jvm/java-16-openjdk-amd64/bin/java
   JAVA_17_PATH=/usr/lib/jvm/java-17-openjdk-amd64/bin/java
   JAVA_21_PATH=/usr/lib/jvm/java-21-openjdk-amd64/bin/java
   ```
2. If not in `.env`, check standard paths:
   ```bash
   /usr/lib/jvm/java-{7,8,16,17,21}-openjdk-amd64/bin/java
   ```
3. Detection runs at API startup for all Java versions
4. Java detection API endpoint provided for verification

**Error Handling**:
- If required Java version not found → return error when server creation requested
- No fallback to different Java version (compatibility issues)

**Note**: Paper/Forge/Fabric have the same Java requirements as Vanilla

---

### 3. Unified Snapshot System (Version Management)

**Purpose**: Common versioning for files and world backups

**Data Model**:
```sql
Snapshot (
  id UUID PRIMARY KEY,
  resource_type ENUM('file', 'world', 'server_full'),
  resource_identifier VARCHAR,  -- file path or server ID
  version_number INTEGER,
  snapshot_type ENUM('manual', 'scheduled', 'auto_save', 'pre_update'),
  storage_path VARCHAR,  -- actual backup file location
  file_size BIGINT,
  metadata JSONB,  -- resource-specific data
  created_by INTEGER FK(User),
  created_at TIMESTAMP
)
```

**Features**:
- Rollback to any previous version
- Configurable retention (max versions per resource)
- Automatic cleanup of old snapshots
- Pre-update snapshots (before Minecraft version upgrades)

---

### 4. Server Status State Machine

**Purpose**: Define clear server lifecycle states and allowed operations

**Server States**:
```
- stopped     : Server is not running
- starting    : Server is starting up (process launch → ready)
- running     : Server is running (players can connect)
- stopping    : Server is shutting down
- unknown     : Server state cannot be determined (temporary, will re-detect)
```

**State Transitions**:
```
stopped  → starting   (start operation)
starting → running    (startup complete detected)
starting → stopped    (startup failed or stop operation with force=True)
starting → unknown    (process tracking lost)
running  → stopping   (stop operation)
running  → unknown    (process tracking lost)
stopping → stopped    (shutdown complete detected)
stopping → unknown    (process tracking lost)
unknown  → any state  (state re-detection)
```

**Allowed Operations by State**:

| State    | start | stop | restart | RCON | config change | delete |
|----------|-------|------|---------|------|---------------|--------|
| stopped  | ✅    | ❌   | ❌      | ❌   | ✅            | ✅     |
| starting | ❌    | ✅*  | ❌      | ❌   | ❌            | ❌     |
| running  | ❌    | ✅   | ✅      | ✅   | ❌            | ❌     |
| stopping | ❌    | ❌   | ❌      | ❌   | ❌            | ❌     |
| unknown  | ❌    | ❌   | ❌      | ❌   | ❌            | ❌     |

\* `starting` state stop requires `force=True` parameter

**Notes**:
- `unknown` is a temporary state that resolves automatically via state re-detection
- No `error` state (failures result in `stopped` state, errors logged separately)
- External shutdowns (Docker command, process kill, in-game `/stop`) are supported

---

### 5. Backup Scheduler with Configurable Limits

**Three-tier limit system**:

1. **Application Maximum**: Global ceiling (e.g., 168 hours interval, 30 max backups)
2. **User Maximum**: Per-user ceiling set by admin (e.g., 72 hours interval, 10 max backups)
3. **Server Configuration**: Actual settings (must be ≤ User Maximum ≤ App Maximum)

**Validation**:
```python
if server_config.backup_interval < user_limit.min_interval:
    raise ValidationError("Exceeds user limit")
if user_limit.max_backups > app_config.MAX_BACKUPS:
    raise ValidationError("Exceeds application limit")
```

**Backup Timing**:
- **Interval-based**: Backup every N hours after Minecraft server starts
- Example: Server starts at 10:00 AM, interval=6h → backups at 4:00 PM, 10:00 PM, etc.
- Timer resets when Minecraft server restarts

**API Restart Behavior**:
- If API restarts while Minecraft server is running:
  - Timer recalculates from API startup time
  - Example: API restarts at 3:00 PM (interval=6h) → next backup at 9:00 PM
- Missed backups during API downtime are NOT executed (skip to next interval)

**Backup Failure Handling**:
- Failed backups are recorded in database (`Snapshot` table with `status: failed`)
- Failure reason stored in metadata
- No retry logic (wait for next scheduled interval)

**Database-Persistent Scheduler**:
- Configuration stored in `BackupSchedule` table
- In-memory timer for execution
- Background task checks and executes backups

---

### 6. Group Management (OP/Whitelist)

**Purpose**: Centralized player permission management

**Features**:
- Create groups with player lists (JSON array)
- Group types: `op`, `whitelist`
- Attach groups to multiple servers
- RCON synchronization: `whitelist reload` after changes
- Template groups (reusable across servers)

**Data Model**:
```sql
Group (
  id, name, type, players JSONB, owner_id, is_template
)

ServerGroup (
  id, server_id FK, group_id FK, priority, attached_at
)
```

---

### 7. Minecraft Version Cache

**Purpose**: Avoid repeated external API calls

**Process**:
1. Scheduled task fetches versions from Mojang/PaperMC APIs
2. Store in `MinecraftVersion` table
3. Server creation UI loads from cache (fast)
4. Update log tracks changes

**Data Model**:
```sql
MinecraftVersion (
  id, server_type ENUM('vanilla', 'paper', 'forge'),
  version VARCHAR, download_url, release_date,
  is_stable BOOLEAN, build_number INTEGER,
  created_at, updated_at
)
```

---

### 8. User Approval Workflow

**Flow**:
1. User registers → `is_approved = False`
2. Admin reviews new users
3. Admin approves → `is_approved = True`
4. User gains full access

**Database**:
```sql
User (
  id, username, email, hashed_password,
  role ENUM('admin', 'operator', 'user'),
  is_active BOOLEAN, is_approved BOOLEAN
)
```

---

### 9. Refresh Token Revocation

**Security Feature**:
- Refresh tokens stored in database
- One active token per user
- Token revoked on logout or new login
- Prevents token reuse after compromise

**Data Model**:
```sql
RefreshToken (
  id, token VARCHAR UNIQUE, user_id FK,
  expires_at TIMESTAMP, created_at TIMESTAMP,
  is_revoked BOOLEAN DEFAULT FALSE
)
```

---

### 10. Permission-Based Access Control (PBAC)

**Purpose**: Granular permission system with role-based defaults and user-specific overrides

**Permission Calculation**: `(Role Permissions ∪ User Granted) - User Denied`

**Permission Naming Convention**: `category.action[.scope]`

**Total Permissions**: 38 permissions across 7 categories

**Permission List**:

**1. servers (Server Management) - 8 permissions**
```
servers.create          - Create new server
servers.view            - View own servers
servers.view_all        - View all servers (admin)
servers.update          - Modify server configuration
servers.delete          - Delete server
servers.start           - Start server
servers.stop            - Stop server (includes force stop with force=True)
servers.restart         - Restart server
```

**2. rcon (RCON Execution) - 1 permission**
```
rcon.execute            - Execute RCON commands on other users' servers
                          (Note: Users can always execute RCON on their own servers)
```

**3. files (File Management) - 5 permissions**
```
files.view              - View files
files.edit              - Edit files
files.upload            - Upload files
files.download          - Download files
files.delete            - Delete files
```

**4. backups (Backup Management) - 6 permissions**
```
backups.create          - Create manual backup
backups.view            - View backup list
backups.restore         - Restore from backup
backups.delete          - Delete backup
backups.schedule        - Configure automatic backup schedule
backups.download        - Download backup file
```

**5. groups (Group Management) - 6 permissions**
```
groups.create           - Create new group
groups.view             - View groups
groups.update           - Edit group configuration
groups.delete           - Delete group
groups.attach           - Attach group to server
groups.detach           - Detach group from server
```

**6. users (User Management) - 8 permissions**
```
users.view              - View user list
users.create            - Create new user
users.update            - Edit user information
users.delete            - Delete user
users.approve           - Approve new user registration
users.change_role       - Change user role
users.grant_permission  - Grant individual permission to user
users.deny_permission   - Deny individual permission to user
```

**7. system (System Settings) - 4 permissions**
```
system.view_settings    - View system configuration
system.update_settings  - Modify system configuration
system.view_health      - View health check information
system.manage_limits    - Manage 3-tier limit configuration
```

**Database Schema**:
```sql
-- Permission definitions
permissions (
  id, category, action, scope, description
)

-- Role default permissions
role_permissions (
  id, role ENUM('admin', 'operator', 'user'), permission_id FK
)

-- User-specific permission grants/denials
user_permissions (
  id, user_id FK, permission_id FK,
  is_granted BOOLEAN  -- true: grant, false: deny
)
```

**Notes**:
- `is_dangerous` flag not used (removed from design)
- Permission calculation prevents users from modifying their own permissions
- Audit logging applies to all permission changes (implemented separately)

---

### 11. Security Implementation

#### a) Path Traversal Prevention
```python
def validate_path(user_path: str, base_dir: Path) -> Path:
    """Multi-layer validation"""
    resolved = (base_dir / user_path).resolve()
    if not resolved.is_relative_to(base_dir):
        raise SecurityError("Path traversal detected")
    return resolved
```

#### b) Archive Extraction Security
```python
def validate_archive(archive_path: Path) -> None:
    """Prevent zip bombs and malicious archives"""
    # Size limits, file count limits, compression ratio check
    # Reject symlinks, device files, absolute paths
```

**Configurable Limits** (via environment variables):
```bash
ARCHIVE_MAX_SIZE_MB=500                    # Maximum archive file size
ARCHIVE_MAX_FILES=10000                    # Maximum number of files in archive
ARCHIVE_MAX_FILE_SIZE_MB=500               # Maximum individual file size
ARCHIVE_MAX_COMPRESSION_RATIO=100          # Maximum compression ratio (zip bomb detection)
```

**Rejected File Types** (to be determined based on security considerations):
- Symlinks
- Device files
- Absolute paths (`/` prefix)
- Parent directory references (`../`)
- Additional types TBD

#### c) Input Sanitization (Frontend)
```typescript
class InputSanitizer {
  static sanitizeUsername(input: string): string { ... }
  static sanitizeFilePath(input: string): string { ... }
  static sanitizeHTML(input: string): string { ... }
}
```

**Password Policy**: Relaxed (no email verification, no personal data stored)

---

### 11. Internationalization (i18n)

**Supported Languages**: English, Japanese

**Implementation**:
- Custom `LanguageContext` with lazy-loaded translations
- Translation files: `en.json`, `ja.json`
- Persisted to localStorage
- Error messages translated

---

### 12. Connection Monitoring (Minimal)

**Purpose**: Basic API health check

**Implementation**:
- Periodic check: `GET /api/v1/health`
- Simple status: Connected / Disconnected
- Visual indicator (green/red)
- No complex retry logic or degraded states

---

### 13. Web-based RCON Execution

**Purpose**: Execute Minecraft server commands from Web UI

**Security Model**:
- **Backend-mediated**: Frontend never receives RCON credentials
- **Permission**: Admin role only (application-level administrators)
- **Implementation**:
  ```
  Frontend (Admin UI) → POST /api/v1/servers/{id}/rcon
    → Backend validates user role
    → Backend retrieves RCON credentials from database
    → Backend executes command via RCON client
    → Backend returns command output
  ```

**Command Validation**:
- Input sanitization for command injection prevention
- Whitelist of allowed commands (optional, configurable)
- Audit logging of RCON executions (optional future feature)

---

### 14. Server Log Retrieval (Strategy Pattern)

**Purpose**: Display Minecraft server logs in Web UI with minimal overhead

**Implementation**: Strategy-based approach (varies by launch method)

**Interface**:
```python
class LogRetrievalStrategy(ABC):
    @abstractmethod
    async def get_recent_logs(self, server_id: str, lines: int = 100) -> list[str]:
        """Retrieve last N lines of server logs"""
        pass
```

**Strategies**:

**A) Host Process Strategy**:
- Read from log file: `servers/{server_id}/logs/latest.log`
- Cache last 1000 lines in memory (update on file mtime change)
- Frontend polls every 5 seconds
- Return last 100 lines per request

**B) Docker Strategies (DinD/DooD)**:
- Use Docker API: `container.logs(tail=100, stream=False)`
- No file I/O required
- Logs retrieved directly from container

**Performance Optimization**:
- Backend caches logs with mtime-based invalidation
- Polling interval: 5 seconds (configurable)
- Limit: Display last 100 lines, cache up to 1000 lines

---

### 15. Unified Error Response Format

**Purpose**: Consistent API error handling across all endpoints

**Standard Format**:
```json
{
  "error": {
    "code": "SERVER_NOT_FOUND",
    "message": "Server with ID 'abc-123' not found",
    "details": {},
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

**Error Code Categories**:
- `VALIDATION_ERROR`: Input validation failures
- `AUTHENTICATION_ERROR`: Auth failures (invalid credentials, expired tokens)
- `AUTHORIZATION_ERROR`: Permission denied
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Resource conflict (e.g., duplicate username)
- `INTERNAL_ERROR`: Server-side errors
- `EXTERNAL_SERVICE_ERROR`: Minecraft server or Docker errors

**HTTP Status Mapping**:
- 400: `VALIDATION_ERROR`
- 401: `AUTHENTICATION_ERROR`
- 403: `AUTHORIZATION_ERROR`
- 404: `NOT_FOUND`
- 409: `CONFLICT`
- 500: `INTERNAL_ERROR`, `EXTERNAL_SERVICE_ERROR`

**Frontend Handling**:
- Type-safe error parsing with TypeScript interfaces
- Internationalized error messages (en/ja)
- User-friendly error display

**`details` Field Structure**:
- Standardized per feature (defined during implementation)
- Example structures:
  ```json
  // VALIDATION_ERROR
  "details": {
    "field": "backup_interval",
    "constraint": "must be >= 1 hour",
    "provided": "30 minutes"
  }

  // AUTHORIZATION_ERROR
  "details": {
    "required_permission": "servers.delete",
    "user_role": "operator"
  }
  ```
- Implementation-phase decision (not pre-defined for all error codes)

---

## Data Flow Examples

### 1. Server Creation Flow

```
User → Frontend (Select version from cache)
  → Backend API (POST /api/v1/servers)
    → Validate user limits (backup settings, etc.)
    → Select launch strategy (host/DinD/DooD)
    → Download Minecraft JAR (from cached version URL)
    → Initialize server directory
    → Create initial snapshot (pre-start)
    → PostgreSQL (Save server config)
    ← Return server ID
  ← Redirect to server detail page
```

### 2. Scheduled Backup Flow

```
Background Scheduler (every N hours)
  → Check BackupSchedule table
    → Find servers due for backup
      → For each server:
        → Create snapshot (type: scheduled)
        → Compress world folder → tar.gz
        → Store in backup directory
        → PostgreSQL (Save snapshot metadata)
        → Cleanup old snapshots (respect max_backups limit)
```

### 3. Group Synchronization Flow

```
User → Frontend (Update group players)
  → Backend API (PUT /api/v1/groups/:id)
    → PostgreSQL (Update group.players JSONB)
    → Find attached servers (ServerGroup table)
    → For each attached server:
      → RCON connection
      → Send `whitelist add <player>` commands
      → Send `whitelist reload`
    ← Return success
  ← Update UI
```

---

## Graceful Shutdown Procedure

**Purpose**: Ensure clean API shutdown without data loss or corruption

### API Shutdown Behavior

**1. Minecraft Servers**:
- **Keep running**: Minecraft servers are NOT stopped during API shutdown
- Processes/containers continue running independently
- API reconnects to running servers after restart
- Rationale: Minimize player disruption

**2. In-Progress Backups**:
- **Wait for completion**: API waits for running backups to finish
- Timeout: 5 minutes (configurable via `BACKUP_SHUTDOWN_TIMEOUT_SECONDS`)
- If timeout exceeded: Force shutdown, backup marked as `failed` in database
- Partial backup files are cleaned up on next startup

**3. Database Connections**:
- **Explicit cleanup**: All PostgreSQL connections are properly closed
- Connection pool is shut down gracefully
- Ensures no orphaned connections or transaction locks

**Implementation**:
```python
@app.on_event("shutdown")
async def shutdown_event():
    # 1. Wait for in-progress backups (with timeout)
    await backup_service.wait_for_completion(timeout=300)

    # 2. Close database connections
    await database.disconnect()

    # 3. Cleanup resources
    await cleanup_temp_files()
```

**Note**: Minecraft servers remain running and must be manually stopped if needed before host shutdown

---

## Deployment Architecture

### Development Environment

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: mcsd
      POSTGRES_USER: mcsd_user
      POSTGRES_PASSWORD: <secret>
    ports: ["5432:5432"]
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://mcsd_user:<secret>@postgres:5432/mcsd
      SECRET_KEY: <min-32-chars>
    ports: ["8000:8000"]
    depends_on: [postgres]
    volumes:
      - ./servers:/app/servers  # Minecraft server data

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports: ["3000:3000"]
    depends_on: [backend]
```

### Production Environment (Docker)

- Same as development with:
  - Secrets management (Docker secrets or environment)
  - Persistent volumes for server data
  - Health checks enabled
  - Resource limits configured

### systemd Deployment (Alternative)

- Backend: `mc-server-dashboard-api.service`
- Frontend: `mc-dashboard-ui.service`
- Direct host deployment without containers
- Suitable for single-machine setups

---

## Network Layer Design (Future - Phase 2)

### Subdomain-based Server Routing

**Goal**: `aaa.example.net:25565` → Server A, `bbb.example.net:25565` → Server B

**Data Model** (Implemented from Day 1):
```sql
Server (
  ...
  subdomain VARCHAR UNIQUE,  -- "aaa", "bbb", etc.
  ...
)
```

**Future Implementation**:
1. DNS: `*.example.net` → Dashboard IP
2. TCP Proxy intercepts Minecraft connections
3. Parse handshake packet → extract hostname
4. Lookup subdomain in database
5. Route to appropriate server

**Technology Options**: Custom TCP proxy, nginx stream, HAProxy, Velocity

---

## Configuration Management

### Environment Variables

**Backend (.env)**:
```bash
# Security
SECRET_KEY=<min-32-chars>
ALLOWED_ORIGINS=http://localhost:3000,https://mcsd.example.net  # Comma-separated, no wildcards

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Authentication
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS Configuration
CORS_CREDENTIALS=true  # Allow cookies and auth headers
CORS_METHODS=GET,POST,PUT,DELETE,PATCH
CORS_HEADERS=Content-Type,Authorization

# Backup limits (Application-level maximum)
MAX_BACKUP_RETENTION=30
MAX_BACKUP_INTERVAL_HOURS=168

# Launch strategy
DEFAULT_LAUNCH_STRATEGY=host  # host|dind|dood

# Java paths (if using host strategy)
JAVA_7_PATH=/usr/lib/jvm/java-7-openjdk-amd64/bin/java
JAVA_8_PATH=/usr/lib/jvm/java-8-openjdk-amd64/bin/java
JAVA_16_PATH=/usr/lib/jvm/java-16-openjdk-amd64/bin/java
JAVA_17_PATH=/usr/lib/jvm/java-17-openjdk-amd64/bin/java
JAVA_21_PATH=/usr/lib/jvm/java-21-openjdk-amd64/bin/java

# File storage
DATA_DIR=/data  # Base directory for all file storage
MAX_UPLOAD_SIZE_MB=100  # Enforced at Nginx/reverse proxy layer

# Archive Security (configurable limits)
ARCHIVE_MAX_SIZE_MB=500                    # Maximum archive file size
ARCHIVE_MAX_FILES=10000                    # Maximum number of files in archive
ARCHIVE_MAX_FILE_SIZE_MB=500               # Maximum individual file size
ARCHIVE_MAX_COMPRESSION_RATIO=100          # Maximum compression ratio (zip bomb detection)

# Timezone
TZ=UTC  # Backend timezone (fixed to UTC)

# API Rate Limiting (relaxed, realistic limits)
RATE_LIMIT_PER_MINUTE=60  # General API calls
LOGIN_RATE_LIMIT_PER_MINUTE=10  # Login attempts per IP

# Graceful Shutdown
BACKUP_SHUTDOWN_TIMEOUT_SECONDS=300  # Wait time for backups during shutdown (5 minutes)
```

**Frontend (.env)**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEFAULT_LOCALE=en  # Default language (en or ja)
```

### File Storage Structure

**Directory Layout**:
```
/data/
├── servers/              # Minecraft server files
│   ├── {server_id}/
│   │   ├── server.jar
│   │   ├── server.properties
│   │   ├── eula.txt
│   │   ├── world/
│   │   ├── plugins/     # Paper/Spigot
│   │   ├── mods/        # Forge/Fabric
│   │   └── logs/
│   │       └── latest.log
├── snapshots/            # Version history and backups
│   ├── {snapshot_id}/
│   │   ├── metadata.json
│   │   └── data.tar.gz
└── temp/                 # Temporary files
    ├── uploads/         # File uploads before processing
    └── extractions/     # Archive extractions
```

**Permissions**:
- Application user: Read/write access to `/data/`
- Minecraft containers: Bind mount `/data/servers/{server_id}/` as volume

**Cleanup Policy**:
- Temp files older than 24 hours are automatically deleted
- Failed uploads are removed immediately

### CORS Security

**Configuration Approach**:
```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    allowed_origins: list[str] = []  # Loaded from ALLOWED_ORIGINS env var

    @property
    def cors_config(self):
        return {
            "allow_origins": self.allowed_origins,  # NO wildcards
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
```

**Environment-specific Configuration**:
- **Development**: `ALLOWED_ORIGINS=http://localhost:3000`
- **Production**: `ALLOWED_ORIGINS=https://mcsd.example.net`
- **Never use**: `*` wildcard (security risk)

### Timezone Handling

**Backend**:
- **Fixed to UTC**: All timestamps stored and processed in UTC
- Database: `TIMESTAMP WITH TIME ZONE` columns in UTC
- Python: `datetime.now(timezone.utc)` for all time operations

**Frontend**:
- **User timezone conversion**: Convert UTC to local timezone for display
- Browser API: `Intl.DateTimeFormat` or `toLocaleString()`
- User preference: Optional timezone selector in settings

**Example**:
```typescript
// Frontend: Display UTC timestamp in user's local time
const utcTimestamp = "2025-12-26T10:30:00Z";
const localTime = new Date(utcTimestamp).toLocaleString('ja-JP', {
  timeZone: 'Asia/Tokyo'
});
```

### API Rate Limiting

**Implementation**: Middleware-based (e.g., `slowapi` for FastAPI)

**Limits** (Relaxed, realistic thresholds):
- **General API**: 60 requests/minute per IP
- **Login endpoint**: 10 attempts/minute per IP
- **File upload**: 5 uploads/minute per user
- **RCON execution**: 20 commands/minute per user

**Response on Limit Exceeded**:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "details": {
      "retry_after": 30
    },
    "timestamp": "2025-12-26T10:30:00Z"
  }
}
```

**HTTP Status**: `429 Too Many Requests`

### File Upload Restrictions

**Enforcement Layer**: Nginx/reverse proxy (not application layer)

**Nginx Configuration Example**:
```nginx
server {
    location /api/v1/upload {
        client_max_body_size 100M;  # Maximum upload size

        # Only allow specific file types (optional)
        if ($request_filename ~* \.(exe|bat|cmd|sh|ps1)$) {
            return 403;
        }
    }
}
```

**Allowed Extensions** (Application-level validation):
- Server files: `.jar`, `.zip`, `.tar.gz`
- Configuration: `.properties`, `.yml`, `.yaml`, `.json`, `.toml`
- Worlds: `.zip`, `.tar.gz` (world folder archives)

**Size Limits**:
- Individual files: 100 MB (configurable via `MAX_UPLOAD_SIZE_MB`)
- World archives: 500 MB (larger limit for world backups)

---

## Logging Strategy

### Application Logs

**Philosophy**: Follow Docker best practices (stdout/stderr logging)

**Implementation**:
- **Backend**: Log to stdout/stderr (not to files)
- **Frontend**: Server-side logs to stdout, client-side logs to browser console
- **Container Runtime**: Docker captures logs automatically
- **Log Aggregation**: External tools (e.g., Docker logging drivers, ELK stack, Loki)

**Log Levels**:
- `DEBUG`: Development debugging (disabled in production)
- `INFO`: Normal operations (server start, scheduled tasks)
- `WARNING`: Recoverable errors (failed Minecraft version fetch, retry logic)
- `ERROR`: Serious errors (database connection failures, unhandled exceptions)
- `CRITICAL`: System-level failures

**Python Logging Configuration**:
```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,  # Configurable via LOG_LEVEL env var
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
```

**Log Rotation**: Handled by Docker logging driver
```yaml
# docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Structured Logging** (Optional future enhancement):
- Use `structlog` for JSON-formatted logs
- Easier parsing by log aggregation tools
- Include request IDs for tracing

### Minecraft Server Logs

**Storage**: Per-server log files (see File Storage Structure)
- Path: `/data/servers/{server_id}/logs/latest.log`
- Rotation: Handled by Minecraft server itself

**Retrieval**: See "Server Log Retrieval (Strategy Pattern)" section above

**Retention**: Logs are deleted when server is deleted or during snapshot cleanup

---

## Testing Strategy

### Test Coverage Target
- **Current Reality**: 75-80% (existing implementation)
- **Aspiration**: 95%+
- **Migration Path**: Gradual improvement over time

### Test Types
- **Unit Tests**: Services, utilities, models
- **Integration Tests**: API endpoints, database operations
- **E2E Tests**: Critical user flows (future addition)

### Tools
- **Backend**: pytest, pytest-asyncio, coverage
- **Frontend**: Vitest, React Testing Library

---

## Future Enhancements

### Phase 1 (Current Implementation Scope)
- ✅ Multiple server launch strategies (Host/DinD/DooD)
- ✅ Windows support (DooD and Host Process priority)
- ✅ Unified snapshot system (files + worlds)
- ✅ Group management (OP/Whitelist with RCON sync)
- ✅ Version caching (Vanilla/Paper/Forge)
- ✅ User approval workflow
- ✅ Internationalization (English + Japanese)
- ✅ Configurable backup limits (3-tier: app/user/server)
- ✅ Web-based RCON execution (admin only)
- ✅ Desktop-first responsive design
- ✅ Unified error response format
- ✅ API rate limiting
- ✅ Log retrieval (strategy-based)

### Phase 2 (Network Layer)
- ⏳ Subdomain-based routing (`aaa.example.net` → Server A)
- ⏳ Minecraft protocol proxy (TCP handshake parsing)
- ⏳ DNS integration (wildcard `*.example.net`)

### Phase 3 (Observability - Optional)
- ⏳ Prometheus + Grafana integration (external tools)
- ⏳ Distributed tracing (if multi-instance deployment needed)
- ⏳ Advanced audit logging (RCON command history, user actions)

---

## Design Principles Applied

1. **Strategy Pattern**: Pluggable server launch methods and log retrieval
2. **Unified Versioning**: Common snapshot system for files and backups
3. **Security-First**: Path validation, archive safety, input sanitization, rate limiting
4. **User Limits**: Three-tier configuration (app/user/server)
5. **Database Persistence**: Schedules survive restarts
6. **Simplicity**: No unnecessary complexity (polling over WebSocket, Context API over Redux)
7. **Platform Agnostic**: Cross-platform support (Linux primary, Windows partial)
8. **Desktop-First UI**: Optimize for desktop, graceful degradation for mobile
9. **Consistent Error Handling**: Unified error response format across all endpoints
10. **Docker Best Practices**: stdout/stderr logging, environment-based configuration
11. **Timezone Consistency**: UTC backend, user-local frontend conversion
12. **Backend-Mediated Security**: RCON credentials never exposed to frontend

---

**Last Updated**: 2025-12-27

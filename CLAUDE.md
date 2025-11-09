# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

eMuse is a web application for poetry sharing and management, built with:
- **Backend**: FastAPI (Python 3.12+) with PostgreSQL (located in `src/emuse/`)
- **Frontend**: React 19 + TypeScript with Vite (located in `src/ui/`)
- **Session Management**: In-memory sessions with cookie-based authentication
- **Build System**: Hatchling with src-layout structure
- **Testing**: pytest with coverage requirements (≥90%)

## Development Setup

### Initial Setup
Run the bootstrap script to set up the development environment:
```bash
./bootstrap
```

This script:
- Installs pre-commit hooks
- Starts PostgreSQL in Docker
- Creates a `.env` file with database connection details
- Initializes the database schema from `postgres/emuse.sql`

### Environment Variables
After running bootstrap, source the `.env` file:
```bash
source .env
```

Key environment variables:
- `POSTGRES_URL`: Database connection string
- `DEBUG`: Enable debug mode (1 for development)
- `CORS_ORIGIN`: Allowed CORS origin (default: http://localhost:5173)
- `COOKIE_SECRET`: Session cookie secret

## Backend (Python/FastAPI)

### Running the Backend
```bash
# Development mode (from project root)
python -m emuse.main --verbose

# Or using the installed script
emuse --verbose
```

The backend runs on `http://0.0.0.0:8000`

### Testing
```bash
# Run tests with pytest
.venv/bin/pytest

# Run tests with coverage
.venv/bin/coverage run -m pytest
.venv/bin/coverage report

# Tests require 90% coverage (configured in pyproject.toml)
```

### Linting and Formatting
```bash
# Run ruff linter
.venv/bin/ruff check .

# Run ruff with auto-fix
.venv/bin/ruff check --fix .

# Run pre-commit hooks manually
.venv/bin/pre-commit run --all-files
```

Code style:
- Line length: 79 characters
- Formatter: yapf
- Linter: ruff (extensive ruleset including flake8-async, bugbear, bandit, etc.)
- Single quotes for inline strings

### Architecture

#### Project Structure
The project uses a **src-layout** structure:
- Backend: `src/emuse/` (Python package)
- Frontend: `src/ui/` (React/TypeScript)
- Version: `src/emuse/__version__.py` (single source of truth)
- Logging config: `src/emuse/logconfig.toml`

#### Database Layer (`src/emuse/database.py`)
- Uses `psycopg` (async) with connection pooling (`psycopg_pool.AsyncConnectionPool`)
- Connections are autocommit by default with dict row factory
- Database connections are injected via FastAPI dependency: `InjectConnection`
- Schema: All tables live in the `v1` schema

#### Session Management (`src/emuse/session.py`)
- Singleton `Session` class using `fastapi-sessions`
- In-memory backend (not persistent across restarts)
- Cookie-based sessions with UUIDv7 session IDs
- Session data includes `session_id` and `account_id`

#### Models (`src/emuse/models/`)
- Pydantic models with extra fields forbidden
- `Account` model handles authentication with PBKDF2-SHA256 password hashing (100k iterations)
- Models include methods for `save()`, `get()`, and `authenticate()`

#### Endpoints (`src/emuse/endpoints/`)
- Each endpoint is a separate module exporting a router
- Routers are registered in `src/emuse/endpoints/__init__.py`
- Current endpoints: index, login, logout
- Endpoints use FastAPI dependency injection for database connections

#### Application Lifecycle (`src/emuse/main.py`)
- `fastapi_lifespan()`: Manages database pool startup/shutdown
- Database pool is stored in `request.state.postgres`
- Static files served from `src/emuse/static/`
- CORS configured via settings
- Logging configured from `src/emuse/logconfig.toml`

#### Utilities (`src/emuse/common.py`)
- `Settings`: Pydantic settings with environment variable support
- `new_uuid7()`: Generates UUIDv7 for time-sortable IDs
- `log_config()`: Loads logging configuration from TOML
- `configure_logging()`: Configures Python logging for the application
- `StatusEndpointFilter`: Filters /status endpoint logs

## Frontend (React/TypeScript)

### Running the Frontend
```bash
cd src/ui
npm run dev
```

The frontend runs on `http://localhost:5173` and proxies to the backend.

### Building the Frontend
```bash
cd src/ui
npm run build
```

### Linting
```bash
cd src/ui
npm run lint
```

### Architecture

The UI uses:
- **React 19.1.1**: Latest React version
- **Vite 7.1.7**: Build tool and dev server
- **TypeScript**: Strict type checking
- **Tailwind CSS**: For styling (if configured)

Key directories:
- `src/ui/src/`: React source code
- `src/ui/public/`: Static assets (logo, etc.)
- `src/ui/src/assets/`: Application assets

The main app structure is in `src/ui/src/App.tsx`, which sets up the application routes and layout.

## Database Schema

Schema is defined in `postgres/emuse.sql`:

### Tables
- **v1.accounts**: User accounts with authentication, profile info, and access flags
- **v1.poetry**: Poetry entries with ownership, privacy levels, and metadata

### Key Patterns
- UUIDs for all IDs (prefer UUIDv7 for time-sortable IDs)
- All timestamps use `TIMESTAMP WITH TIME ZONE`
- Privacy levels: 'public', 'logged-in-only', 'friends-only', 'private'

## Docker Compose

The `compose.yml` defines:
- PostgreSQL service with initialization scripts from `postgres/`
- Database init scripts run automatically on first start
- Password: "password" (development only)

## Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:
- Shell script checks
- TOML/YAML validation
- Debug statement detection
- End-of-file fixing
- yapf formatting
- ruff linting with auto-fix

Hooks are installed automatically by the bootstrap script.

## Important Notes

### Project Structure
- **Src-layout structure**: All source code is under `src/` directory
- Backend package: `src/emuse/`
- Frontend app: `src/ui/`
- Version management: `src/emuse/__version__.py`

### Security & Authentication
- Password hashing: PBKDF2-SHA256 with 100k iterations and per-user salts
- Sessions: In-memory only (lost on server restart)
- UUIDs: Uses UUIDv7 (from `uuid-utils`) for time-sortable unique identifiers
- Cookie-based authentication with secure session management

### Testing & Quality
- Test framework: pytest
- Coverage requirement: ≥90% (configured in pyproject.toml)
- Pre-commit hooks run automatically (ruff, yapf, etc.)

### Database
- Schema namespace: All tables in `v1` schema
- **Warning**: `postgres/emuse.sql` contains `DROP SCHEMA v1 CASCADE` - dangerous for production
- Initialization: Automatic via Docker Compose on first start

### Build & Deployment
- Build system: Hatchling with src-layout
- Logging: Configured via `src/emuse/logconfig.toml` (TOML format)

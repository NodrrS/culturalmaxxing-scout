# REST API Template

A production-ready FastAPI template for building scalable REST APIs with Docker support, rate limiting, logging, and security features.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Docker Support**: Multi-stage Dockerfile and docker-compose for easy deployment
- **Rate Limiting**: Built-in request rate limiting with SlowAPI
- **Logging**: Comprehensive logging system with file and console output
- **Security**: Non-root user in Docker, input validation, encryption utilities
- **Configuration**: JSON-based configuration management via `config_loader`
- **Health Checks**: Built-in health check endpoints (includes optional Redis status)
- **Development Ready**: Hot reload support for development

## Project Structure

```
python_rest_api_template/
├── src/
│   ├── api_endpoints/              # API route definitions
│   │   ├── routers/
│   │   │   └── specific_router_group/
│   │   │       └── example_router.py   # Reference router — copy this pattern
│   │   └── root_endpoint.py            # Root / health-check endpoint
│   ├── core_specs/                 # Core configuration and static data
│   │   ├── configuration/
│   │   │   ├── config_file.json        # Endpoint, network, logging settings
│   │   │   └── config_loader.py        # Loads config_file.json → config_loader
│   │   └── data/
│   │       ├── general_data.json         # Static reference data
│   │       └── data_loader.py            # Loads general_data.json → data_loader
│   ├── models/
│   │   └── models_example.py           # Pydantic model pattern (Base/Create/Update/Response)
│   ├── resources/                  # Database and cache assets
│   │   ├── cache/                      # Optional Redis cache layer
│   │   │   ├── redis_client.py         # Connection + enable flag
│   │   │   └── redis_service.py        # cache_get / cache_set / cache_delete
│   │   ├── db/                         # Migration files (add when needed)
│   │   └── mock_db_jsons/              # Mock JSON tables (add when needed)
│   └── utils/
│       ├── custom_logger.py        # Logging configuration (log_handler)
│       ├── limiter.py              # Shared SlowAPI limiter instance
│       ├── request_limiter.py      # 429 handler for rate-limit exceeded
│       ├── validators.py           # Email, password, phone, token, UUID validators
│       ├── en_de_crypt.py          # RSA encrypt/decrypt (requires .env keys)
│       ├── keys_generator.py       # One-off script to generate RSA key pairs
│       ├── secure_file_io.py       # Hardened atomic file read/write helpers
│       └── pycache_n_logs_deleter.py  # Dev utility to purge __pycache__ / logs
├── logs/                           # Log files (created automatically)
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── start.sh / start.bat            # Dev setup and launch scripts
├── DOCKERFILE                      # Docker build configuration
├── docker-compose.yml              # Docker compose configuration
├── .env / .env.example             # Environment variables template
├── .dockerignore
├── .gitignore
├── .pylintrc
└── README.md
```

## Quick Start

### Option 1: Run with Python (Development)

1. **Clone and setup**:
   ```bash
   cd templates/python_rest_api_template
   python -m venv venv
   source venv/bin/activate          # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env.local        # or copy .env on Windows
   # Edit .env.local — set E_PRIVATE_KEY, E_PRIVATE_PASSWORD, E_PUBLIC_KEY
   # (run src/utils/keys_generator.py once to generate them)
   ```

3. **Run the application**:
   ```bash
   python main.py
   # or: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the API**:
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Option 2: Run with Docker (Production)

```bash
cd templates/python_rest_api_template
docker-compose up --build
```

Or manually:

```bash
docker build -t rest-api-template .
docker run -p 8000:8000 --env-file .env rest-api-template
```

## Configuration

### Environment Variables (.env)

```bash
# Server (overridden by config_file.json when using python main.py)
SERVER_PORT=8000
HOST=0.0.0.0
RELOAD=false
WORKERS=1

# RSA encryption keys (required by en_de_crypt.py)
E_PRIVATE_KEY=your_private_key_here
E_PRIVATE_PASSWORD=your_private_password_here
E_PUBLIC_KEY=your_public_key_here

# Logging
LOG_LEVEL=info

# API metadata (read by main.py)
API_TITLE=REST API Template
API_VERSION=1.0.0
API_DESCRIPTION=A template for building REST APIs with FastAPI

# Redis (optional — default off; app runs normally without it)
REDIS_ENABLED=false
REDIS_HOST=localhost       # use "redis" when running via docker-compose
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

### JSON Configuration (`config_file.json` + `config_loader`)

`config_loader.py` reads `config_file.json` at import time and exposes the result as `config_loader` (a dict). Every router should pull its prefix, tag, route, and rate-limit values from here rather than hard-coding them.

**Sections in `config_file.json`:**

| Section | Purpose |
|---|---|
| `defaults` | Shared paths and defaults |
| `logging` | Log level, directory, file name prefix |
| `email_validation` | Allowed email providers and TLDs (used by `validators.py`) |
| `network` | Uvicorn host, port, workers, reload |
| `endpoints` | Per-endpoint prefix, tag, route, and rate-limit settings |

**Endpoint config shape** (one entry per route):

```json
"example_endpoint": {
    "request_limit": 3,
    "unit_of_time_for_limit": "m",
    "endpoint_prefix": "/subsection",
    "endpoint_tag": "subsection",
    "endpoint_route": "/endpoint_name"
}
```

**Usage in a router:**

```python
from src.core_specs.configuration.config_loader import config_loader

cfg = config_loader["endpoints"]["example_endpoint"]

router = APIRouter(
    prefix=cfg["endpoint_prefix"],
    tags=[cfg["endpoint_tag"]],
)

@router.get(cfg["endpoint_route"])
@limiter.limit(f"{cfg['request_limit']}/{cfg['unit_of_time_for_limit']}")
async def my_endpoint(request: Request):
    ...
```

### Static Data (`general_data.json` + `data_loader`)

`data_loader.py` works the same way as `config_loader` but loads `src/core_specs/data/general_data.json`. Use it for reference data that is not environment-specific (e.g. supported languages, lookup tables).

```python
from src.core_specs.data.data_loader import data_loader

languages = data_loader["languages"]
```

## Adding New Endpoints

Use `src/api_endpoints/routers/specific_router_group/example_router.py` as the canonical reference. It demonstrates every pattern the template expects:

1. **Config-driven router** — prefix, tag, routes, and rate limits from `config_loader`
2. **Pydantic models** — `ExampleItemCreate` / `ExampleItemResponse` from `src/models/models_example.py`
3. **Validators** — optional `contact_email` validated via `validate_email_format`
4. **Static data** — reads `languages` from `data_loader` in the list endpoint
5. **Logging** — `log_handler` for debug/info messages
6. **Rate limiting** — `@SlowLimiter.limit(...)` on every route

See `src/api_endpoints/routers/specific_router_group_2/example_router.py` and
`src/resources/example_item_service.py` for optional Redis caching via the service layer.

**Steps to add a new endpoint group:**

1. Add entries under `endpoints` in `config_file.json`.
2. Copy `example_router.py` into a new file under `src/api_endpoints/routers/<your_group>/`.
3. Create matching Pydantic models in `src/models/` (follow the Base / Create / Update / Response split in `models_example.py`).
4. Register the router in `main.py`:
   ```python
   from src.api_endpoints.routers.your_group.your_router import router as your_router
   app.include_router(your_router)
   ```

**Example endpoints shipped with the template:**

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check (includes Redis status when configured) |
| `GET` | `/subsection/endpoint_name` | List example items |
| `GET` | `/subsection/items/{item_id}` | Get item by ID (optional Redis cache demo) |

## Models (`src/models/`)

`models_example.py` shows the recommended Pydantic split for any entity:

| Class | Role |
|---|---|
| `*Base` | Domain fields shared by every variant |
| `*Create` | POST body (no server-managed fields like `id`) |
| `*Update` | PATCH body (all fields optional) |
| `*<Entity>` | Full persisted record including `id` |
| `*Response` | API response shape (decoupled from storage) |

Rename or replace this file per project; keep the split.

## Optional Redis Cache (`src/resources/cache/`)

Redis is an **optional** cache layer. The application starts and serves requests normally when Redis is disabled or unreachable. PostgreSQL (when added) remains the source of truth; Redis is only for temporary cached data.

| Module | Role |
|---|---|
| `redis_client.py` | Reads env config, connects when `REDIS_ENABLED=true`, exposes `get_redis_status()` |
| `redis_service.py` | `cache_get`, `cache_set`, `cache_delete` — use these in services, not in routers directly against Redis |

**Enable locally:**

```bash
REDIS_ENABLED=true
REDIS_HOST=localhost
```

**Enable with Docker Compose** (Redis service is included in `docker-compose.yml`):

```bash
REDIS_ENABLED=true
REDIS_HOST=redis
```

**Health check response** (`GET /`):

| Redis state | `"redis"` value |
|---|---|
| Disabled (`REDIS_ENABLED=false`) | `"disabled"` |
| Enabled and connected | `"connected"` |
| Enabled but unreachable | `"unavailable"` |

The API stays `"status": "ok"` even when Redis is unavailable.

**Usage in business logic** (see `src/resources/example_item_service.py`):

```python
from src.resources.cache.redis_service import cache_get, cache_set

async def get_user_profile(user_id: str):
    cache_key = f"user:{user_id}"

    cached_user = cache_get(cache_key)
    if cached_user:
        return cached_user

    user = database.get_user(user_id)  # your persistence layer

    cache_set(cache_key, user, expiration_seconds=600)
    return user
```

## Utilities (`src/utils/`)

| Module | When to use |
|---|---|
| `custom_logger.py` | `log_handler` — use everywhere instead of `print` |
| `limiter.py` | Shared `limiter` instance; decorate routes with `@limiter.limit(...)` |
| `request_limiter.py` | Registered in `main.py` as the global 429 handler |
| `validators.py` | `validate_email_format`, `validate_password_format`, `validate_phone_format`, token/UUID checks |
| `en_de_crypt.py` | `encrypt_in` / `decrypt_out` for RSA-encrypted request fields |
| `keys_generator.py` | Run once to generate `E_PRIVATE_KEY` / `E_PUBLIC_KEY` for `.env` |
| `secure_file_io.py` | Safe atomic file reads/writes with path confinement |
| `pycache_n_logs_deleter.py` | Dev cleanup script — set `ROOT_FOLDER` before running |

## Security Features

- **Rate Limiting**: Configurable per-endpoint rate limiting via `config_file.json`
- **Input Validation**: Pydantic models + `validators.py` helpers
- **Encryption**: RSA utilities in `en_de_crypt.py` (keys from environment)
- **Non-root Docker**: Container runs as non-root user
- **Environment Variables**: Sensitive data via `.env`, never committed

## Logging

- **File Logging**: Timestamped log files in `logs/`
- **Console Logging**: Structured output for containers
- **Configurable Levels**: Set via `logging.logging_level` in `config_file.json`
- **Request Logging**: Rate-limit violations logged at warning level

## Docker Features

### Multi-stage Build
- **Builder stage**: Installs dependencies
- **Production stage**: Minimal runtime image
- **Security**: Non-root user execution
- **Health checks**: Built-in container health monitoring

### Docker Compose
- **Production**: Optimized for deployment
- **Services**: Optional Redis cache (enabled via env); PostgreSQL stub commented for extension
- **Volumes**: Persistent log storage and Redis data

## Development

### Hot Reload

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Or use `start.bat` / `start.sh` and choose development mode.

### Adding Dependencies

```bash
pip install new-package
pip freeze > requirements.txt
```

### Running Tests

```bash
pip install pytest
pytest tests/    # add a tests/ directory as needed
```

## Deployment

1. Update environment variables for production.
2. Build: `docker build -t your-api:latest .`
3. Deploy: `docker-compose up -d`

Compatible with AWS ECS/Fargate, Google Cloud Run, Azure Container Instances, Heroku, DigitalOcean App Platform, and similar.

## API Documentation

Once running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Customization

### Changing the API Title / Description

Set `API_TITLE`, `API_VERSION`, and `API_DESCRIPTION` in `.env`, or edit the defaults in `main.py`.

### Adding Database Support

1. Uncomment the database service in `docker-compose.yml`.
2. Add database dependencies to `requirements.txt`.
3. Place migration files in `src/resources/db/` and mock fixtures in `src/resources/mock_db_jsons/`.
4. Create connection utilities in `src/utils/` or a dedicated `src/resources/` module.

### Adding Authentication

1. Install auth dependencies (e.g. `python-jose`, `passlib`).
2. Create auth utilities in `src/utils/`.
3. Add authentication middleware or dependencies in `main.py`.

## Requirements

- Python 3.12+
- Docker (optional)
- Docker Compose (optional)

## Contributing

This is a template — customize it for your specific needs:

1. Update `config_file.json` and `.env`
2. Copy `example_router.py` and `models_example.py` as starting points
3. Implement your business logic
4. Add tests
5. Update this README

## License

This template is provided as-is for educational and development purposes.

# Carrier Platform Architecture

## Overview

Carrier (Centry) is a plugin-based performance testing and engagement automation platform built with Python/Flask. It uses a microservices architecture with comprehensive multi-tenant support and a sophisticated plugin system.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Client                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Traefik                                  │
│                    (Reverse Proxy)                               │
└───────┬──────────────────────────────────────────┬──────────────┘
        │                                           │
        │ Forward Auth                              │ Main Traffic
        ▼                                           ▼
┌──────────────────┐                    ┌──────────────────────┐
│   pylon_auth     │                    │       pylon          │
│ (Auth Service)   │                    │  (Main Application)  │
│                  │                    │                      │
│ • auth_root      │                    │ • 32+ Plugins        │
│ • auth_core      │                    │ • REST APIs          │
│ • auth_oidc      │                    │ • RPC Services       │
│ • auth_manager   │                    │ • UI Rendering       │
└────────┬─────────┘                    └──────────┬───────────┘
         │                                         │
         └─────────────┬───────────────────────────┘
                       │
         ┌─────────────┴─────────────────────────────┐
         │                                            │
         ▼                                            ▼
┌──────────────────┐                    ┌──────────────────────┐
│    RabbitMQ      │                    │     PostgreSQL       │
│  (RPC/Events)    │                    │  (Multi-tenant DB)   │
└──────────────────┘                    └──────────────────────┘
         │
         └─────────────┬─────────────────┬────────────┬────────┐
                       │                 │            │        │
                       ▼                 ▼            ▼        ▼
              ┌──────────┐      ┌──────────┐  ┌───────┐  ┌──────┐
              │  Redis   │      │  MinIO   │  │ Vault │  │ Loki │
              │ (Cache)  │      │(Storage) │  │(Sec.) │  │(Logs)│
              └──────────┘      └──────────┘  └───────┘  └──────┘
```

## Core Components

### 1. Pylon Framework

The Carrier platform is built on the **Pylon** framework, which provides:

- **Plugin System**: Dynamic plugin loading with dependency resolution
- **Module Lifecycle**: Standardized init/deinit hooks for plugins
- **Configuration Management**: YAML-based config with environment variable support
- **Service Discovery**: Automatic registration of APIs, RPCs, and events

**Configuration Seed**: `CORE_CONFIG_SEED=file:/data/config/pylon.yml`

### 2. Dual-Pylon Architecture

The platform uses two Pylon instances:

#### pylon (Main Application)
- **Port**: 8080
- **Purpose**: Main business logic and UI
- **Plugins**: 32+ plugins for features
- **Config**: `config/pylon.yml`

#### pylon_auth (Authentication Service)
- **Port**: 8080 (internal)
- **Purpose**: Authentication and authorization
- **Plugins**: auth_root, auth_core, auth_oidc, auth_manager, auth_init, auth_mappers
- **Config**: `config/pylon_auth.yml`
- **Integration**: Traefik forward-auth middleware

### 3. Service Infrastructure

#### Traefik (Reverse Proxy)
- **Port**: 80 (HTTP), 443 (HTTPS)
- Dynamic routing with labels
- Forward authentication via pylon_auth
- SSL termination (optional)

#### PostgreSQL (Database)
- **Multi-tenant Support**: Schema isolation per project
- **Schema Pattern**: `project_{project_id}` for tenant data
- **Shared Schema**: `carrier` for global data
- **Context Switching**: SQLAlchemy execution options for schema translation

#### RabbitMQ (Message Queue)
- **Virtual Host**: `carrier`
- **Queues**: `rpc`, `events`
- **Purpose**:
  - RPC: Synchronous inter-plugin communication
  - Events: Asynchronous event broadcasting

#### Redis (Cache & Sessions)
- Session storage for Flask
- Cache for frequently accessed data
- Pub/sub for real-time updates

#### MinIO (Object Storage)
- S3-compatible storage
- **Buckets**: `module`, `config`, custom per-plugin
- Artifact storage for test results

#### Vault (Secrets Management)
- Secure storage of sensitive data
- Plugin configurations
- API keys and tokens

#### Loki (Log Aggregation)
- Centralized logging
- Buffered log collection
- Query interface for debugging

#### Keycloak (OAuth/OIDC Provider)
- Identity and access management
- OAuth2/OpenID Connect flows
- User federation
- Custom themes (config/keycloak/themes)

## Database Architecture

### Multi-Tenant Design

```
┌──────────────────────────────────────────────────────────┐
│                    PostgreSQL                             │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Schema: carrier (Shared)                                │
│  ├── projects                                            │
│  ├── users                                               │
│  ├── roles                                               │
│  ├── permissions                                         │
│  └── quotas                                              │
│                                                           │
│  Schema: project_1 (Tenant 1)                            │
│  ├── backend_performance_test_results                    │
│  ├── backend_performance_tests                           │
│  ├── ui_performance_tests                                │
│  └── engagement_tasks                                    │
│                                                           │
│  Schema: project_2 (Tenant 2)                            │
│  ├── backend_performance_test_results                    │
│  ├── backend_performance_tests                           │
│  ├── ui_performance_tests                                │
│  └── engagement_tasks                                    │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Schema Switching

```python
# Context manager for schema switching
with db.with_project_schema_session(project_id):
    # Queries here use project_{project_id} schema
    results = TestResult.query.all()
```

## Plugin Architecture

### Plugin Structure

Every plugin follows this structure:

```
plugin_name/
├── __init__.py              # Module export
├── metadata.json            # Plugin definition
├── module.py                # Main Module class
├── config.yml               # Configuration
├── requirements.txt         # Python dependencies
├── api/
│   └── v1/                  # REST API endpoints
├── rpc/                     # RPC methods
├── models/                  # SQLAlchemy models
├── slots/                   # UI slots
├── templates/               # Jinja2 templates
├── static/
│   ├── js/                  # JavaScript
│   └── css/                 # Stylesheets
└── tools/                   # Utility functions
```

### Plugin Lifecycle

```python
class Module(ModuleModel):
    def __init__(self, context, descriptor):
        self.context = context
        self.descriptor = descriptor

    def init(self):
        # 1. Initialize database models
        # 2. Register API endpoints
        # 3. Register RPC methods
        # 4. Subscribe to events
        # 5. Register UI slots
        # 6. Set up background tasks
        pass

    def deinit(self):
        # Cleanup resources
        pass
```

### Plugin Dependencies

Defined in `metadata.json`:

```json
{
  "name": "backend_performance",
  "version": "1.0.0",
  "depends_on": ["shared", "projects", "tasks", "theme"],
  "init_after": []
}
```

**Dependency Resolution**:
- `depends_on`: Required plugins (must be loaded)
- `init_after`: Initialization order (optional)

### Plugin Categories

#### Core Foundation
- **shared**: Base library (db, rpc_tools, api_tools)
- **integrations**: Integration framework
- **market**: Plugin marketplace

#### Authentication
- **auth**: Main auth utilities
- **auth_root**: Root auth plugin (pylon_auth)
- **auth_core**: Core auth service (pylon_auth)
- **auth_oidc**: OpenID Connect (pylon_auth)
- **auth_manager**: User management (pylon_auth)

#### UI/Theme
- **theme**: Theme engine
- **design-system**: Component library
- **admin**: Admin interface

#### Business Logic
- **projects**: Project management
- **tasks**: Task execution
- **secrets**: Secret storage
- **artifacts**: Artifact management
- **scheduling**: Cron jobs

#### Testing
- **backend_performance**: Backend performance tests
- **ui_performance**: UI performance tests
- **performance_test_suite**: Test suites
- **performance_analysis**: Analysis engine

#### Cloud Integrations
- **aws_integration**: AWS services
- **gcp_integration**: GCP services
- **s3_integration**: S3 storage
- **kubernetes**: K8s integration

#### Reporting
- **reporter_email**: Email reports
- **reporter_jira**: Jira integration
- **reporter_engagement**: Engagement reports

#### Advanced Features
- **engagements**: Engagement management
- **issues**: Issue tracking
- **kanban**: Kanban boards
- **audit_logs**: Audit logging
- **shared_orch**: Orchestration library

## Communication Patterns

### REST API

```python
# plugins/*/api/v1/*.py
from tools import api_tools

class API(api_tools.APIModeHandler):
    @auth.decorators.check_api(["projects"])
    def get(self, project_id: int):
        # Handle GET request
        return {"status": "success"}

    @auth.decorators.check_api(["projects"])
    def post(self, project_id: int):
        # Handle POST request
        data = request.json
        return {"status": "created"}
```

### RPC (Remote Procedure Call)

```python
# plugins/*/rpc/*.py
from tools import rpc_tools

class RPC:
    @web.rpc("backend_performance_test_run", "run")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def run_test(self, project_id, test_id):
        # Execute test
        return {"result": "completed"}

# Calling RPC from another plugin
result = self.context.rpc_manager.timeout(5).backend_performance_test_run(
    project_id=1, test_id=123
)
```

### Events

```python
# Firing an event
self.context.event_manager.fire('test_completed', {
    'test_id': 123,
    'status': 'passed'
})

# Subscribing to an event
def init(self):
    self.context.event_manager.register_listener('test_completed',
                                                   self.on_test_completed)

def on_test_completed(self, event_data):
    print(f"Test {event_data['test_id']} completed")
```

## Authentication Flow

```
1. Client → Traefik (port 80/443)
   │
   ├─→ Middleware: pylon-auth (forward-auth)
   │   │
   │   └─→ pylon_auth:8080/forward-auth/auth?target=rpc
   │       │
   │       ├─→ Check session (Redis)
   │       ├─→ Validate JWT (Keycloak)
   │       ├─→ Check permissions (auth_core)
   │       │
   │       └─→ Return 200 (authenticated) or 401 (denied)
   │
   └─→ If authenticated → pylon:8080
       │
       └─→ Request handler with permission decorators
           │
           └─→ @auth.decorators.check_api(["permission"])
```

### Permission System

```python
# Define permissions in plugin module
def init(self):
    self.descriptor.register_scope('backend_performance',
                                    'Backend Performance Testing')

# Protect API endpoints
@auth.decorators.check_api(["projects"])
def get(self, project_id: int):
    # Only users with "projects" permission can access
    pass

# Check permissions in code
if not auth.user_has_permission('backend_performance', project_id):
    return {"error": "Forbidden"}, 403
```

## Configuration Management

### Configuration Files

```
config/
├── pylon.yml              # Main app config
├── pylon_auth.yml         # Auth service config
├── pylon-example.yml      # Config template
├── .env                   # Environment variables
├── Makefile              # Deployment automation
└── keycloak/
    └── themes/           # Keycloak customization
```

### Configuration Loading

```yaml
# pylon.yml
modules:
  plugins:
    provider:
      type: folder
      path: /data/pylon/plugins
  config:
    provider:
      type: folder
      path: /data/pylon/configs

configs:
  market:
    local_preordered_plugins:
      - integrations
      - shared
      - backend_performance
      # ... more plugins

sessions:
  redis:
    host: redis
    password: ${REDIS_PASSWORD}

rpc:
  rabbitmq:
    host: rabbitmq
    vhost: carrier
```

### Environment Variables

Key variables in `.env`:

```bash
# Core
CORE_CONFIG_SEED=file:/data/config/pylon.yml
MODULES_PATH=plugins

# Database
DATABASE_VENDOR=postgres
POSTGRES_HOST=carrier-postgres
POSTGRES_DB=carrier
POSTGRES_SCHEMA=carrier

# Services
REDIS_PASSWORD=password
RABBIT_USER=user
RABBIT_PASSWORD=password
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=password

# Tasks
INTERCEPTOR_TASKS=5
INTERNAL_TASKS=15
```

## Deployment

### Docker Compose Services

```yaml
services:
  traefik:       # Reverse proxy
  postgres:      # Database
  redis:         # Cache/Sessions
  rabbitmq:      # Message queue
  vault:         # Secrets
  minio:         # Object storage
  influx:        # Time-series DB
  dedoc:         # Document parsing
  interceptor:   # Task executor
  keycloak:      # OAuth/OIDC
  loki:          # Log aggregation
  pylon:         # Main app
  pylon_auth:    # Auth service
```

### Startup Sequence

```bash
# 1. Deploy infrastructure
make up INTERFACE=eth0

# This does:
# - Set APP_IP based on network interface
# - Create pylon.yml from example if needed
# - Start all Docker services
# - Wait for services to be healthy

# 2. Automatic plugin loading
# - Pylon reads config/pylon.yml
# - Discovers plugins in /data/pylon/plugins
# - Resolves dependencies
# - Loads plugins in order
# - Initializes each plugin

# 3. Services become available
# - HTTP: http://<APP_IP>
# - HTTPS: https://<APP_IP> (if SSL configured)
```

## Development Workflow

### Adding a New Plugin

1. Create plugin directory: `pylon/plugins/my_plugin/`
2. Create `metadata.json`:
   ```json
   {
     "name": "my_plugin",
     "version": "1.0.0",
     "depends_on": ["shared"]
   }
   ```
3. Create `module.py` with Module class
4. Implement init() method
5. Add to preordered_plugins in pylon.yml
6. Restart pylon service

### Making Changes

1. Edit plugin code in `pylon/plugins/<plugin>/`
2. Restart service: `docker-compose restart pylon`
3. Check logs: `docker-compose logs -f pylon`

### Debugging

```bash
# Enable debug logging
CORE_DEBUG_LOGGING=yes

# View logs
docker-compose logs -f pylon
docker-compose logs -f pylon_auth

# Access container
docker exec -it centry-pylon-1 bash

# Database access
docker exec -it centry-postgres-1 psql -U carrier -d carrier

# RabbitMQ management
http://<APP_IP>:15672  (user/password)
```

## Best Practices

### Plugin Development

1. **Always declare dependencies** in metadata.json
2. **Use RPC for inter-plugin communication** instead of direct imports
3. **Follow schema isolation** for multi-tenant data
4. **Use permission decorators** on all API endpoints
5. **Handle errors gracefully** with rpc_tools.wrap_exceptions
6. **Register UI slots** instead of hardcoding HTML

### Database

1. **Use context manager** for schema switching:
   ```python
   with db.with_project_schema_session(project_id):
       # queries here
   ```
2. **Define models with AbstractBaseMixin** for common fields
3. **Use alembic migrations** for schema changes
4. **Index foreign keys** for performance

### Security

1. **Never bypass auth decorators** on APIs
2. **Validate input** on all user-facing endpoints
3. **Use Vault** for sensitive configuration
4. **Audit all changes** via audit_logs plugin
5. **Follow least privilege** for permissions

### Performance

1. **Use Redis caching** for expensive queries
2. **Batch RPC calls** when possible
3. **Implement pagination** on list endpoints
4. **Use async tasks** for long-running operations
5. **Monitor with Loki** for bottlenecks

## Troubleshooting

### Common Issues

**Plugin not loading:**
- Check metadata.json syntax
- Verify all dependencies are present
- Check logs for import errors

**Database connection errors:**
- Verify POSTGRES_* env vars
- Check postgres service is healthy
- Test connection from pylon container

**RPC timeouts:**
- Increase timeout: `rpc_manager.timeout(30)`
- Check RabbitMQ is running
- Verify queue names match config

**Permission errors:**
- Check user has required permission
- Verify permission registered in plugin init()
- Check Keycloak group mappings

**UI not rendering:**
- Check theme plugin is loaded
- Verify slots are registered
- Check browser console for JS errors

## References

- **Main Config**: `config/pylon.yml`
- **Auth Config**: `config/pylon_auth.yml`
- **Environment**: `.env`
- **Deployment**: `Makefile`
- **Plugins**: `pylon/plugins/*/module.py`
- **Auth Core**: `pylon_auth/plugins/auth_core/module.py`

# Carrier Plugin System

## Overview

Carrier uses a sophisticated plugin architecture powered by the Pylon framework. Plugins are self-contained modules that provide specific functionality and can declare dependencies on other plugins. The system handles automatic dependency resolution, ordered loading, and lifecycle management.

## Plugin Structure

### Minimal Plugin Layout

```
plugin_name/
├── __init__.py              # Required: Module export
├── metadata.json            # Required: Plugin definition
├── module.py                # Required: Main Module class
├── config.yml               # Optional: Plugin configuration
└── requirements.txt         # Optional: Python dependencies
```

### Full Plugin Layout

```
plugin_name/
├── __init__.py              # Module export
├── metadata.json            # Plugin metadata
├── module.py                # Module class
├── config.yml               # Configuration
├── requirements.txt         # Python dependencies
│
├── api/                     # REST API endpoints
│   └── v1/
│       ├── __init__.py
│       └── endpoint.py
│
├── rpc/                     # RPC methods
│   ├── __init__.py
│   └── methods.py
│
├── models/                  # Database models
│   ├── __init__.py
│   └── model.py
│
├── slots/                   # UI slot handlers
│   ├── __init__.py
│   └── slot.py
│
├── templates/               # Jinja2 templates
│   ├── content.html
│   └── scripts.html
│
├── static/                  # Static assets
│   ├── js/
│   │   └── script.js
│   └── css/
│       └── style.css
│
├── tools/                   # Utility functions
│   ├── __init__.py
│   └── helpers.py
│
├── events/                  # Event handlers
│   ├── __init__.py
│   └── handlers.py
│
└── migrations/              # Database migrations
    └── alembic/
```

## Core Plugin Files

### 1. metadata.json

Defines plugin identity and dependencies.

```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Plugin description",
  "depends_on": [
    "shared",
    "auth",
    "theme"
  ],
  "init_after": [
    "projects"
  ]
}
```

**Fields:**
- `name` (required): Unique plugin identifier
- `version` (required): Semantic version
- `author`: Plugin author
- `description`: Brief description
- `depends_on`: Required plugins (must be loaded)
- `init_after`: Plugins that should initialize first (optional)

### 2. module.py

Main plugin class.

```python
from pylon.core.tools import module
from pylon.core.tools import log

class Module(module.ModuleModel):
    """
    Plugin module
    """

    def __init__(self, context, descriptor):
        """
        Initialize module

        Args:
            context: Pylon context with managers
            descriptor: Plugin descriptor with metadata
        """
        self.context = context
        self.descriptor = descriptor

    def init(self):
        """
        Initialize plugin - called on startup
        """
        log.info("Initializing my_plugin")

        # 1. Initialize database models
        self._init_db()

        # 2. Register API endpoints
        self._init_api()

        # 3. Register RPC methods
        self._init_rpc()

        # 4. Register events
        self._init_events()

        # 5. Register UI slots
        self._init_slots()

        # 6. Register permissions
        self._init_permissions()

    def deinit(self):
        """
        Cleanup plugin - called on shutdown
        """
        log.info("Deinitializing my_plugin")

    def _init_db(self):
        """Initialize database models"""
        from .models import MyModel
        # Models auto-register with SQLAlchemy

    def _init_api(self):
        """Register API endpoints"""
        from .api.v1 import endpoint
        self.context.api_manager.add_resource(
            endpoint.API,
            "/api/v1/my_plugin/<int:project_id>/action"
        )

    def _init_rpc(self):
        """Register RPC methods"""
        from .rpc import methods
        self.context.rpc_manager.register_function(
            methods.RPC(self.context, self.descriptor).my_method,
            name="my_plugin_method"
        )

    def _init_events(self):
        """Subscribe to events"""
        from .events import handlers
        self.context.event_manager.register_listener(
            'test_completed',
            handlers.on_test_completed
        )

    def _init_slots(self):
        """Register UI slots"""
        from .slots import slot
        self.descriptor.register_slot(
            'my_plugin_content',
            slot.content,
            'Content slot description'
        )

    def _init_permissions(self):
        """Register permissions"""
        self.descriptor.register_scope(
            'my_plugin',
            'My Plugin Access'
        )
```

### 3. __init__.py

Export the Module class.

```python
from .module import Module
```

### 4. config.yml

Plugin-specific configuration.

```yaml
settings:
  enabled: true
  max_retries: 3
  timeout: 30

features:
  advanced_mode: false
  debug: false

api:
  rate_limit: 100
  cache_ttl: 300
```

Access in module:

```python
def init(self):
    config = self.descriptor.config
    max_retries = config.get('settings', {}).get('max_retries', 3)
```

### 5. requirements.txt

Python package dependencies.

```
requests>=2.28.0
pandas>=1.5.0
numpy>=1.23.0
```

## Plugin Lifecycle

### Loading Sequence

```
1. Pylon starts
   ↓
2. Read config/pylon.yml
   ↓
3. Scan /data/pylon/plugins/ for metadata.json
   ↓
4. Build dependency graph
   ↓
5. Resolve dependencies
   ↓
6. Sort plugins by dependencies
   ↓
7. For each plugin in order:
   │
   ├─→ Import module
   ├─→ Instantiate Module class
   ├─→ Call init()
   └─→ Register with context
   ↓
8. All plugins loaded
   ↓
9. Start Flask app
```

### Initialization Phases

```python
def init(self):
    # Phase 1: Database Setup
    # - Define models
    # - Run migrations
    # - Create tables

    # Phase 2: Service Registration
    # - Register APIs
    # - Register RPCs
    # - Register slots

    # Phase 3: Integration
    # - Subscribe to events
    # - Set up background tasks
    # - Initialize connections

    # Phase 4: Configuration
    # - Load settings
    # - Validate config
    # - Set defaults
```

## Dependency Management

### Declaring Dependencies

```json
{
  "name": "backend_performance",
  "depends_on": [
    "shared",      // Required: Will not load without this
    "projects",    // Required: Must be present
    "tasks",       // Required: Needed for functionality
    "theme"        // Required: UI rendering
  ],
  "init_after": [
    "scheduling"   // Optional: Initialize after this if present
  ]
}
```

### Dependency Resolution Rules

1. **depends_on**: Hard dependency
   - Plugin WILL NOT load if dependency is missing
   - Guarantees dependency is loaded before plugin

2. **init_after**: Soft dependency
   - Plugin WILL load even if dependency is missing
   - Only affects initialization order if dependency exists

### Circular Dependencies

**Not Allowed**. Will cause loading failure.

```
❌ Bad:
plugin_a depends_on plugin_b
plugin_b depends_on plugin_a

✅ Good:
plugin_a depends_on shared
plugin_b depends_on shared
```

### Common Dependency Chain

```
shared (foundation - no dependencies)
  ├─→ auth
  ├─→ theme
  │   ├─→ admin
  │   └─→ design-system
  ├─→ secrets
  ├─→ integrations
  │   ├─→ tasks
  │   ├─→ aws_integration
  │   ├─→ reporter_email
  │   └─→ s3_integration
  └─→ projects
      ├─→ backend_performance
      ├─→ ui_performance
      └─→ performance_analysis
```

## Communication Between Plugins

### Method 1: RPC (Recommended)

**Define RPC in plugin_a:**

```python
# plugin_a/rpc/methods.py
from tools import rpc_tools

class RPC:
    def __init__(self, context, descriptor):
        self.context = context
        self.descriptor = descriptor

    @web.rpc("plugin_a_get_data", "get_data")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def get_data(self, project_id, item_id):
        """Get data by ID"""
        with db.with_project_schema_session(project_id):
            item = MyModel.query.get(item_id)
            return item.to_dict() if item else None

# plugin_a/module.py
def init(self):
    from .rpc import methods
    self.context.rpc_manager.register_function(
        methods.RPC(self.context, self.descriptor).get_data,
        name="plugin_a_get_data"
    )
```

**Call RPC from plugin_b:**

```python
# plugin_b/api/v1/endpoint.py
def get(self, project_id):
    # Call plugin_a's RPC
    result = self.module.context.rpc_manager.timeout(5).plugin_a_get_data(
        project_id=project_id,
        item_id=123
    )
    return result
```

### Method 2: Events (Pub/Sub)

**Fire event in plugin_a:**

```python
# plugin_a/api/v1/endpoint.py
def post(self, project_id):
    # Do something
    result = process_data()

    # Fire event
    self.module.context.event_manager.fire('data_processed', {
        'project_id': project_id,
        'result': result,
        'timestamp': datetime.now()
    })

    return {'status': 'success'}
```

**Subscribe to event in plugin_b:**

```python
# plugin_b/events/handlers.py
def on_data_processed(event_data):
    project_id = event_data['project_id']
    result = event_data['result']

    # React to event
    log.info(f"Data processed for project {project_id}")
    update_statistics(project_id, result)

# plugin_b/module.py
def init(self):
    from .events import handlers
    self.context.event_manager.register_listener(
        'data_processed',
        handlers.on_data_processed
    )
```

### Method 3: Shared Database (Use with Caution)

Only for shared/global data, not tenant-specific.

```python
# plugin_a/models/shared_data.py
from tools import db

class SharedData(db.Base, db.AbstractBaseMixin):
    __tablename__ = 'shared_data'
    __table_args__ = {'schema': 'carrier'}  # Shared schema

    key = db.Column(db.String, unique=True)
    value = db.Column(db.Text)

# plugin_b can query this directly
from plugin_a.models.shared_data import SharedData
data = SharedData.query.filter_by(key='config').first()
```

## API Endpoints

### Defining REST APIs

```python
# plugins/my_plugin/api/v1/endpoint.py
from flask import request
from tools import api_tools, auth

class API(api_tools.APIModeHandler):
    """
    API endpoint handler
    """

    @auth.decorators.check_api(["my_plugin"])
    def get(self, project_id: int, item_id: int):
        """
        Get item by ID

        GET /api/v1/my_plugin/<project_id>/items/<item_id>
        """
        with db.with_project_schema_session(project_id):
            item = MyModel.query.get(item_id)
            if not item:
                return {'error': 'Not found'}, 404
            return item.to_dict()

    @auth.decorators.check_api(["my_plugin"])
    def post(self, project_id: int):
        """
        Create new item

        POST /api/v1/my_plugin/<project_id>/items
        Body: {"name": "Item name", "value": 123}
        """
        data = request.json

        with db.with_project_schema_session(project_id):
            item = MyModel(**data)
            db.session.add(item)
            db.session.commit()
            return item.to_dict(), 201

    @auth.decorators.check_api(["my_plugin"])
    def put(self, project_id: int, item_id: int):
        """
        Update item

        PUT /api/v1/my_plugin/<project_id>/items/<item_id>
        """
        data = request.json

        with db.with_project_schema_session(project_id):
            item = MyModel.query.get(item_id)
            if not item:
                return {'error': 'Not found'}, 404

            for key, value in data.items():
                setattr(item, key, value)

            db.session.commit()
            return item.to_dict()

    @auth.decorators.check_api(["my_plugin"])
    def delete(self, project_id: int, item_id: int):
        """
        Delete item

        DELETE /api/v1/my_plugin/<project_id>/items/<item_id>
        """
        with db.with_project_schema_session(project_id):
            item = MyModel.query.get(item_id)
            if not item:
                return {'error': 'Not found'}, 404

            db.session.delete(item)
            db.session.commit()
            return {'status': 'deleted'}
```

### Registering APIs

```python
# plugins/my_plugin/module.py
def init(self):
    from .api.v1 import endpoint

    # Register endpoint
    self.context.api_manager.add_resource(
        endpoint.API,
        "/api/v1/my_plugin/<int:project_id>/items",
        "/api/v1/my_plugin/<int:project_id>/items/<int:item_id>"
    )
```

## Database Models

### Defining Models

```python
# plugins/my_plugin/models/item.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from tools import db

class MyModel(db.Base, db.AbstractBaseMixin):
    """
    Example model
    """
    __tablename__ = 'my_plugin_items'
    __table_args__ = {'extend_existing': True}

    # AbstractBaseMixin provides: id, created_at, updated_at

    name = Column(String(128), nullable=False)
    description = Column(Text)
    value = Column(Integer, default=0)
    project_id = Column(Integer, nullable=False)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'value': self.value,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

### Multi-Tenant Models

```python
# For project-specific data
class ProjectSpecificModel(db.Base, db.AbstractBaseMixin):
    __tablename__ = 'project_data'
    # No __table_args__ with schema - dynamically set

    name = Column(String(128))

# Usage with schema switching
with db.with_project_schema_session(project_id):
    # This query uses project_{project_id} schema
    items = ProjectSpecificModel.query.all()
```

### Shared/Global Models

```python
# For data shared across all projects
class GlobalModel(db.Base, db.AbstractBaseMixin):
    __tablename__ = 'global_data'
    __table_args__ = {'schema': 'carrier'}  # Shared schema

    key = Column(String(128), unique=True)
    value = Column(Text)

# Usage without schema switching
items = GlobalModel.query.all()
```

## UI Integration

### Templates

```html
<!-- plugins/my_plugin/templates/content.html -->
<div class="my-plugin-content">
    <h2>{{ title }}</h2>
    <div id="my-plugin-app">
        <!-- Vue.js app will mount here -->
    </div>
</div>
```

### JavaScript/Vue.js

```javascript
// plugins/my_plugin/static/js/script.js
const MyPluginApp = {
    data() {
        return {
            items: [],
            loading: false
        }
    },
    mounted() {
        this.loadItems()
    },
    methods: {
        async loadItems() {
            this.loading = true
            try {
                const response = await fetch(
                    `/api/v1/my_plugin/${project_id}/items`
                )
                this.items = await response.json()
            } catch (error) {
                console.error('Failed to load items:', error)
            } finally {
                this.loading = false
            }
        },
        async createItem(name, value) {
            const response = await fetch(
                `/api/v1/my_plugin/${project_id}/items`,
                {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, value})
                }
            )
            const item = await response.json()
            this.items.push(item)
        }
    }
}

Vue.createApp(MyPluginApp).mount('#my-plugin-app')
```

### Slots

Slots allow plugins to inject content into UI areas defined by other plugins (usually theme).

```python
# plugins/my_plugin/slots/content.py
from pylon.core.tools import web

@web.slot('my_plugin_slot')
def content(context, slot, payload):
    """
    Render content for slot

    Args:
        context: Pylon context
        slot: Slot name
        payload: Data passed to slot
    """
    project_id = payload.get('project_id')

    # Render template
    return context.module_manager.module.my_plugin.descriptor.render_template(
        'content.html',
        project_id=project_id,
        title='My Plugin'
    )

# Register in module.py
def init(self):
    from .slots import content
    self.descriptor.register_slot(
        'my_plugin_slot',
        content.content,
        'My plugin content slot'
    )
```

## Permissions

### Registering Permissions

```python
def init(self):
    # Register scope (permission category)
    self.descriptor.register_scope(
        'my_plugin',
        'My Plugin Access'
    )
```

### Protecting Endpoints

```python
from tools import auth

@auth.decorators.check_api(["my_plugin"])
def get(self, project_id):
    # Only users with "my_plugin" permission can access
    pass

# Multiple permissions (user needs ANY)
@auth.decorators.check_api(["my_plugin", "admin"])
def post(self, project_id):
    pass
```

### Checking Permissions in Code

```python
from tools import auth

def my_function(project_id):
    if not auth.user_has_permission('my_plugin', project_id):
        raise PermissionError("Access denied")

    # Continue with operation
```

## Background Tasks

### RabbitMQ Tasks

```python
# plugins/my_plugin/module.py
def init(self):
    # Register task consumer
    self.context.rpc_manager.register_function(
        self.process_task,
        name="my_plugin_process_task"
    )

def process_task(self, project_id, task_data):
    """
    Process background task
    """
    log.info(f"Processing task for project {project_id}")

    # Long-running operation
    result = perform_heavy_computation(task_data)

    # Fire completion event
    self.context.event_manager.fire('task_completed', {
        'project_id': project_id,
        'result': result
    })

    return result

# Trigger from API
def post(self, project_id):
    # Queue task for background processing
    task_id = self.module.context.rpc_manager.call.my_plugin_process_task(
        project_id=project_id,
        task_data=request.json
    )
    return {'task_id': task_id, 'status': 'queued'}
```

## Testing Plugins

### Unit Tests

```python
# plugins/my_plugin/tests/test_module.py
import unittest
from unittest.mock import Mock, patch

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.context = Mock()
        self.descriptor = Mock()
        self.module = Module(self.context, self.descriptor)

    def test_init(self):
        """Test plugin initialization"""
        self.module.init()
        # Assert API registered
        self.context.api_manager.add_resource.assert_called()

    def test_rpc_method(self):
        """Test RPC method"""
        from .rpc import methods
        rpc = methods.RPC(self.context, self.descriptor)
        result = rpc.get_data(project_id=1, item_id=123)
        self.assertIsNotNone(result)
```

### Integration Tests

```python
# plugins/my_plugin/tests/test_api.py
import requests

class TestAPI(unittest.TestCase):
    BASE_URL = "http://localhost:8080"
    PROJECT_ID = 1

    def test_create_item(self):
        """Test item creation"""
        response = requests.post(
            f"{self.BASE_URL}/api/v1/my_plugin/{self.PROJECT_ID}/items",
            json={"name": "Test Item", "value": 42}
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], "Test Item")
```

## Best Practices

### DO

1. **Declare all dependencies explicitly** in metadata.json
2. **Use RPC for inter-plugin communication** instead of direct imports
3. **Wrap exceptions** with `@rpc_tools.wrap_exceptions()`
4. **Use schema switching** for multi-tenant data
5. **Register permissions** for all API endpoints
6. **Fire events** for significant state changes
7. **Use type hints** in function signatures
8. **Document RPC methods** with docstrings
9. **Handle errors gracefully** and return meaningful messages
10. **Log important operations** for debugging

### DON'T

1. **Don't import other plugins directly** - use RPC
2. **Don't bypass authentication decorators**
3. **Don't hardcode configuration** - use config.yml
4. **Don't mix tenant and shared data** without schema switching
5. **Don't create circular dependencies**
6. **Don't use global state** - use context
7. **Don't block on long operations** - use background tasks
8. **Don't ignore database transactions**
9. **Don't forget to unregister** in deinit()
10. **Don't skip input validation**

## Plugin Examples

### Minimal Plugin

```python
# my_minimal_plugin/__init__.py
from .module import Module

# my_minimal_plugin/metadata.json
{
  "name": "my_minimal_plugin",
  "version": "1.0.0",
  "depends_on": ["shared"]
}

# my_minimal_plugin/module.py
from pylon.core.tools import module, log

class Module(module.ModuleModel):
    def __init__(self, context, descriptor):
        self.context = context
        self.descriptor = descriptor

    def init(self):
        log.info("My minimal plugin loaded!")

    def deinit(self):
        pass
```

### Complete Plugin

See `pylon/plugins/backend_performance/` or `pylon/plugins/projects/` for full examples.

## Debugging

### Enable Debug Logging

```bash
# .env
CORE_DEBUG_LOGGING=yes
```

### Check Plugin Loading

```bash
docker-compose logs pylon | grep "Loading plugin"
docker-compose logs pylon | grep "my_plugin"
```

### Inspect Context

```python
def init(self):
    # Print available managers
    print("API Manager:", self.context.api_manager)
    print("RPC Manager:", self.context.rpc_manager)
    print("Event Manager:", self.context.event_manager)

    # List loaded plugins
    print("Loaded modules:", self.context.module_manager.modules.keys())
```

### Test RPC Manually

```python
# From pylon container
docker exec -it centry-pylon-1 python

>>> from pylon.core.tools import rpc
>>> result = rpc.call('my_plugin_method', project_id=1, item_id=123)
>>> print(result)
```

## Migration Guide

### Converting Monolithic Code to Plugin

1. **Identify boundaries** - What functionality belongs together?
2. **Extract models** - Move to `models/`
3. **Extract APIs** - Move to `api/v1/`
4. **Extract RPC methods** - Move to `rpc/`
5. **Create metadata.json** - Define dependencies
6. **Create module.py** - Wire everything together
7. **Test in isolation** - Verify plugin loads
8. **Integration test** - Verify with dependencies

## References

- **Plugin Examples**: `pylon/plugins/*/module.py`
- **Shared Library**: `pylon/plugins/shared/tools/`
- **Auth Plugin**: `pylon/plugins/auth/module.py`
- **Projects Plugin**: `pylon/plugins/projects/module.py`
- **Backend Performance**: `pylon/plugins/backend_performance/module.py`

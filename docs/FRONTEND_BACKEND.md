# Frontend & Backend Architecture

## Overview

Carrier uses a split frontend/backend architecture where:
- **Backend**: Python/Flask with plugin-based API and RPC services
- **Frontend**: Server-side rendered templates (Jinja2) with Vue.js for interactivity
- **Communication**: REST APIs and RPC calls via RabbitMQ

## Backend Architecture

### Technology Stack

- **Framework**: Flask
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL with multi-tenant schemas
- **Message Queue**: RabbitMQ (for RPC and events)
- **Cache**: Redis
- **Storage**: MinIO (S3-compatible)
- **Secrets**: HashiCorp Vault
- **Logging**: Loki

### Component Structure

```
Backend Plugin Structure:
plugins/my_plugin/
├── api/                    # REST API endpoints
│   └── v1/
│       └── endpoint.py     # APIModeHandler classes
├── rpc/                    # RPC methods
│   └── methods.py          # @web.rpc decorated functions
├── models/                 # Database models
│   └── model.py            # SQLAlchemy models
├── tools/                  # Business logic
│   └── helpers.py          # Utility functions
├── events/                 # Event handlers
│   └── handlers.py         # Event listeners
└── module.py               # Plugin initialization
```

### REST API Layer

#### APIModeHandler Base Class

All API endpoints inherit from `api_tools.APIModeHandler`:

```python
# plugins/my_plugin/api/v1/endpoint.py
from flask import request
from tools import api_tools, auth, db

class API(api_tools.APIModeHandler):
    """
    REST API endpoint handler
    Maps HTTP methods to handler methods
    """

    @auth.decorators.check_api(["my_plugin"])
    def get(self, project_id: int, item_id: int = None):
        """
        GET /api/v1/my_plugin/<project_id>/items
        GET /api/v1/my_plugin/<project_id>/items/<item_id>
        """
        with db.with_project_schema_session(project_id):
            if item_id:
                item = MyModel.query.get(item_id)
                if not item:
                    return {'error': 'Not found'}, 404
                return item.to_dict()
            else:
                # List all items
                items = MyModel.query.all()
                return [item.to_dict() for item in items]

    @auth.decorators.check_api(["my_plugin"])
    def post(self, project_id: int):
        """
        POST /api/v1/my_plugin/<project_id>/items
        Body: {"name": "Item name", "value": 123}
        """
        data = request.json

        # Validate input
        if not data.get('name'):
            return {'error': 'Name is required'}, 400

        with db.with_project_schema_session(project_id):
            item = MyModel(
                project_id=project_id,
                name=data['name'],
                value=data.get('value', 0)
            )
            db.session.add(item)
            db.session.commit()

            # Fire event
            self.module.context.event_manager.fire('item_created', {
                'project_id': project_id,
                'item_id': item.id
            })

            return item.to_dict(), 201

    @auth.decorators.check_api(["my_plugin"])
    def put(self, project_id: int, item_id: int):
        """
        PUT /api/v1/my_plugin/<project_id>/items/<item_id>
        Body: {"name": "Updated name", "value": 456}
        """
        data = request.json

        with db.with_project_schema_session(project_id):
            item = MyModel.query.get(item_id)
            if not item:
                return {'error': 'Not found'}, 404

            # Update fields
            if 'name' in data:
                item.name = data['name']
            if 'value' in data:
                item.value = data['value']

            db.session.commit()
            return item.to_dict()

    @auth.decorators.check_api(["my_plugin"])
    def delete(self, project_id: int, item_id: int):
        """
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

#### Registering API Endpoints

```python
# plugins/my_plugin/module.py
def init(self):
    from .api.v1 import endpoint

    # Register routes
    self.context.api_manager.add_resource(
        endpoint.API,
        # Route with item_id (for GET/PUT/DELETE)
        "/api/v1/my_plugin/<int:project_id>/items/<int:item_id>",
        # Route without item_id (for GET all/POST)
        "/api/v1/my_plugin/<int:project_id>/items"
    )
```

#### Authentication Decorators

```python
from tools import auth

# Single permission
@auth.decorators.check_api(["my_plugin"])
def get(self, project_id):
    pass

# Multiple permissions (user needs ANY)
@auth.decorators.check_api(["my_plugin", "admin"])
def post(self, project_id):
    pass

# Admin only
@auth.decorators.check_api(["administration"])
def delete(self, project_id):
    pass
```

### RPC Layer

#### RPC Methods

RPC provides synchronous communication between plugins via RabbitMQ.

```python
# plugins/my_plugin/rpc/methods.py
from tools import rpc_tools, db
from pylon.core.tools import web

class RPC:
    def __init__(self, context, descriptor):
        self.context = context
        self.descriptor = descriptor

    @web.rpc("my_plugin_get_item", "get_item")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def get_item(self, project_id, item_id):
        """
        Get item by ID

        Args:
            project_id (int): Project ID
            item_id (int): Item ID

        Returns:
            dict: Item data or None
        """
        with db.with_project_schema_session(project_id):
            item = MyModel.query.get(item_id)
            return item.to_dict() if item else None

    @web.rpc("my_plugin_list_items", "list_items")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def list_items(self, project_id, filters=None):
        """
        List items with optional filters

        Args:
            project_id (int): Project ID
            filters (dict): Optional filters

        Returns:
            list: List of items
        """
        with db.with_project_schema_session(project_id):
            query = MyModel.query
            if filters:
                if 'name' in filters:
                    query = query.filter(MyModel.name.like(f"%{filters['name']}%"))
            items = query.all()
            return [item.to_dict() for item in items]

    @web.rpc("my_plugin_process_item", "process_item")
    @rpc_tools.wrap_exceptions(RuntimeError)
    def process_item(self, project_id, item_id, operation):
        """
        Process item (long-running operation)

        Args:
            project_id (int): Project ID
            item_id (int): Item ID
            operation (str): Operation to perform

        Returns:
            dict: Processing result
        """
        with db.with_project_schema_session(project_id):
            item = MyModel.query.get(item_id)
            if not item:
                raise RuntimeError(f"Item {item_id} not found")

            # Perform operation
            result = self._perform_operation(item, operation)

            # Update item
            item.value = result['value']
            db.session.commit()

            # Fire event
            self.context.event_manager.fire('item_processed', {
                'project_id': project_id,
                'item_id': item_id,
                'operation': operation,
                'result': result
            })

            return result

    def _perform_operation(self, item, operation):
        """Private helper method"""
        # Business logic here
        pass
```

#### Registering RPC Methods

```python
# plugins/my_plugin/module.py
def init(self):
    from .rpc import methods

    rpc = methods.RPC(self.context, self.descriptor)

    # Register all RPC methods
    self.context.rpc_manager.register_function(
        rpc.get_item,
        name="my_plugin_get_item"
    )
    self.context.rpc_manager.register_function(
        rpc.list_items,
        name="my_plugin_list_items"
    )
    self.context.rpc_manager.register_function(
        rpc.process_item,
        name="my_plugin_process_item"
    )
```

#### Calling RPC Methods

```python
# From another plugin
def my_function(self, project_id):
    # Call with timeout
    result = self.context.rpc_manager.timeout(5).my_plugin_get_item(
        project_id=project_id,
        item_id=123
    )

    # Call with longer timeout for heavy operations
    result = self.context.rpc_manager.timeout(30).my_plugin_process_item(
        project_id=project_id,
        item_id=123,
        operation='heavy_computation'
    )

    # Async call (fire and forget)
    self.context.rpc_manager.call.my_plugin_process_item(
        project_id=project_id,
        item_id=123,
        operation='background_task'
    )
```

### Event System

#### Publishing Events

```python
# Fire event after important operation
self.context.event_manager.fire('item_created', {
    'project_id': project_id,
    'item_id': item_id,
    'name': item.name,
    'timestamp': datetime.now().isoformat()
})

# Fire with custom event data
self.context.event_manager.fire('test_completed', {
    'project_id': project_id,
    'test_id': test_id,
    'status': 'passed',
    'duration': 123.45,
    'metrics': {
        'requests': 1000,
        'errors': 5
    }
})
```

#### Subscribing to Events

```python
# plugins/my_plugin/events/handlers.py
from pylon.core.tools import log

def on_item_created(event_data):
    """
    Handle item_created event

    Args:
        event_data (dict): Event payload
    """
    project_id = event_data['project_id']
    item_id = event_data['item_id']

    log.info(f"Item {item_id} created in project {project_id}")

    # React to event
    update_statistics(project_id)
    send_notification(event_data)

def on_test_completed(event_data):
    """Handle test_completed event"""
    if event_data['status'] == 'passed':
        log.info(f"Test {event_data['test_id']} passed")
    else:
        log.error(f"Test {event_data['test_id']} failed")

# plugins/my_plugin/module.py
def init(self):
    from .events import handlers

    # Register event listeners
    self.context.event_manager.register_listener(
        'item_created',
        handlers.on_item_created
    )
    self.context.event_manager.register_listener(
        'test_completed',
        handlers.on_test_completed
    )
```

### Database Models

#### Model Definition

```python
# plugins/my_plugin/models/item.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from tools import db

class MyModel(db.Base, db.AbstractBaseMixin):
    """
    Item model

    AbstractBaseMixin provides:
    - id (primary key)
    - created_at (DateTime)
    - updated_at (DateTime)
    """
    __tablename__ = 'my_plugin_items'
    __table_args__ = {'extend_existing': True}

    # Fields
    project_id = Column(Integer, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    value = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)

    # Relationships (if needed)
    # parent_id = Column(Integer, ForeignKey('my_plugin_parents.id'))
    # parent = relationship('ParentModel', back_populates='items')

    def to_dict(self):
        """
        Convert to dictionary

        Returns:
            dict: Model data
        """
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'value': self.value,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create from dictionary

        Args:
            data (dict): Model data

        Returns:
            MyModel: New instance
        """
        return cls(
            project_id=data['project_id'],
            name=data['name'],
            description=data.get('description'),
            value=data.get('value', 0),
            enabled=data.get('enabled', True)
        )
```

#### Multi-Tenant Schema Switching

```python
# For project-specific data
with db.with_project_schema_session(project_id):
    # All queries use project_{project_id} schema
    items = MyModel.query.filter_by(enabled=True).all()
    item = MyModel.query.get(item_id)
    db.session.add(new_item)
    db.session.commit()

# For shared/global data (use explicit schema)
from plugins.admin.models.project import Project  # Uses carrier schema
projects = Project.query.all()
```

## Frontend Architecture

### Technology Stack

- **Templates**: Jinja2
- **JavaScript Framework**: Vue.js 3
- **HTTP Client**: Fetch API
- **Styling**: CSS/SCSS

### Component Structure

```
Frontend Plugin Structure:
plugins/my_plugin/
├── templates/              # Jinja2 templates
│   ├── content.html        # Main content
│   ├── scripts.html        # JavaScript includes
│   └── styles.html         # CSS includes
├── static/
│   ├── js/
│   │   ├── app.js          # Vue.js app
│   │   └── components.js   # Vue components
│   └── css/
│       └── styles.css      # Stylesheets
└── slots/                  # UI slot handlers
    └── content.py          # Slot rendering
```

### Templates (Jinja2)

#### Main Content Template

```html
<!-- plugins/my_plugin/templates/content.html -->
<div class="my-plugin-container">
    <div class="row">
        <div class="col-12">
            <h2>{{ plugin_title }}</h2>
            <p>{{ plugin_description }}</p>
        </div>
    </div>

    <!-- Vue.js App -->
    <div id="my-plugin-app" class="mt-4">
        <!-- Loading state -->
        <div v-if="loading" class="text-center">
            <div class="spinner-border" role="status">
                <span class="sr-only">Loading...</span>
            </div>
        </div>

        <!-- Error state -->
        <div v-if="error" class="alert alert-danger">
            {{ error }}
        </div>

        <!-- Content -->
        <div v-if="!loading && !error">
            <!-- Item list -->
            <div class="card">
                <div class="card-header d-flex justify-content-between">
                    <span>Items</span>
                    <button @click="showCreateModal" class="btn btn-sm btn-primary">
                        Create Item
                    </button>
                </div>
                <div class="card-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Value</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="item in items" :key="item.id">
                                <td>{{ item.id }}</td>
                                <td>{{ item.name }}</td>
                                <td>{{ item.value }}</td>
                                <td>{{ formatDate(item.created_at) }}</td>
                                <td>
                                    <button @click="editItem(item)" class="btn btn-sm btn-info">
                                        Edit
                                    </button>
                                    <button @click="deleteItem(item)" class="btn btn-sm btn-danger">
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Create/Edit Modal -->
            <div v-if="showModal" class="modal d-block" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                {{ editingItem ? 'Edit Item' : 'Create Item' }}
                            </h5>
                            <button @click="closeModal" class="btn-close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">Name</label>
                                <input v-model="formData.name" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Description</label>
                                <textarea v-model="formData.description" class="form-control"></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Value</label>
                                <input v-model.number="formData.value" type="number" class="form-control">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button @click="closeModal" class="btn btn-secondary">
                                Cancel
                            </button>
                            <button @click="saveItem" class="btn btn-primary">
                                Save
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Include styles -->
{% include 'my_plugin/styles.html' %}

<!-- Include scripts -->
{% include 'my_plugin/scripts.html' %}
```

#### Scripts Template

```html
<!-- plugins/my_plugin/templates/scripts.html -->
<script src="{{ url_for('my_plugin.static', filename='js/app.js') }}"></script>
```

#### Styles Template

```html
<!-- plugins/my_plugin/templates/styles.html -->
<link rel="stylesheet" href="{{ url_for('my_plugin.static', filename='css/styles.css') }}">
```

### Vue.js Application

```javascript
// plugins/my_plugin/static/js/app.js

const MyPluginApp = {
    data() {
        return {
            // State
            items: [],
            loading: false,
            error: null,

            // Modal state
            showModal: false,
            editingItem: null,
            formData: {
                name: '',
                description: '',
                value: 0
            }
        }
    },

    computed: {
        apiBaseUrl() {
            // Get from window or template variable
            return `/api/v1/my_plugin/${window.project_id}`
        }
    },

    mounted() {
        // Load data on mount
        this.loadItems()
    },

    methods: {
        async loadItems() {
            this.loading = true
            this.error = null

            try {
                const response = await fetch(`${this.apiBaseUrl}/items`)
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`)
                }
                this.items = await response.json()
            } catch (error) {
                console.error('Failed to load items:', error)
                this.error = 'Failed to load items. Please try again.'
            } finally {
                this.loading = false
            }
        },

        async createItem(data) {
            try {
                const response = await fetch(`${this.apiBaseUrl}/items`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })

                if (!response.ok) {
                    const error = await response.json()
                    throw new Error(error.error || 'Failed to create item')
                }

                const item = await response.json()
                this.items.push(item)
                return item
            } catch (error) {
                console.error('Failed to create item:', error)
                throw error
            }
        },

        async updateItem(itemId, data) {
            try {
                const response = await fetch(`${this.apiBaseUrl}/items/${itemId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })

                if (!response.ok) {
                    throw new Error('Failed to update item')
                }

                const updatedItem = await response.json()

                // Update in list
                const index = this.items.findIndex(item => item.id === itemId)
                if (index !== -1) {
                    this.items[index] = updatedItem
                }

                return updatedItem
            } catch (error) {
                console.error('Failed to update item:', error)
                throw error
            }
        },

        async deleteItem(item) {
            if (!confirm(`Delete item "${item.name}"?`)) {
                return
            }

            try {
                const response = await fetch(`${this.apiBaseUrl}/items/${item.id}`, {
                    method: 'DELETE'
                })

                if (!response.ok) {
                    throw new Error('Failed to delete item')
                }

                // Remove from list
                this.items = this.items.filter(i => i.id !== item.id)
            } catch (error) {
                console.error('Failed to delete item:', error)
                alert('Failed to delete item. Please try again.')
            }
        },

        showCreateModal() {
            this.editingItem = null
            this.formData = {
                name: '',
                description: '',
                value: 0
            }
            this.showModal = true
        },

        editItem(item) {
            this.editingItem = item
            this.formData = {
                name: item.name,
                description: item.description,
                value: item.value
            }
            this.showModal = true
        },

        async saveItem() {
            try {
                if (this.editingItem) {
                    // Update existing
                    await this.updateItem(this.editingItem.id, this.formData)
                } else {
                    // Create new
                    await this.createItem(this.formData)
                }
                this.closeModal()
            } catch (error) {
                alert('Failed to save item: ' + error.message)
            }
        },

        closeModal() {
            this.showModal = false
            this.editingItem = null
            this.formData = {
                name: '',
                description: '',
                value: 0
            }
        },

        formatDate(dateString) {
            if (!dateString) return ''
            const date = new Date(dateString)
            return date.toLocaleString()
        }
    }
}

// Mount app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    Vue.createApp(MyPluginApp).mount('#my-plugin-app')
})
```

### UI Slots

Slots allow plugins to inject content into areas defined by theme plugin.

```python
# plugins/my_plugin/slots/content.py
from pylon.core.tools import web, log

@web.slot('my_plugin_main_content')
def main_content(context, slot, payload):
    """
    Render main content slot

    Args:
        context: Pylon context
        slot (str): Slot name
        payload (dict): Data passed to slot

    Returns:
        str: Rendered HTML
    """
    project_id = payload.get('project_id')

    # Get data via RPC
    try:
        items = context.rpc_manager.timeout(5).my_plugin_list_items(
            project_id=project_id
        )
    except Exception as e:
        log.error(f"Failed to load items: {e}")
        items = []

    # Render template
    return context.module_manager.module.my_plugin.descriptor.render_template(
        'content.html',
        project_id=project_id,
        plugin_title='My Plugin',
        plugin_description='Manage items in your project',
        initial_items=items  # Pass to template for SSR
    )

# Register in module.py
def init(self):
    from .slots import content

    self.descriptor.register_slot(
        'my_plugin_main_content',
        content.main_content,
        'Main content area for my plugin'
    )
```

## Communication Patterns

### Backend to Backend (RPC)

```python
# Plugin A calls Plugin B via RPC
result = self.context.rpc_manager.timeout(5).plugin_b_method(
    project_id=project_id,
    param1=value1,
    param2=value2
)
```

### Frontend to Backend (REST)

```javascript
// Frontend calls backend via REST API
const response = await fetch('/api/v1/my_plugin/1/items', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: 'Item', value: 123})
})
const result = await response.json()
```

### Backend to Frontend (Events)

```python
# Backend fires event
self.context.event_manager.fire('item_updated', {
    'item_id': item_id,
    'changes': changes
})

# Frontend listens via WebSocket or polling
# (implementation depends on Loki integration)
```

### Frontend to Frontend (Vue Events)

```javascript
// Parent component
<ChildComponent @item-selected="handleItemSelected" />

// Child component emits event
this.$emit('item-selected', item)
```

## Best Practices

### Backend

1. **Always use schema switching** for tenant data
2. **Wrap RPC methods** with `@rpc_tools.wrap_exceptions()`
3. **Validate input** before processing
4. **Use transactions** for multi-step operations
5. **Fire events** for state changes
6. **Log errors** with context
7. **Handle timeouts** in RPC calls
8. **Use connection pooling** for DB
9. **Cache expensive queries** in Redis
10. **Document RPC methods** with docstrings

### Frontend

1. **Show loading states** during async operations
2. **Handle errors gracefully** with user feedback
3. **Validate forms** before submission
4. **Use computed properties** for derived data
5. **Debounce expensive operations** (search, etc.)
6. **Clean up resources** in unmount hooks
7. **Use async/await** instead of promises
8. **Provide user feedback** (success/error messages)
9. **Make UI responsive** to different screen sizes
10. **Test with real data** and edge cases

### Security

1. **Never bypass auth decorators** on APIs
2. **Validate all user input** on backend
3. **Sanitize output** to prevent XSS
4. **Use CSRF tokens** for forms
5. **Don't expose sensitive data** in responses
6. **Log security events** in audit_logs
7. **Rate limit APIs** to prevent abuse
8. **Use HTTPS** in production
9. **Don't trust client-side validation** alone
10. **Follow principle of least privilege** for permissions

## Debugging

### Backend Debugging

```bash
# View backend logs
docker-compose logs -f pylon

# Enable debug mode
CORE_DEBUG_LOGGING=yes

# Access pylon shell
docker exec -it centry-pylon-1 python
>>> from tools import db, rpc_tools
>>> result = rpc_tools.RpcManager().my_plugin_get_item(project_id=1, item_id=123)

# Database queries
docker exec -it centry-postgres-1 psql -U carrier -d carrier
\dt project_1.*  -- List project 1 tables
SELECT * FROM project_1.my_plugin_items;
```

### Frontend Debugging

```javascript
// Browser console
console.log('Items:', app.items)

// Vue DevTools
// Install browser extension for Vue.js debugging

// Network tab
// Inspect API calls and responses

// Check for errors
window.addEventListener('error', (e) => {
    console.error('Global error:', e)
})
```

## Performance Optimization

### Backend

1. **Use database indexes** on frequently queried columns
2. **Implement pagination** for large result sets
3. **Cache expensive queries** in Redis
4. **Use connection pooling** for database
5. **Batch database operations** when possible
6. **Profile slow queries** with PostgreSQL EXPLAIN
7. **Use async tasks** for heavy computation
8. **Optimize RPC timeouts** based on operation
9. **Compress large responses** (gzip)
10. **Use database views** for complex queries

### Frontend

1. **Lazy load components** not needed initially
2. **Implement virtual scrolling** for long lists
3. **Debounce user input** (search, filters)
4. **Use pagination** instead of loading all data
5. **Minimize DOM updates** with Vue's reactivity
6. **Optimize images** (compression, format)
7. **Bundle and minify JavaScript** in production
8. **Use CDN** for static assets
9. **Implement caching** (localStorage, sessionStorage)
10. **Profile with browser DevTools** Performance tab

## References

- **API Examples**: `pylon/plugins/*/api/v1/`
- **RPC Examples**: `pylon/plugins/*/rpc/`
- **Model Examples**: `pylon/plugins/*/models/`
- **Template Examples**: `pylon/plugins/*/templates/`
- **Vue.js Examples**: `pylon/plugins/*/static/js/`
- **Shared Tools**: `pylon/plugins/shared/tools/`

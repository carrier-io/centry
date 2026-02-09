# Carrier Platform - Development Guide

## Overview

This guide provides instructions for developing features, fixing bugs, and extending the Carrier platform. It covers common development workflows, debugging techniques, and best practices.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Common Development Tasks](#common-development-tasks)
- [Bug Fixing Workflow](#bug-fixing-workflow)
- [Adding New Features](#adding-new-features)
- [Testing](#testing)
- [Debugging](#debugging)
- [Performance Optimization](#performance-optimization)
- [Security Considerations](#security-considerations)
- [Code Review Checklist](#code-review-checklist)

---

## Development Environment Setup

### Prerequisites

- Docker and Docker Compose
- Git
- Text editor or IDE (VSCode recommended)
- Network interface name (for deployment)

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd centry

# Review configuration
cp config/pylon-example.yml config/pylon.yml
cp config/pylon_auth-example.yml config/pylon_auth.yml

# Edit .env file with your settings
vim .env

# Deploy services
make up INTERFACE=eth0  # or your network interface

# Verify services are running
docker-compose ps
```

### Access Points

- **Main App**: http://<APP_IP>
- **RabbitMQ**: http://<APP_IP>:15672 (user/password from .env)
- **MinIO**: http://<APP_IP>:9000 (admin/password from .env)
- **PostgreSQL**: Port 5432 (carrier/password from .env)

### Development Tools

```bash
# View logs
docker-compose logs -f pylon
docker-compose logs -f pylon_auth

# Access shell in pylon container
docker exec -it centry-pylon-1 bash

# Access PostgreSQL
docker exec -it centry-postgres-1 psql -U carrier -d carrier

# Restart services after changes
docker-compose restart pylon
docker-compose restart pylon_auth
```

---

## Common Development Tasks

### Task 1: Modifying an Existing Plugin

**Scenario**: Update the `backend_performance` plugin to add a new field.

**Steps**:

1. **Locate the plugin**:
   ```bash
   cd pylon/plugins/backend_performance
   ```

2. **Update the model** (if adding database field):
   ```python
   # models/test.py
   class BackendPerformanceTest(db.Base, db.AbstractBaseMixin):
       __tablename__ = 'backend_performance_tests'
       # ... existing fields ...

       # Add new field
       new_field = Column(String(256), default='')
   ```

3. **Update the API** (if exposing via REST):
   ```python
   # api/v1/test.py
   @auth.decorators.check_api(["backend_performance"])
   def post(self, project_id: int):
       data = request.json
       # Handle new field
       new_field_value = data.get('new_field', '')
       # ... rest of logic
   ```

4. **Update the frontend** (if UI changes needed):
   ```javascript
   // static/js/app.js
   // Add new field to form
   formData: {
       // ... existing fields ...
       new_field: ''
   }
   ```

5. **Test changes**:
   ```bash
   # Restart pylon
   docker-compose restart pylon

   # Check logs for errors
   docker-compose logs -f pylon

   # Test via API
   curl -X POST http://<APP_IP>/api/v1/backend_performance/1/tests \
     -H "Content-Type: application/json" \
     -d '{"name": "Test", "new_field": "value"}'
   ```

6. **Create database migration** (if model changed):
   ```bash
   # Access pylon container
   docker exec -it centry-pylon-1 bash

   # Generate migration (if using alembic)
   # This is plugin-specific, check if plugin uses migrations
   ```

---

### Task 2: Adding a New API Endpoint

**Scenario**: Add a new endpoint to get test statistics.

**Steps**:

1. **Create new API file** (or add to existing):
   ```python
   # pylon/plugins/backend_performance/api/v1/statistics.py
   from flask import request
   from tools import api_tools, auth, db

   class StatisticsAPI(api_tools.APIModeHandler):
       @auth.decorators.check_api(["backend_performance"])
       def get(self, project_id: int):
           """
           Get test statistics

           GET /api/v1/backend_performance/<project_id>/statistics
           """
           with db.with_project_schema_session(project_id):
               total_tests = BackendPerformanceTest.query.count()
               active_tests = BackendPerformanceTest.query.filter_by(
                   enabled=True
               ).count()

               return {
                   'total_tests': total_tests,
                   'active_tests': active_tests,
                   'inactive_tests': total_tests - active_tests
               }
   ```

2. **Register the endpoint** in module.py:
   ```python
   # pylon/plugins/backend_performance/module.py
   def init(self):
       # ... existing registrations ...

       from .api.v1 import statistics
       self.context.api_manager.add_resource(
           statistics.StatisticsAPI,
           "/api/v1/backend_performance/<int:project_id>/statistics"
       )
   ```

3. **Test the endpoint**:
   ```bash
   docker-compose restart pylon
   curl http://<APP_IP>/api/v1/backend_performance/1/statistics
   ```

---

### Task 3: Adding a New RPC Method

**Scenario**: Add RPC method to duplicate a test.

**Steps**:

1. **Create or update RPC file**:
   ```python
   # pylon/plugins/backend_performance/rpc/test.py
   from tools import rpc_tools, db
   from pylon.core.tools import web

   class RPC:
       def __init__(self, context, descriptor):
           self.context = context
           self.descriptor = descriptor

       @web.rpc("backend_performance_duplicate_test", "duplicate_test")
       @rpc_tools.wrap_exceptions(RuntimeError)
       def duplicate_test(self, project_id, test_id):
           """
           Duplicate a test

           Args:
               project_id (int): Project ID
               test_id (int): Test ID to duplicate

           Returns:
               dict: New test data
           """
           with db.with_project_schema_session(project_id):
               # Get original test
               original = BackendPerformanceTest.query.get(test_id)
               if not original:
                   raise RuntimeError(f"Test {test_id} not found")

               # Create duplicate
               duplicate = BackendPerformanceTest(
                   project_id=project_id,
                   name=f"{original.name} (Copy)",
                   description=original.description,
                   # ... copy other fields ...
               )

               db.session.add(duplicate)
               db.session.commit()

               return duplicate.to_dict()
   ```

2. **Register the RPC** in module.py:
   ```python
   def init(self):
       from .rpc import test
       rpc = test.RPC(self.context, self.descriptor)

       self.context.rpc_manager.register_function(
           rpc.duplicate_test,
           name="backend_performance_duplicate_test"
       )
   ```

3. **Call from another plugin**:
   ```python
   # From another plugin
   result = self.context.rpc_manager.timeout(5).backend_performance_duplicate_test(
       project_id=1,
       test_id=123
   )
   ```

---

### Task 4: Adding a Database Model

**Scenario**: Create a new model for test templates.

**Steps**:

1. **Create model file**:
   ```python
   # pylon/plugins/backend_performance/models/template.py
   from sqlalchemy import Column, Integer, String, Text, Boolean
   from tools import db

   class TestTemplate(db.Base, db.AbstractBaseMixin):
       """
       Test template model
       """
       __tablename__ = 'backend_performance_test_templates'
       __table_args__ = {'extend_existing': True}

       project_id = Column(Integer, nullable=False, index=True)
       name = Column(String(128), nullable=False)
       description = Column(Text)
       config = Column(Text)  # JSON config
       is_public = Column(Boolean, default=False)

       def to_dict(self):
           return {
               'id': self.id,
               'project_id': self.project_id,
               'name': self.name,
               'description': self.description,
               'config': self.config,
               'is_public': self.is_public,
               'created_at': self.created_at.isoformat() if self.created_at else None
           }
   ```

2. **Initialize model** in module.py:
   ```python
   def init(self):
       # Import to register with SQLAlchemy
       from .models import template
   ```

3. **Create tables** (on first run, tables auto-create):
   ```bash
   docker-compose restart pylon
   # Tables will be created in project schemas automatically
   ```

4. **Verify table creation**:
   ```bash
   docker exec -it centry-postgres-1 psql -U carrier -d carrier
   \dt project_1.*template*
   ```

---

### Task 5: Adding a UI Component

**Scenario**: Add a statistics widget to the dashboard.

**Steps**:

1. **Create template**:
   ```html
   <!-- pylon/plugins/backend_performance/templates/widgets/statistics.html -->
   <div class="statistics-widget card">
       <div class="card-header">Test Statistics</div>
       <div class="card-body">
           <div id="stats-app">
               <div v-if="loading">Loading...</div>
               <div v-else>
                   <p>Total Tests: {{ stats.total_tests }}</p>
                   <p>Active Tests: {{ stats.active_tests }}</p>
                   <p>Success Rate: {{ stats.success_rate }}%</p>
               </div>
           </div>
       </div>
   </div>

   <script>
   const StatsApp = {
       data() {
           return {
               stats: {},
               loading: true
           }
       },
       mounted() {
           this.loadStats()
       },
       methods: {
           async loadStats() {
               const response = await fetch('/api/v1/backend_performance/{{ project_id }}/statistics')
               this.stats = await response.json()
               this.loading = false
           }
       }
   }
   Vue.createApp(StatsApp).mount('#stats-app')
   </script>
   ```

2. **Register slot**:
   ```python
   # pylon/plugins/backend_performance/slots/dashboard.py
   from pylon.core.tools import web

   @web.slot('project_dashboard_widgets')
   def statistics_widget(context, slot, payload):
       project_id = payload.get('project_id')

       return context.module_manager.module.backend_performance.descriptor.render_template(
           'widgets/statistics.html',
           project_id=project_id
       )
   ```

3. **Register in module.py**:
   ```python
   def init(self):
       from .slots import dashboard

       self.descriptor.register_slot(
           'project_dashboard_widgets',
           dashboard.statistics_widget,
           'Backend performance statistics widget'
       )
   ```

---

## Bug Fixing Workflow

### Step 1: Reproduce the Bug

1. **Gather information**:
   - What is the expected behavior?
   - What is the actual behavior?
   - Steps to reproduce
   - Error messages or stack traces

2. **Reproduce locally**:
   ```bash
   # Enable debug logging
   # Edit .env
   CORE_DEBUG_LOGGING=yes

   docker-compose restart pylon
   docker-compose logs -f pylon

   # Reproduce the bug and observe logs
   ```

### Step 2: Locate the Issue

1. **Check logs**:
   ```bash
   docker-compose logs pylon | grep ERROR
   docker-compose logs pylon | grep -A 10 "Traceback"
   ```

2. **Check the relevant plugin**:
   ```bash
   # If bug is in backend_performance
   cd pylon/plugins/backend_performance

   # Search for relevant code
   grep -r "error_keyword" .
   ```

3. **Use RPC/API directly**:
   ```bash
   # Test RPC directly
   docker exec -it centry-pylon-1 python
   >>> from tools import rpc_tools
   >>> result = rpc_tools.RpcManager().backend_performance_get_test(
   ...     project_id=1, test_id=123
   ... )
   ```

### Step 3: Fix the Bug

1. **Make the fix**:
   ```python
   # Example: Fix null pointer error
   # Before:
   test_name = test.name.upper()  # Fails if test is None

   # After:
   test_name = test.name.upper() if test else "Unknown"
   ```

2. **Add error handling**:
   ```python
   # Add proper exception handling
   try:
       result = risky_operation()
   except SpecificException as e:
       log.error(f"Operation failed: {e}")
       return {'error': str(e)}, 400
   ```

### Step 4: Test the Fix

1. **Unit test** (if applicable):
   ```python
   # pylon/plugins/backend_performance/tests/test_bug_fix.py
   def test_null_test_name():
       result = handle_test(None)
       assert result == "Unknown"
   ```

2. **Integration test**:
   ```bash
   # Restart and test
   docker-compose restart pylon

   # Reproduce the original bug scenario
   # Verify it's fixed
   ```

3. **Check for regressions**:
   - Test related functionality
   - Check logs for new errors

### Step 5: Document the Fix

1. **Add comments** to code if logic is complex
2. **Update documentation** if user-facing behavior changed
3. **Create changelog entry** if applicable

---

## Adding New Features

### Feature Development Process

#### Phase 1: Planning

1. **Define requirements**:
   - What problem does this solve?
   - Who are the users?
   - What are the acceptance criteria?

2. **Design the solution**:
   - Database changes needed?
   - New APIs needed?
   - UI changes needed?
   - Dependencies on other plugins?

3. **Create technical spec**:
   - Database schema
   - API endpoints
   - RPC methods
   - UI mockups

#### Phase 2: Implementation

1. **Create feature branch**:
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Implement backend**:
   - Database models
   - API endpoints
   - RPC methods
   - Business logic

3. **Implement frontend**:
   - Templates
   - Vue.js components
   - Styling

4. **Add tests**:
   - Unit tests
   - Integration tests
   - UI tests (if applicable)

#### Phase 3: Testing

1. **Local testing**:
   ```bash
   docker-compose restart pylon
   # Test all functionality
   ```

2. **Edge case testing**:
   - Empty data
   - Large datasets
   - Concurrent requests
   - Invalid input

3. **Performance testing**:
   - Check query performance
   - Check API response times
   - Check memory usage

#### Phase 4: Documentation

1. **Code documentation**:
   - Docstrings for functions
   - Comments for complex logic

2. **User documentation**:
   - Update relevant .md files
   - Add examples

3. **API documentation**:
   - Document endpoints
   - Document parameters
   - Document responses

#### Phase 5: Code Review & Merge

1. **Self-review checklist**:
   - [ ] Code follows project style
   - [ ] No hardcoded values
   - [ ] Error handling in place
   - [ ] Permissions checked
   - [ ] Database transactions used
   - [ ] Tests pass
   - [ ] Documentation updated

2. **Create pull request**
3. **Address review comments**
4. **Merge to main branch**

---

## Testing

### Manual Testing

#### API Testing with curl

```bash
# GET request
curl http://<APP_IP>/api/v1/backend_performance/1/tests

# POST request
curl -X POST http://<APP_IP>/api/v1/backend_performance/1/tests \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "type": "load"}'

# PUT request
curl -X PUT http://<APP_IP>/api/v1/backend_performance/1/tests/123 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Test"}'

# DELETE request
curl -X DELETE http://<APP_IP>/api/v1/backend_performance/1/tests/123
```

#### RPC Testing

```python
# Access pylon container
docker exec -it centry-pylon-1 python

>>> from pylon.core.tools import rpc
>>>
>>> # Call RPC method
>>> result = rpc.call(
...     'backend_performance_get_test',
...     project_id=1,
...     test_id=123
... )
>>> print(result)
```

#### Database Testing

```bash
# Access PostgreSQL
docker exec -it centry-postgres-1 psql -U carrier -d carrier

-- Check shared tables
SELECT * FROM carrier.projects;

-- Check project-specific tables
SET search_path TO project_1;
SELECT * FROM backend_performance_tests;

-- Check schema exists
SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'project_%';
```

### Automated Testing

#### Unit Tests

```python
# pylon/plugins/my_plugin/tests/test_module.py
import unittest
from unittest.mock import Mock, patch

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.context = Mock()
        self.descriptor = Mock()

    def test_something(self):
        # Test logic
        result = my_function()
        self.assertEqual(result, expected_value)

if __name__ == '__main__':
    unittest.main()
```

#### Running Tests

```bash
# Run plugin tests
docker exec -it centry-pylon-1 bash
cd /data/pylon/plugins/my_plugin
python -m pytest tests/
```

---

## Debugging

### Log Levels

```python
from pylon.core.tools import log

log.debug("Debug message")
log.info("Info message")
log.warning("Warning message")
log.error("Error message")
log.critical("Critical message")
```

### Debug Mode

```bash
# Enable debug logging
# Edit .env
CORE_DEBUG_LOGGING=yes

# Enable development mode
CORE_DEVELOPMENT_MODE=true

# Restart
docker-compose restart pylon
```

### Common Debugging Scenarios

#### Scenario 1: Plugin Not Loading

**Symptoms**: Plugin not available, APIs return 404

**Debug Steps**:
1. Check logs for plugin loading:
   ```bash
   docker-compose logs pylon | grep "Loading plugin"
   docker-compose logs pylon | grep "my_plugin"
   ```

2. Check metadata.json syntax:
   ```bash
   cat pylon/plugins/my_plugin/metadata.json | jq .
   ```

3. Check dependencies are met:
   ```bash
   docker-compose logs pylon | grep "dependency"
   ```

4. Check module.py has no syntax errors:
   ```bash
   docker exec -it centry-pylon-1 python -m py_compile /data/pylon/plugins/my_plugin/module.py
   ```

#### Scenario 2: Database Query Failing

**Symptoms**: 500 error, database errors in logs

**Debug Steps**:
1. Check if schema switching is used:
   ```python
   # Should be wrapped
   with db.with_project_schema_session(project_id):
       items = MyModel.query.all()
   ```

2. Check if table exists:
   ```bash
   docker exec -it centry-postgres-1 psql -U carrier -d carrier -c "\dt project_1.*"
   ```

3. Check query in PostgreSQL directly:
   ```sql
   SET search_path TO project_1;
   SELECT * FROM my_table;
   ```

4. Enable SQL logging:
   ```python
   # In module.py
   import logging
   logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
   ```

#### Scenario 3: RPC Timeout

**Symptoms**: RPC call hangs or times out

**Debug Steps**:
1. Check RabbitMQ is running:
   ```bash
   docker-compose ps rabbitmq
   ```

2. Check RabbitMQ queues:
   - Access: http://<APP_IP>:15672
   - Check "Queues" tab for messages

3. Check RPC is registered:
   ```bash
   docker-compose logs pylon | grep "register_function"
   ```

4. Increase timeout:
   ```python
   result = self.context.rpc_manager.timeout(30).my_rpc_method()
   ```

#### Scenario 4: Permission Denied

**Symptoms**: 403 Forbidden, "Permission denied" in logs

**Debug Steps**:
1. Check permission is registered:
   ```python
   # In module.py init()
   self.descriptor.register_scope('my_plugin', 'My Plugin Access')
   ```

2. Check user has permission:
   - Access Keycloak admin: http://<APP_IP>:8080
   - Check user's groups and permissions

3. Check decorator is present:
   ```python
   @auth.decorators.check_api(["my_plugin"])
   def get(self, project_id):
       pass
   ```

---

## Performance Optimization

### Database Optimization

1. **Add indexes** on frequently queried columns:
   ```python
   class MyModel(db.Base):
       name = Column(String(128), index=True)  # Add index
       project_id = Column(Integer, index=True)
   ```

2. **Use joins** instead of multiple queries:
   ```python
   # Bad: N+1 queries
   for item in items:
       user = User.query.get(item.user_id)

   # Good: Single query with join
   items = Item.query.join(User).all()
   ```

3. **Implement pagination**:
   ```python
   page = request.args.get('page', 1, type=int)
   per_page = 20

   items = MyModel.query.paginate(page=page, per_page=per_page)

   return {
       'items': [item.to_dict() for item in items.items],
       'total': items.total,
       'page': page,
       'pages': items.pages
   }
   ```

4. **Use query filters** efficiently:
   ```python
   # Filter in database, not in Python
   # Bad:
   all_items = MyModel.query.all()
   active_items = [item for item in all_items if item.enabled]

   # Good:
   active_items = MyModel.query.filter_by(enabled=True).all()
   ```

### API Optimization

1. **Cache expensive responses**:
   ```python
   import redis
   cache = redis.Redis(host='redis', password='password')

   def get(self, project_id):
       cache_key = f"stats:{project_id}"
       cached = cache.get(cache_key)

       if cached:
           return json.loads(cached)

       # Compute expensive result
       result = compute_statistics(project_id)

       # Cache for 5 minutes
       cache.setex(cache_key, 300, json.dumps(result))
       return result
   ```

2. **Use async for I/O operations**:
   ```python
   # For long-running operations, use background tasks
   self.context.rpc_manager.call.my_long_operation(project_id=project_id)
   return {'status': 'queued'}
   ```

3. **Return only needed data**:
   ```python
   # Bad: Return all fields
   return item.to_dict()

   # Good: Return only what frontend needs
   return {
       'id': item.id,
       'name': item.name,
       'status': item.status
   }
   ```

### Frontend Optimization

1. **Lazy load data**:
   ```javascript
   // Load only visible data initially
   mounted() {
       this.loadSummary()  // Fast
   },
   methods: {
       async loadDetails() {
           // Load on demand
       }
   }
   ```

2. **Debounce user input**:
   ```javascript
   data() {
       return {
           searchQuery: '',
           searchDebounce: null
       }
   },
   watch: {
       searchQuery(value) {
           clearTimeout(this.searchDebounce)
           this.searchDebounce = setTimeout(() => {
               this.performSearch(value)
           }, 300)
       }
   }
   ```

3. **Use pagination**:
   ```javascript
   methods: {
       async loadPage(page) {
           const response = await fetch(`/api/v1/items?page=${page}`)
           const data = await response.json()
           this.items = data.items
           this.totalPages = data.pages
       }
   }
   ```

---

## Security Considerations

### Input Validation

```python
from flask import request

def post(self, project_id):
    data = request.json

    # Validate required fields
    if not data.get('name'):
        return {'error': 'Name is required'}, 400

    # Validate types
    if not isinstance(data.get('value'), int):
        return {'error': 'Value must be integer'}, 400

    # Validate ranges
    if data.get('value', 0) < 0:
        return {'error': 'Value must be positive'}, 400

    # Sanitize strings
    name = str(data['name']).strip()[:128]

    # Proceed with validated data
```

### SQL Injection Prevention

```python
# SQLAlchemy ORM is safe by default
# Don't use raw SQL unless necessary

# Bad:
query = f"SELECT * FROM items WHERE name = '{user_input}'"
db.session.execute(query)

# Good:
items = MyModel.query.filter_by(name=user_input).all()

# If raw SQL needed, use parameterized queries:
from sqlalchemy import text
query = text("SELECT * FROM items WHERE name = :name")
result = db.session.execute(query, {"name": user_input})
```

### XSS Prevention

```html
<!-- Jinja2 auto-escapes by default -->
<!-- Safe: -->
<p>{{ user_input }}</p>

<!-- Dangerous (only if you trust the source): -->
<p>{{ user_input | safe }}</p>

<!-- Vue.js also auto-escapes -->
<!-- Safe: -->
<p>{{ userData }}</p>

<!-- Dangerous: -->
<p v-html="userData"></p>
```

### Permission Checks

```python
# Always check permissions on APIs
@auth.decorators.check_api(["my_plugin"])
def get(self, project_id):
    pass

# Check in code too for complex logic
if not auth.user_has_permission('admin', project_id):
    log.warning(f"Unauthorized access attempt by user {user_id}")
    return {'error': 'Forbidden'}, 403
```

### Secrets Management

```python
# Never hardcode secrets
# Bad:
API_KEY = "sk_live_123456"

# Good: Use Vault
from tools.VaultClient import VaultClient
vault = VaultClient()
api_key = vault.get_secret(project_id, 'api_key')

# Or use environment variables
import os
api_key = os.environ.get('API_KEY')
```

---

## Code Review Checklist

### General

- [ ] Code follows Python PEP 8 style guide
- [ ] No commented-out code
- [ ] No debug print statements
- [ ] Proper error handling
- [ ] Logging at appropriate levels
- [ ] Documentation/comments for complex logic

### Backend

- [ ] All APIs have permission decorators
- [ ] Input validation on all user input
- [ ] Database transactions used properly
- [ ] Schema switching used for tenant data
- [ ] RPC methods have error handling
- [ ] No N+1 query problems
- [ ] Indexes on frequently queried columns

### Frontend

- [ ] Loading states shown
- [ ] Error states handled
- [ ] User feedback provided (success/error)
- [ ] Input validated client-side (but also server-side)
- [ ] No sensitive data exposed
- [ ] Responsive design considered

### Security

- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] No hardcoded secrets
- [ ] Proper permission checks
- [ ] Sensitive operations logged

### Performance

- [ ] No unnecessary database queries
- [ ] Expensive operations cached
- [ ] Pagination implemented for large datasets
- [ ] No memory leaks (resource cleanup)

### Testing

- [ ] Unit tests for business logic
- [ ] Integration tests for APIs
- [ ] Edge cases tested
- [ ] Error cases tested

---

## Common Pitfalls

### Pitfall 1: Forgetting Schema Switching

```python
# Wrong: Queries default schema
items = MyModel.query.all()  # Queries shared schema!

# Correct: Use context manager
with db.with_project_schema_session(project_id):
    items = MyModel.query.all()  # Queries project_X schema
```

### Pitfall 2: Not Using Transactions

```python
# Wrong: No transaction, partial updates on error
item1.update()
db.session.commit()
item2.update()  # If this fails, item1 is still updated
db.session.commit()

# Correct: Use transaction
try:
    item1.update()
    item2.update()
    db.session.commit()  # Both succeed or both fail
except Exception as e:
    db.session.rollback()
    raise
```

### Pitfall 3: Blocking RPC Calls

```python
# Wrong: Blocks for 30 seconds
result = self.context.rpc_manager.timeout(30).slow_operation()
return result  # User waits 30 seconds

# Correct: Queue for background processing
self.context.rpc_manager.call.slow_operation(project_id=project_id)
return {'status': 'queued', 'message': 'Processing in background'}
```

### Pitfall 4: Missing Error Handling

```python
# Wrong: Unhandled exception crashes plugin
def get(self, project_id):
    item = MyModel.query.get(item_id)  # item_id not defined!
    return item.to_dict()

# Correct: Handle errors
def get(self, project_id, item_id):
    try:
        with db.with_project_schema_session(project_id):
            item = MyModel.query.get(item_id)
            if not item:
                return {'error': 'Not found'}, 404
            return item.to_dict()
    except Exception as e:
        log.error(f"Failed to get item: {e}")
        return {'error': 'Internal error'}, 500
```

### Pitfall 5: Not Validating Input

```python
# Wrong: Trust user input
def post(self, project_id):
    data = request.json
    item = MyModel(**data)  # Dangerous!
    db.session.add(item)
    db.session.commit()

# Correct: Validate and sanitize
def post(self, project_id):
    data = request.json

    # Validate required fields
    if not data.get('name'):
        return {'error': 'Name required'}, 400

    # Sanitize and create
    item = MyModel(
        project_id=project_id,
        name=str(data['name']).strip()[:128],
        value=int(data.get('value', 0))
    )

    db.session.add(item)
    db.session.commit()
    return item.to_dict(), 201
```

---

## Additional Resources

- **Architecture**: `ARCHITECTURE.md`
- **Plugin System**: `PLUGIN_SYSTEM.md`
- **Frontend/Backend**: `FRONTEND_BACKEND.md`
- **Plugin Reference**: `PLUGINS_REFERENCE.md`
- **Example Plugins**: `pylon/plugins/*/`
- **Docker Compose**: `docker-compose.yaml`
- **Configuration**: `config/pylon.yml`

## Getting Help

1. **Check logs**: `docker-compose logs -f pylon`
2. **Check documentation**: Read the .md files in this directory
3. **Check existing plugins**: Look at similar functionality
4. **Check RabbitMQ**: http://<APP_IP>:15672
5. **Check database**: `docker exec -it centry-postgres-1 psql -U carrier -d carrier`

## Contributing

When contributing to the Carrier platform:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Update documentation
5. Submit pull request
6. Address review comments

Happy developing!

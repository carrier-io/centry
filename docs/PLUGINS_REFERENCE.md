# Carrier Platform - Available Plugins Reference

## Overview

This document provides a comprehensive reference of all available plugins in the Carrier platform. Each plugin is documented with its purpose, dependencies, key features, and APIs.

## Plugin Categories

- [Core Foundation](#core-foundation)
- [Authentication](#authentication)
- [UI & Theme](#ui--theme)
- [Project Management](#project-management)
- [Performance Testing](#performance-testing)
- [Task Execution](#task-execution)
- [Cloud Integrations](#cloud-integrations)
- [Reporting](#reporting)
- [Engagement & Collaboration](#engagement--collaboration)
- [Storage & Secrets](#storage--secrets)
- [Scheduling & Automation](#scheduling--automation)

---

## Core Foundation

### shared

**Purpose**: Foundation library providing core utilities and tools used by all other plugins.

**Version**: Latest
**Dependencies**: None (root plugin)

**Key Features**:
- Database tools and ORM (SQLAlchemy)
- Database migration utilities (Alembic)
- RPC tools for inter-plugin communication
- API tools and base classes
- MinIO client for object storage
- Vault client for secrets management
- Loki client for logging
- Session management (Redis)
- Jinja2 filters and helpers

**Location**: `pylon/plugins/shared/`

**Key Tools**:
```python
from tools import db                    # Database utilities
from tools import db_migrations         # Migration tools
from tools import rpc_tools             # RPC helpers
from tools import api_tools             # API base classes
from tools.MinioClient import MinioClient
from tools.VaultClient import VaultClient
```

---

### market

**Purpose**: Plugin marketplace and package manager for discovering, installing, and managing plugins.

**Version**: Latest
**Dependencies**: None

**Key Features**:
- Plugin discovery and installation
- Plugin version management
- Dependency resolution
- Plugin configuration management
- Local plugin preordering

**Configuration**: `config/pylon.yml` → `configs.market.local_preordered_plugins`

**Location**: `pylon/plugins/market/`

---

### integrations

**Purpose**: Base framework for external service integrations (AWS, GCP, email, etc.).

**Version**: Latest
**Dependencies**: None

**Key Features**:
- Integration registry
- Connection management
- Credential handling
- Integration testing
- Base classes for integration plugins

**Location**: `pylon/plugins/integrations/`

---

## Authentication

### auth

**Purpose**: Main authentication utilities and decorators for the pylon (main app) service.

**Version**: Latest
**Dependencies**: None (init_after: shared)

**Key Features**:
- Permission decorators (`@auth.decorators.check_api()`)
- Session handling
- User context management
- Permission checking utilities
- Integration with pylon_auth service

**Location**: `pylon/plugins/auth/`

**Common Usage**:
```python
from tools import auth

@auth.decorators.check_api(["backend_performance"])
def get(self, project_id):
    # Protected endpoint
    pass

# Check permissions in code
if auth.user_has_permission('my_plugin', project_id):
    # Allow operation
    pass
```

---

### auth_root (pylon_auth)

**Purpose**: Root authentication plugin for the pylon_auth service.

**Version**: Latest
**Dependencies**: None
**Service**: pylon_auth

**Key Features**:
- Base authentication infrastructure
- Root-level auth configuration
- Auth service initialization

**Location**: `pylon_auth/plugins/auth_root/`

---

### auth_core (pylon_auth)

**Purpose**: Core authentication service providing user management, permissions, and OAuth/OIDC support.

**Version**: Latest
**Dependencies**: auth_root
**Service**: pylon_auth

**Key Features**:
- User management (CRUD operations)
- Role and permission management
- OAuth2/OIDC authentication flows
- Bearer token handling
- Session management
- Multiple auth provider support (Basic, Bearer, OAuth, OIDC)
- User/group/scope management
- Keycloak integration

**Location**: `pylon_auth/plugins/auth_core/module.py` (68KB)

**Key RPCs**:
- `auth_add_user` - Create new user
- `auth_update_user` - Update user details
- `auth_delete_user` - Delete user
- `auth_get_user_permissions` - Get user's permissions
- `auth_set_permission_for_role` - Assign permission to role
- `auth_register_auth_provider` - Register auth provider
- `auth_handle_bearer_token` - Validate bearer token

---

### auth_oidc (pylon_auth)

**Purpose**: OpenID Connect integration for enterprise SSO.

**Version**: Latest
**Dependencies**: auth_root, auth_core
**Service**: pylon_auth

**Key Features**:
- OIDC authentication flow
- Integration with Keycloak
- ID token validation
- User info endpoint integration

**Location**: `pylon_auth/plugins/auth_oidc/`

---

### auth_manager (pylon_auth)

**Purpose**: User management interface and APIs.

**Version**: Latest
**Dependencies**: auth_root
**Service**: pylon_auth

**Key Features**:
- User administration UI
- User CRUD APIs
- Group management
- Role assignment

**Location**: `pylon_auth/plugins/auth_manager/`

---

### auth_init (pylon_auth)

**Purpose**: Authentication initialization and setup.

**Version**: Latest
**Dependencies**: auth_root
**Service**: pylon_auth

**Key Features**:
- Initial auth setup
- Default user/role creation
- Auth database initialization

**Location**: `pylon_auth/plugins/auth_init/`

---

### auth_mappers (pylon_auth)

**Purpose**: OAuth provider mappings and user attribute mapping.

**Version**: Latest
**Dependencies**: auth_root
**Service**: pylon_auth

**Key Features**:
- OAuth provider configuration
- User attribute mapping
- Claim transformations
- Provider-specific handlers

**Location**: `pylon_auth/plugins/auth_mappers/`

---

## UI & Theme

### theme

**Purpose**: Theme engine and UI rendering system.

**Version**: Latest
**Dependencies**: shared, auth

**Key Features**:
- Dynamic page registration
- Section and subsection management
- Slot-based content injection
- Permission-based UI rendering
- Template rendering utilities
- Mode management (admin, project, etc.)

**Location**: `pylon/plugins/theme/module.py` (17KB)

**Key Concepts**:
- **Modes**: Top-level UI sections (admin, projects, etc.)
- **Sections**: Categories within modes
- **Subsections**: Pages within sections
- **Slots**: Dynamic content injection points

---

### design-system

**Purpose**: Design system and component library.

**Version**: Latest
**Dependencies**: theme

**Key Features**:
- Reusable UI components
- Consistent styling
- Component documentation
- Design tokens

**Location**: `pylon/plugins/design-system/`

---

### admin

**Purpose**: Admin interface for system management.

**Version**: Latest
**Dependencies**: shared, auth, theme

**Key Features**:
- Project management UI
- User management UI
- Role and permission management
- System settings
- Plugin management
- Runtime monitoring

**Location**: `pylon/plugins/admin/`

**Admin Sections**:
- Projects
- Users
- Roles
- Permissions
- System Status
- Configurations

---

## Project Management

### projects

**Purpose**: Project management and multi-tenancy support.

**Version**: 0.5
**Dependencies**: shared, tasks, auth (init_after: scheduling)

**Key Features**:
- Project CRUD operations
- Multi-tenant database schema management
- Project quotas and limits
- Project settings and configuration
- Keycloak group integration
- Plugin enablement per project

**Location**: `pylon/plugins/projects/`

**Database**:
- **Shared Schema**: `carrier.projects` table
- **Per-Project Schemas**: `project_{id}.*` tables

**Key APIs**:
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/<id>` - Get project
- `PUT /api/v1/projects/<id>` - Update project
- `DELETE /api/v1/projects/<id>` - Delete project

**Key RPCs**:
- `projects_get_project` - Get project by ID
- `projects_create_project` - Create new project
- `projects_list_projects` - List all projects

---

## Performance Testing

### backend_performance

**Purpose**: Backend/API performance testing (load, stress, soak tests).

**Version**: 0.2
**Dependencies**: shared, projects, tasks, theme (init_after: integrations)

**Key Features**:
- HTTP/REST API performance testing
- Load/stress/soak test types
- JMeter, Gatling, Locust integration
- Request rate and concurrency control
- Response time metrics
- Error rate tracking
- Custom assertions and validations
- Test result storage and analysis
- Historical trend analysis

**Location**: `pylon/plugins/backend_performance/`

**Test Types**:
- **Load Test**: Steady load to measure performance
- **Stress Test**: Increasing load to find breaking point
- **Soak Test**: Extended duration to find memory leaks

**Key Features per Test**:
- Environment configuration
- Test data management
- Request builders
- Response validators
- Metric collectors

**Database Tables** (project schema):
- `backend_performance_tests` - Test configurations
- `backend_performance_test_results` - Test execution results
- `backend_performance_test_metrics` - Detailed metrics

**Key APIs**:
- `GET /api/v1/backend_performance/<project_id>/tests` - List tests
- `POST /api/v1/backend_performance/<project_id>/tests` - Create test
- `POST /api/v1/backend_performance/<project_id>/tests/<test_id>/run` - Run test
- `GET /api/v1/backend_performance/<project_id>/results/<result_id>` - Get results

---

### ui_performance

**Purpose**: UI/frontend performance testing (page load, rendering, interaction).

**Version**: 0.1
**Dependencies**: shared, projects, tasks, theme (init_after: integrations)

**Key Features**:
- Browser automation (Selenium, Puppeteer, Playwright)
- Page load time measurement
- First Contentful Paint (FCP)
- Time to Interactive (TTI)
- Cumulative Layout Shift (CLS)
- Lighthouse integration
- Screenshot capture
- Network waterfall analysis
- JavaScript execution profiling

**Location**: `pylon/plugins/ui_performance/`

**Metrics Collected**:
- Load Time
- First Paint
- First Contentful Paint
- Time to Interactive
- DOM Content Loaded
- Page Size
- Request Count
- JavaScript Heap Size

**Database Tables** (project schema):
- `ui_performance_tests` - Test configurations
- `ui_performance_test_results` - Test execution results
- `ui_performance_test_metrics` - Detailed metrics

**Key APIs**:
- `GET /api/v1/ui_performance/<project_id>/tests` - List tests
- `POST /api/v1/ui_performance/<project_id>/tests` - Create test
- `POST /api/v1/ui_performance/<project_id>/tests/<test_id>/run` - Run test
- `GET /api/v1/ui_performance/<project_id>/results/<result_id>` - Get results

---

### performance_test_suite

**Purpose**: Test suite management for organizing and running multiple tests.

**Version**: Latest
**Dependencies**: shared, projects, backend_performance, ui_performance, theme

**Key Features**:
- Group tests into suites
- Sequential and parallel execution
- Suite-level reporting
- Test dependencies
- Pre/post test hooks

**Location**: `pylon/plugins/performance_test_suite/`

---

### performance_analysis

**Purpose**: Performance data analysis and reporting.

**Version**: Latest
**Dependencies**: shared, auth, theme, projects

**Key Features**:
- Statistical analysis of test results
- Trend analysis over time
- Comparison between test runs
- SLA validation
- Performance regression detection
- Custom dashboards
- Export to various formats

**Location**: `pylon/plugins/performance_analysis/`

**Analysis Types**:
- Response time percentiles (p50, p90, p95, p99)
- Error rate analysis
- Throughput trends
- Resource utilization
- Bottleneck identification

---

## Task Execution

### tasks

**Purpose**: Task execution engine for running tests and background jobs.

**Version**: 0.3
**Dependencies**: secrets, integrations

**Key Features**:
- Task queue management (via RabbitMQ)
- Task status tracking
- Task cancellation
- Task result storage
- Parallel task execution
- Task prioritization
- Integration with Interceptor service

**Location**: `pylon/plugins/tasks/`

**Task States**:
- `pending` - Queued for execution
- `running` - Currently executing
- `completed` - Successfully finished
- `failed` - Execution failed
- `cancelled` - Manually cancelled

**Database Tables** (project schema):
- `tasks` - Task definitions and status

**Key APIs**:
- `GET /api/v1/tasks/<project_id>` - List tasks
- `POST /api/v1/tasks/<project_id>` - Create task
- `GET /api/v1/tasks/<project_id>/<task_id>` - Get task status
- `DELETE /api/v1/tasks/<project_id>/<task_id>` - Cancel task

**Key RPCs**:
- `tasks_run_task` - Execute task
- `tasks_get_status` - Get task status
- `tasks_cancel_task` - Cancel running task

---

## Cloud Integrations

### aws_integration

**Purpose**: AWS service integration (S3, EC2, Lambda, etc.).

**Version**: Latest
**Dependencies**: integrations

**Key Features**:
- AWS credential management
- S3 bucket operations
- EC2 instance management
- Lambda function invocation
- CloudWatch metrics
- IAM role integration

**Location**: `pylon/plugins/aws_integration/`

---

### gcp_integration

**Purpose**: Google Cloud Platform integration.

**Version**: Latest
**Dependencies**: integrations

**Key Features**:
- GCP credential management
- Cloud Storage operations
- Compute Engine management
- Cloud Functions integration
- Stackdriver monitoring

**Location**: `pylon/plugins/gcp_integration/`

---

### s3_integration

**Purpose**: S3-compatible storage integration (AWS S3, MinIO, etc.).

**Version**: Latest
**Dependencies**: integrations

**Key Features**:
- S3 bucket management
- Object upload/download
- Presigned URLs
- Multipart uploads
- Object versioning
- Bucket policies

**Location**: `pylon/plugins/s3_integration/`

---

### kubernetes

**Purpose**: Kubernetes cluster integration.

**Version**: Latest
**Dependencies**: integrations

**Key Features**:
- Cluster connection management
- Pod deployment and management
- Service discovery
- ConfigMap/Secret management
- Job execution
- Resource monitoring

**Location**: `pylon/plugins/kubernetes/`

---

## Reporting

### email_base

**Purpose**: Base email functionality.

**Version**: Latest
**Dependencies**: integrations, tasks

**Key Features**:
- Email configuration (SMTP)
- Email sending
- Template support
- Attachment handling
- Email queue management

**Location**: `pylon/plugins/email_base/`

---

### email_template

**Purpose**: Email templating system.

**Version**: Latest
**Dependencies**: email_base

**Key Features**:
- Template management
- Variable substitution
- HTML/Text email generation
- Template preview
- Localization support

**Location**: `pylon/plugins/email_template/`

---

### reporter_email

**Purpose**: Email reporting for test results.

**Version**: Latest
**Dependencies**: integrations, tasks

**Key Features**:
- Automated test result emails
- Scheduled reports
- Custom email templates
- Recipient management
- Report attachments (PDF, CSV)

**Location**: `pylon/plugins/reporter_email/`

---

### reporter_jira

**Purpose**: Jira integration for issue creation and tracking.

**Version**: Latest
**Dependencies**: integrations

**Key Features**:
- Jira connection management
- Automatic issue creation for failures
- Issue status updates
- Custom field mapping
- Attachment upload
- Comment management

**Location**: `pylon/plugins/reporter_jira/`

**Configuration**:
- Jira URL
- Authentication (API token, OAuth)
- Project and issue type mapping
- Field mappings

---

### reporter_engagement

**Purpose**: Engagement reporting and metrics.

**Version**: Latest
**Dependencies**: integrations, engagements

**Key Features**:
- Engagement status reports
- Activity summaries
- Team collaboration metrics
- Milestone tracking

**Location**: `pylon/plugins/reporter_engagement/`

---

## Engagement & Collaboration

### engagements

**Purpose**: Engagement management for organizing work and teams.

**Version**: 0.1
**Dependencies**: shared, theme, auth, shared_orch

**Key Features**:
- Engagement creation and management
- Team assignment
- Milestone tracking
- Engagement-specific workflows
- Resource allocation
- Engagement-level permissions

**Location**: `pylon/plugins/engagements/`

**Database Tables** (project schema):
- `engagements` - Engagement definitions
- `engagement_members` - Team members
- `engagement_milestones` - Milestones

**Key APIs**:
- `GET /api/v1/engagements/<project_id>` - List engagements
- `POST /api/v1/engagements/<project_id>` - Create engagement
- `GET /api/v1/engagements/<project_id>/<engagement_id>` - Get engagement
- `PUT /api/v1/engagements/<project_id>/<engagement_id>` - Update engagement

---

### issues

**Purpose**: Issue tracking and bug management.

**Version**: Latest
**Dependencies**: shared, auth, theme, audit_logs, shared_orch, engagements

**Key Features**:
- Issue creation and tracking
- Priority and severity levels
- Status workflow
- Assignment and ownership
- Comments and attachments
- Issue linking
- Search and filtering

**Location**: `pylon/plugins/issues/`

**Issue States**:
- Open
- In Progress
- Resolved
- Closed
- Reopened

---

### kanban

**Purpose**: Kanban board for task visualization and management.

**Version**: Latest
**Dependencies**: shared, auth, theme, audit_logs, shared_orch, secrets, engagements

**Key Features**:
- Customizable board columns
- Card creation and management
- Drag-and-drop interface
- WIP limits
- Board templates
- Multiple boards per project
- Card filtering and search

**Location**: `pylon/plugins/kanban/`

**Board Columns** (customizable):
- Backlog
- To Do
- In Progress
- Review
- Done

---

### audit_logs

**Purpose**: Audit logging for compliance and security.

**Version**: Latest
**Dependencies**: shared, auth, theme

**Key Features**:
- Automatic action logging
- User activity tracking
- Change history
- Security event logging
- Compliance reporting
- Log search and filtering
- Log retention policies

**Location**: `pylon/plugins/audit_logs/`

**Logged Events**:
- User actions (create, update, delete)
- Permission changes
- Configuration changes
- Login/logout events
- API access

---

### shared_orch

**Purpose**: Shared orchestration library for workflow management.

**Version**: Latest
**Dependencies**: shared, auth, theme

**Key Features**:
- Workflow definitions
- Step orchestration
- Conditional execution
- Parallel execution
- Error handling
- Workflow templates

**Location**: `pylon/plugins/shared_orch/`

---

## Storage & Secrets

### secrets

**Purpose**: Secrets management using HashiCorp Vault.

**Version**: Latest
**Dependencies**: shared

**Key Features**:
- Vault integration
- Secret storage and retrieval
- Secret rotation
- Access control
- Secret versioning
- Environment-specific secrets

**Location**: `pylon/plugins/secrets/`

**Secret Types**:
- API keys
- Database credentials
- OAuth tokens
- SSH keys
- Certificates

**Key APIs**:
- `GET /api/v1/secrets/<project_id>` - List secrets (metadata only)
- `POST /api/v1/secrets/<project_id>` - Create secret
- `GET /api/v1/secrets/<project_id>/<secret_id>` - Get secret value
- `DELETE /api/v1/secrets/<project_id>/<secret_id>` - Delete secret

---

### artifacts

**Purpose**: Artifact storage and management (test results, logs, reports).

**Version**: Latest
**Dependencies**: shared, theme

**Key Features**:
- Artifact upload/download
- MinIO integration
- Artifact metadata
- Artifact retention policies
- Artifact search
- Public/private artifacts
- Download links (presigned URLs)

**Location**: `pylon/plugins/artifacts/`

**Artifact Types**:
- Test results
- Log files
- Screenshots
- Reports (PDF, HTML)
- Configuration files

**Key APIs**:
- `GET /api/v1/artifacts/<project_id>` - List artifacts
- `POST /api/v1/artifacts/<project_id>` - Upload artifact
- `GET /api/v1/artifacts/<project_id>/<artifact_id>` - Download artifact
- `DELETE /api/v1/artifacts/<project_id>/<artifact_id>` - Delete artifact

---

## Scheduling & Automation

### scheduling

**Purpose**: Cron job scheduling and automation.

**Version**: Latest
**Dependencies**: shared, theme, tasks, secrets

**Key Features**:
- Cron expression support
- Scheduled test execution
- Job history and logs
- Email notifications
- Job dependencies
- Timezone support
- One-time and recurring jobs

**Location**: `pylon/plugins/scheduling/`

**Schedule Types**:
- Cron (e.g., `0 0 * * *` for daily)
- Interval (e.g., every 5 minutes)
- One-time (specific date/time)

**Database Tables** (project schema):
- `scheduled_jobs` - Job definitions
- `job_executions` - Execution history

**Key APIs**:
- `GET /api/v1/scheduling/<project_id>/jobs` - List scheduled jobs
- `POST /api/v1/scheduling/<project_id>/jobs` - Create scheduled job
- `PUT /api/v1/scheduling/<project_id>/jobs/<job_id>` - Update job
- `DELETE /api/v1/scheduling/<project_id>/jobs/<job_id>` - Delete job

---

## Plugin Dependency Graph

```
shared (foundation)
  ├─→ auth
  ├─→ theme
  │   ├─→ admin
  │   ├─→ design-system
  │   ├─→ artifacts
  │   └─→ performance_analysis
  ├─→ secrets
  │   └─→ tasks
  │       ├─→ backend_performance
  │       ├─→ ui_performance
  │       ├─→ scheduling
  │       └─→ email_base
  ├─→ integrations
  │   ├─→ tasks (also depends on secrets)
  │   ├─→ aws_integration
  │   ├─→ gcp_integration
  │   ├─→ s3_integration
  │   ├─→ kubernetes
  │   ├─→ reporter_email
  │   ├─→ reporter_jira
  │   └─→ email_base
  └─→ shared_orch
      ├─→ engagements
      ├─→ issues
      └─→ kanban

projects (depends on: shared, tasks, auth)
  ├─→ backend_performance
  ├─→ ui_performance
  └─→ performance_test_suite

auth (pylon_auth service)
  ├─→ auth_root
  │   ├─→ auth_core
  │   ├─→ auth_oidc
  │   ├─→ auth_manager
  │   ├─→ auth_init
  │   └─→ auth_mappers
```

---

## Quick Reference

### Most Used Plugins

1. **projects** - Project management (required for multi-tenancy)
2. **auth** - Authentication and permissions
3. **theme** - UI rendering
4. **tasks** - Task execution
5. **backend_performance** - Backend testing
6. **ui_performance** - Frontend testing
7. **scheduling** - Automated test runs
8. **artifacts** - Result storage

### Plugin Loading Order

The system automatically resolves dependencies and loads plugins in the correct order. The general sequence is:

1. **shared** (foundation)
2. **integrations** (no dependencies)
3. **market** (no dependencies)
4. **secrets** (depends: shared)
5. **tasks** (depends: secrets, integrations)
6. **auth** (depends: shared)
7. **theme** (depends: shared, auth)
8. **scheduling** (depends: shared, theme, tasks, secrets)
9. **projects** (depends: shared, tasks, auth; init_after: scheduling)
10. **admin** (depends: shared, auth, theme)
11. **backend_performance** (depends: shared, projects, tasks, theme)
12. **ui_performance** (depends: shared, projects, tasks, theme)
13. ... (other plugins based on their dependencies)

### Common Plugin Patterns

#### Creating a Test Plugin

Dependencies needed:
- `shared` - Database and tools
- `projects` - Multi-tenant support
- `tasks` - Test execution
- `theme` - UI rendering

#### Creating an Integration Plugin

Dependencies needed:
- `integrations` - Base integration framework

#### Creating a Reporting Plugin

Dependencies needed:
- `integrations` - Connection management
- `tasks` - Background job execution

---

## Plugin Configuration

### Per-Plugin Configuration

Each plugin can have a `config.yml` file:

```yaml
# pylon/plugins/my_plugin/config.yml
settings:
  enabled: true
  max_concurrent: 5

features:
  advanced_mode: false
```

Access in plugin:
```python
config = self.descriptor.config
enabled = config.get('settings', {}).get('enabled', True)
```

### Global Plugin Configuration

In `config/pylon.yml`:

```yaml
configs:
  backend_performance:
    max_test_duration: 3600
    default_engine: jmeter

  ui_performance:
    browser: chrome
    headless: true
```

---

## Creating a New Plugin

### Minimal Steps

1. Create directory: `pylon/plugins/my_plugin/`
2. Create `metadata.json`:
   ```json
   {
     "name": "my_plugin",
     "version": "1.0.0",
     "depends_on": ["shared"]
   }
   ```
3. Create `module.py` with Module class
4. Create `__init__.py` exporting Module
5. Add to `config/pylon.yml` preordered_plugins
6. Restart pylon service

### Full Plugin Template

See `PLUGIN_SYSTEM.md` for complete plugin development guide.

---

## References

- **Architecture**: `ARCHITECTURE.md`
- **Plugin System**: `PLUGIN_SYSTEM.md`
- **Frontend/Backend**: `FRONTEND_BACKEND.md`
- **Development Guide**: `DEVELOPMENT_GUIDE.md`
- **Plugin Source**: `pylon/plugins/*/`
- **Auth Plugins**: `pylon_auth/plugins/*/`

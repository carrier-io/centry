# Carrier Platform - Documentation Index

## Welcome

This is the comprehensive documentation for the Carrier (Centry) platform - a plugin-based performance testing and engagement automation platform. This documentation is designed to help developers understand, maintain, and extend the platform.

## Quick Start

**New to Carrier?** Start here:

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for system overview
2. Read [PLUGIN_SYSTEM.md](PLUGIN_SYSTEM.md) to understand plugins
3. Review [PLUGINS_REFERENCE.md](PLUGINS_REFERENCE.md) to see available plugins
4. Use [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) when working on code

## Documentation Structure

### 📐 [ARCHITECTURE.md](ARCHITECTURE.md)
**Purpose**: Understand the overall system architecture

**Contents**:
- High-level architecture overview
- Component descriptions (Pylon, services, databases)
- Dual-pylon architecture (main app + auth service)
- Service infrastructure (Traefik, PostgreSQL, RabbitMQ, etc.)
- Database multi-tenancy design
- Plugin architecture overview
- Communication patterns (REST, RPC, Events)
- Authentication flow
- Configuration management
- Deployment structure

**When to use**:
- Starting a new feature that spans multiple plugins
- Understanding how services communicate
- Troubleshooting infrastructure issues
- Planning architectural changes
- Onboarding new developers

---

### 🔌 [PLUGIN_SYSTEM.md](PLUGIN_SYSTEM.md)
**Purpose**: Deep dive into the plugin system

**Contents**:
- Plugin structure and layout
- Core plugin files (metadata.json, module.py, etc.)
- Plugin lifecycle (loading, initialization, cleanup)
- Dependency management
- Communication between plugins (RPC, Events, DB)
- API endpoint creation
- Database model definition
- UI integration (templates, slots)
- Permissions system
- Background tasks
- Testing plugins
- Best practices and common pitfalls

**When to use**:
- Creating a new plugin
- Modifying existing plugin
- Understanding plugin dependencies
- Implementing inter-plugin communication
- Debugging plugin loading issues
- Adding RPC methods or API endpoints

---

### 💻 [FRONTEND_BACKEND.md](FRONTEND_BACKEND.md)
**Purpose**: Frontend and backend development patterns

**Contents**:
- Backend architecture (Flask, SQLAlchemy, RabbitMQ)
- REST API layer (APIModeHandler)
- RPC layer (inter-plugin communication)
- Event system (pub/sub)
- Database models (multi-tenant, shared)
- Frontend architecture (Jinja2, Vue.js)
- Template structure
- Vue.js application patterns
- UI slots and dynamic content
- Communication patterns (backend-backend, frontend-backend)
- Best practices for both layers
- Performance optimization
- Debugging techniques

**When to use**:
- Creating new API endpoints
- Building UI components
- Implementing RPC methods
- Working with Vue.js
- Database model design
- Optimizing API performance
- Frontend state management

---

### 📚 [PLUGINS_REFERENCE.md](PLUGINS_REFERENCE.md)
**Purpose**: Comprehensive reference of all available plugins

**Contents**:
- Plugin categories (Core, Auth, UI, Testing, Cloud, etc.)
- Detailed description of each plugin (32+ plugins)
- Plugin dependencies
- Key features per plugin
- API endpoints per plugin
- RPC methods per plugin
- Database tables per plugin
- Configuration options
- Usage examples
- Plugin dependency graph
- Quick reference guide

**When to use**:
- Looking for existing functionality
- Understanding what a plugin does
- Finding the right plugin for a task
- Checking plugin dependencies
- Understanding plugin APIs
- Planning feature implementation
- Avoiding duplicate functionality

---

### 🛠️ [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
**Purpose**: Practical guide for day-to-day development

**Contents**:
- Development environment setup
- Common development tasks (with examples)
  - Modifying existing plugins
  - Adding API endpoints
  - Adding RPC methods
  - Creating database models
  - Adding UI components
- Bug fixing workflow
- Feature development process
- Testing (manual and automated)
- Debugging techniques
- Performance optimization
- Security considerations
- Code review checklist
- Common pitfalls to avoid

**When to use**:
- Setting up development environment
- Fixing bugs
- Adding new features
- Writing tests
- Debugging issues
- Optimizing performance
- Before submitting code for review
- Daily development work

---

## Documentation Usage by Task

### Task: "I need to fix a bug in the backend_performance plugin"

1. **Understand the plugin**: [PLUGINS_REFERENCE.md](PLUGINS_REFERENCE.md) → "Performance Testing" section
2. **Locate the issue**: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) → "Bug Fixing Workflow"
3. **Understand the code**: [FRONTEND_BACKEND.md](FRONTEND_BACKEND.md) → "Backend Architecture"
4. **Fix and test**: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) → "Testing" section

---

### Task: "I need to create a new plugin for Azure integration"

1. **Understand plugin system**: [PLUGIN_SYSTEM.md](PLUGIN_SYSTEM.md) → Read entire document
2. **Check existing patterns**: [PLUGINS_REFERENCE.md](PLUGINS_REFERENCE.md) → "Cloud Integrations" → aws_integration
3. **Create plugin structure**: [PLUGIN_SYSTEM.md](PLUGIN_SYSTEM.md) → "Plugin Structure"
4. **Implement functionality**: [FRONTEND_BACKEND.md](FRONTEND_BACKEND.md) → API and RPC sections
5. **Follow best practices**: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) → "Adding New Features"

---

### Task: "I need to add a new API endpoint to projects plugin"

1. **Understand REST API patterns**: [FRONTEND_BACKEND.md](FRONTEND_BACKEND.md) → "REST API Layer"
2. **See examples**: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) → "Task 2: Adding a New API Endpoint"
3. **Check project plugin details**: [PLUGINS_REFERENCE.md](PLUGINS_REFERENCE.md) → "Project Management" → projects
4. **Test the endpoint**: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) → "Testing" → "API Testing with curl"

---

### Task: "I need to understand how authentication works"

1. **High-level overview**: [ARCHITECTURE.md](ARCHITECTURE.md) → "Authentication Flow"
2. **Auth plugins**: [PLUGINS_REFERENCE.md](PLUGINS_REFERENCE.md) → "Authentication" section
3. **Using auth in code**: [PLUGIN_SYSTEM.md](PLUGIN_SYSTEM.md) → "Permissions"
4. **Security best practices**: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) → "Security Considerations"

---

### Task: "I need to optimize database queries"

1. **Database architecture**: [ARCHITECTURE.md](ARCHITECTURE.md) → "Database Architecture"
2. **Model patterns**: [FRONTEND_BACKEND.md](FRONTEND_BACKEND.md) → "Database Models"
3. **Optimization techniques**: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) → "Performance Optimization" → "Database Optimization"

---

### Task: "I need to create a UI component"

1. **Frontend patterns**: [FRONTEND_BACKEND.md](FRONTEND_BACKEND.md) → "Frontend Architecture"
2. **Example implementation**: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) → "Task 5: Adding a UI Component"
3. **UI slots**: [PLUGIN_SYSTEM.md](PLUGIN_SYSTEM.md) → "UI Integration" → "Slots"
4. **Theme integration**: [PLUGINS_REFERENCE.md](PLUGINS_REFERENCE.md) → "UI & Theme" → theme

---

## Quick Reference

### Key Concepts

- **Plugin**: Self-contained module providing specific functionality
- **Pylon**: Framework that orchestrates plugins
- **RPC**: Remote Procedure Call for inter-plugin communication
- **Schema**: Database namespace for multi-tenant isolation
- **Slot**: UI injection point for dynamic content
- **Descriptor**: Plugin metadata and registration interface

### Key Files

```
centry/
├── ARCHITECTURE.md               # System architecture
├── PLUGIN_SYSTEM.md             # Plugin development
├── FRONTEND_BACKEND.md          # Frontend/backend patterns
├── PLUGINS_REFERENCE.md         # Available plugins
├── DEVELOPMENT_GUIDE.md         # Development workflows
├── docker-compose.yaml          # Infrastructure
├── .env                         # Environment config
├── Makefile                     # Deployment automation
├── config/
│   ├── pylon.yml               # Main app config
│   └── pylon_auth.yml          # Auth service config
├── pylon/
│   └── plugins/                # Main app plugins (32+)
└── pylon_auth/
    └── plugins/                # Auth service plugins
```

### Key Commands

```bash
# Deploy
make up INTERFACE=eth0

# View logs
docker-compose logs -f pylon
docker-compose logs -f pylon_auth

# Restart service
docker-compose restart pylon

# Access shell
docker exec -it centry-pylon-1 bash

# Database access
docker exec -it centry-postgres-1 psql -U carrier -d carrier

# Stop all
make down
```

### Key URLs

- Main App: http://<APP_IP>
- RabbitMQ Management: http://<APP_IP>:15672
- MinIO Console: http://<APP_IP>:9000

## Documentation Maintenance

### When to Update Documentation

- **Adding new plugin**: Update [PLUGINS_REFERENCE.md](PLUGINS_REFERENCE.md)
- **Changing architecture**: Update [ARCHITECTURE.md](ARCHITECTURE.md)
- **New development patterns**: Update [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
- **Plugin system changes**: Update [PLUGIN_SYSTEM.md](PLUGIN_SYSTEM.md)
- **Frontend/backend patterns**: Update [FRONTEND_BACKEND.md](FRONTEND_BACKEND.md)

### Documentation Best Practices

1. **Keep examples up-to-date** - Test code examples regularly
2. **Add practical examples** - Real-world scenarios help understanding
3. **Cross-reference** - Link between documents for related topics
4. **Update incrementally** - Don't wait for major changes
5. **Include context** - Explain the "why", not just the "what"

## Using Documentation with Claude Code

These documentation files are designed to work with Claude Code (AI assistant) to:

1. **Answer questions** about the platform
2. **Generate code** following platform patterns
3. **Debug issues** using documented patterns
4. **Suggest improvements** based on best practices
5. **Create new plugins** following the standard structure

When asking Claude Code for help:
- Reference specific documentation sections
- Provide context from the platform
- Mention which plugin you're working with
- Include relevant error messages or logs

Example prompts:
- "Using the patterns in PLUGIN_SYSTEM.md, create a new plugin for Slack integration"
- "Following DEVELOPMENT_GUIDE.md, help me debug this RPC timeout issue"
- "Based on FRONTEND_BACKEND.md, optimize these database queries"
- "Check my code against the checklist in DEVELOPMENT_GUIDE.md"

## Contributing to Documentation

When contributing:

1. **Follow the existing structure** - Each document has a specific purpose
2. **Use clear headings** - Make sections easy to find
3. **Include code examples** - Show, don't just tell
4. **Add cross-references** - Link to related sections
5. **Test examples** - Ensure code examples work
6. **Update this index** - Keep the index current

## Feedback

If you find:
- Missing information
- Unclear explanations
- Outdated examples
- Broken links
- Opportunities for improvement

Please update the documentation or create an issue.

## Version

- **Documentation Version**: 1.0
- **Platform Version**: beta-3.0
- **Last Updated**: 2026-02-04

---

**Happy developing on the Carrier platform!**

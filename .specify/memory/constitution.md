<!--
Sync Impact Report:
Version: 1.1.0 → 1.2.0 (Branch Strategy Amendment)
Modified Principles:
  - Principle I: Added "Branch Strategy for Plugin Development" section (CRITICAL workflow rule)
Added Sections:
  - Branch Strategy for Plugin Development (dual-repository model: Centry on speckit-dev, plugins on feature branches)
Removed Sections: N/A
Reason: Lesson learned from feature 001-ui-quality-gate-metrics - incorrect feature branch created in Centry repo instead of plugin repo
Templates Status:
  ⚠️ tasks-template.md - T001 needs updated validation and plugin repository navigation commands
  ⚠️ speckit.implement.md - Needs branch validation step before Phase 1 execution
  ✅ plan-template.md - No changes needed (constitution check references principles)
  ✅ spec-template.md - No changes needed (user-focused, no branching details)
Follow-up TODOs:
  - Update tasks-template.md T001 with dual-repository workflow
  - Add branch validation to speckit.implement command
  - Consider adding pre-flight check script for branch verification
Version Bump Rationale: MINOR - New critical section added to existing principle, significantly expands workflow guidance affecting all plugin development
-->

# Centry Platform Constitution

## Core Principles

### I. Plugin-First Architecture

Every feature MUST be implemented as a standalone plugin with clear boundaries and minimal coupling. Plugins are the fundamental unit of modularity in Centry.

**Non-negotiable rules:**
- All new functionality starts as a plugin in the `plugins/` directory
- Each plugin MUST have `metadata.json`, `config.yml`, and `module.py` with `ModuleModel` inheritance
- Plugin dependencies declared explicitly in metadata (`depends_on`, `init_after`)
- No direct imports across plugins—use Pylon context for inter-plugin communication
- Self-contained: dependencies installed via plugin-local `requirements.txt` into plugin's `site-packages/`

**Rationale:** Plugin architecture ensures modularity, independent deployment, and marketplace distribution. It enables teams to work in parallel without merge conflicts and supports gradual feature rollout.

**Resources:** Complete plugin structure guide in `docs/PLUGIN_SYSTEM.md` with lifecycle, dependencies, and communication patterns. Study existing plugins in `docs/PLUGINS_REFERENCE.md` (32+ examples) before creating new plugins.

**Branch Strategy for Plugin Development:**

⚠️ **CRITICAL**: The Centry repository MUST remain on the `speckit-dev` branch for all speckit-based development work.

**Dual Repository Model:**
```
Centry Repository (Main Project):
  - Branch: speckit-dev (ALWAYS - NEVER create feature branches)
  - Purpose: Contains speckit templates (.specify/), generated specs (specs/), and documentation
  - Commits: Speckit configuration, lessons learned, constitution amendments

Plugin Repository (pylon/plugins/<plugin_name>/):
  - Branch: Create feature branches here (e.g., 001-feature-name)
  - Purpose: Plugin implementation code
  - Commits: All feature implementation changes
  - Independent: Separate Git history from Centry repo
```

**Workflow Rules:**
1. **Before starting implementation**: Verify Centry repo is on `speckit-dev` branch
2. **Feature branch creation**: Navigate to plugin directory first
   ```bash
   cd pylon/plugins/<plugin_name>
   git checkout -b 001-feature-name
   ```
3. **Commits**: Implementation code commits go to plugin repo, spec/config commits go to Centry repo
4. **Never**: Create feature branches in Centry repo during speckit workflows

**Rationale**: This dual-repository model separates speckit governance (templates, specs) from implementation code (plugins). The `speckit-dev` branch serves as the stable base for all speckit work, while plugin repositories maintain independent feature branches for code changes.

### II. Contract-Based Integration

Plugins expose functionality via well-defined contracts: REST API endpoints, RPC methods, and configuration schemas.

**Non-negotiable rules:**
- API endpoints follow `/api/v{version}/{resource}` structure
- RPC methods registered through Pylon's RPC system
- Configuration changes backward-compatible or versioned
- Breaking changes require MAJOR version bump
- All public interfaces documented in contracts/ directory

**Rationale:** Explicit contracts enable independent evolution of plugins, prevent coupling, and serve as executable documentation for integration testing.

**Resources:** REST API patterns, RPC method definitions, and Vue.js integration detailed in `docs/FRONTEND_BACKEND.md`. All communication patterns (backend-backend, frontend-backend) documented with code examples.

### III. Test-First for Critical Paths (HIGHLY RECOMMENDED)

Test-driven development is strongly recommended for user-facing features, API contracts, and database migrations.

**Guidelines:**
- Write integration tests for new API endpoints before implementation
- Contract tests verify plugin interfaces match specifications
- Database migration tests ensure schema changes are reversible
- User acceptance scenarios drive test design
- Red-Green-Refactor cycle for high-risk changes

**Rationale:** Test-first prevents regressions in complex plugin interactions and ensures new features integrate properly with existing platform capabilities. Critical for marketplace plugins where failures affect all tenants.

**Resources:** Testing strategies, unit/integration test examples, and debugging techniques in `docs/DEVELOPMENT_GUIDE.md` sections "Testing" and "Debugging".

### IV. Database Migration Discipline

Database schema changes follow strict migration patterns with rollback support.

**Non-negotiable rules:**
- All schema changes via versioned migration files in `db/migrations/` (format: `YYYYMMDDHHMM_description.py`)
- Migrations MUST be reversible (implement both upgrade and downgrade)
- Migrations tested in isolation before merge
- No schema changes in application code—migrations only
- Migration dependencies tracked explicitly

**Rationale:** Multi-tenant platform requires zero-downtime deployments and instant rollback capability. Schema errors affect all users and are expensive to fix in production.

**Resources:** Multi-tenant schema switching patterns and database model examples in `docs/FRONTEND_BACKEND.md` section "Database Models". Migration workflow in `docs/DEVELOPMENT_GUIDE.md` Task 4.

### V. Observability & Debugging

Platform operations and plugin interactions must be traceable through structured logging and text-based I/O.

**Non-negotiable rules:**
- Structured logging via Python logging framework (JSON format for production)
- All API requests/responses logged with correlation IDs
- Plugin initialization/deinitialization logged with timing
- Error traces include plugin context and version
- Configuration changes logged before and after values

**Rationale:** Plugin system complexity requires detailed operational visibility. Text logs enable debugging without production access and support automated alerting.

**Resources:** Debugging workflows, log analysis, and troubleshooting scenarios in `docs/DEVELOPMENT_GUIDE.md` section "Debugging".

### VI. Versioning & Breaking Changes

Platform and plugins follow semantic versioning to communicate compatibility.

**Non-negotiable rules:**
- Version format: `MAJOR.MINOR.PATCH` in metadata.json
- MAJOR: Breaking API changes, removed endpoints, incompatible config schema
- MINOR: New features, new optional config, backward-compatible additions
- PATCH: Bug fixes, security patches, documentation
- Plugin dependencies specify version ranges: `"plugin_name": ">=1.2.0,<2.0.0"`

**Rationale:** Marketplace ecosystem requires clear compatibility signals. Users need confidence that plugin updates won't break their installations.

### VII. Simplicity & YAGNI

Start with the simplest implementation that satisfies current requirements. Avoid premature abstraction.

**Guidelines:**
- Direct implementation preferred over frameworks unless complexity justified
- Copy-paste acceptable for 2-3 occurrences—abstract at 4+
- Plugin-local solutions preferred over new shared libraries
- Configuration grows incrementally—no "future-proof" mega-configs
- Avoid over-engineering: implement what's needed today, refactor when patterns emerge

**Rationale:** Plugin architecture already provides modularity. Additional abstraction layers increase cognitive load and maintenance burden without proportional value.

## Architecture & Design

### Plugin Lifecycle

**Plugin Structure:**
```
plugins/my_plugin/
├── metadata.json          # Name, version, dependencies
├── config.yml             # Default configuration
├── module.py              # Module class with init/deinit
├── requirements.txt       # Python dependencies (optional)
├── site-packages/         # Isolated dependency installation
├── api/                   # REST endpoints (optional)
├── rpc/                   # RPC methods (optional)
├── models/                # Data models (optional)
├── db/migrations/         # Database migrations (optional)
└── static/                # Static assets (optional)
```

**Initialization Order:**
1. Market plugin downloads and updates plugins from configured repository
2. Dependencies resolved via topological sort of `depends_on` + `init_after`
3. Plugin requirements installed to local `site-packages/`
4. Plugins initialized in dependency order
5. Routes/RPC registered with Pylon context

### Multi-Tenant Considerations

Centry runs as a multi-tenant platform. Design decisions must account for:
- Tenant isolation at data and configuration levels
- Shared infrastructure (databases, caches, queues) with tenant-specific namespacing
- Plugin marketplace where one plugin serves all tenants
- Performance: one tenant's load must not degrade others

### Technology Stack

**Complete technical details:** `docs/ARCHITECTURE.md`

**Language/Runtime:** Python 3.10+
**Web Framework:** Pylon (custom Flask-based framework)
**Databases:** PostgreSQL (primary), MongoDB (optional per plugin)
**Caching:** Redis
**Message Queue:** RabbitMQ
**Storage:** Local volumes, S3-compatible object storage
**Authentication:** Keycloak (OIDC/OAuth2)
**Deployment:** Docker Compose (development), Docker Swarm or Kubernetes (production)

### Security Requirements

- Authentication via Keycloak—no plugin-local auth schemes
- Authorization enforced at API gateway and plugin entry points
- Secrets managed via Vault or environment variables—never in config files
- SQL injection prevented via parameterized queries (SQLAlchemy ORM)
- XSS protection via template auto-escaping (Jinja2)
- CSRF tokens for state-changing operations

## Development Documentation

The platform maintains comprehensive technical documentation in `docs/` directory. This documentation provides implementation guidance and complements the constitutional principles defined in this document.

### Documentation Structure

**Core Documentation Files:**

- **DOCUMENTATION_INDEX.md**: Master navigation guide with task-oriented usage patterns
- **ARCHITECTURE.md**: System architecture, dual-pylon design, service infrastructure, multi-tenancy, deployment
- **PLUGIN_SYSTEM.md**: Plugin structure, lifecycle, dependency management, communication patterns, best practices
- **DEVELOPMENT_GUIDE.md**: Day-to-day development workflows, bug fixing, testing, debugging, security, code review
- **FRONTEND_BACKEND.md**: REST API patterns, RPC methods, database models, Vue.js integration, performance optimization
- **PLUGINS_REFERENCE.md**: Comprehensive catalog of 32+ plugins with APIs, RPC methods, dependencies, and usage

### Mandatory Reading Requirements

**Before creating a new plugin:**
- Read `docs/PLUGIN_SYSTEM.md` entirely (plugin structure, lifecycle, dependencies, communication)
- Check `docs/PLUGINS_REFERENCE.md` to avoid duplicating existing functionality
- Review `docs/ARCHITECTURE.md` for system integration points

**Before fixing bugs:**
- Consult `docs/DEVELOPMENT_GUIDE.md` section "Bug Fixing Workflow"
- Reference debugging techniques in `docs/DEVELOPMENT_GUIDE.md` section "Debugging"
- Check `docs/ARCHITECTURE.md` for system-level issues (RabbitMQ, PostgreSQL, Redis)

**Before implementing API/RPC changes:**
- Study patterns in `docs/FRONTEND_BACKEND.md` sections "REST API Layer" and "RPC Layer"
- Review authentication patterns in `docs/FRONTEND_BACKEND.md` section "Authentication Decorators"
- Check existing implementations in `docs/PLUGINS_REFERENCE.md`

**Before database changes:**
- Review multi-tenant schema switching in `docs/FRONTEND_BACKEND.md` section "Multi-Tenant Schema Switching"
- Study model examples in `docs/DEVELOPMENT_GUIDE.md` Task 4
- Check migration patterns in `docs/ARCHITECTURE.md` section "Database Architecture"

**Before frontend implementation:**
- Review Vue.js patterns in `docs/FRONTEND_BACKEND.md` section "Vue.js Application"
- Study template structure in `docs/FRONTEND_BACKEND.md` section "Templates (Jinja2)"
- Check UI slot patterns in `docs/PLUGIN_SYSTEM.md` section "UI Integration"

### Documentation Maintenance

**When documentation MUST be updated:**

1. **Plugin architecture changes**: Update `docs/PLUGIN_SYSTEM.md` and `docs/ARCHITECTURE.md`
2. **New API/RPC patterns**: Update `docs/FRONTEND_BACKEND.md` with examples
3. **Development workflow changes**: Update `docs/DEVELOPMENT_GUIDE.md`
4. **New plugin added**: Update `docs/PLUGINS_REFERENCE.md` with plugin details
5. **Infrastructure changes**: Update `docs/ARCHITECTURE.md` and deployment sections

**Documentation update requirements:**
- Updates MUST be atomic with code changes (same PR)
- Code examples MUST be tested and functional
- Cross-references MUST be maintained between documents
- Version numbers and dates MUST be updated

**Documentation vs. Constitution:**
- **Constitution**: Governance, principles, "why", non-negotiable rules
- **Documentation**: Implementation, patterns, "how", practical examples
- **Together**: Complete development framework

### Using Documentation with AI Agents

When using Claude Code or similar AI development tools:

1. **Context Loading**: Reference relevant documentation sections in prompts
   - Example: "Following the pattern in docs/PLUGIN_SYSTEM.md section 'RPC Methods', create an RPC method for..."

2. **Pattern Matching**: Use documentation examples as templates
   - Example: "Using the API structure from docs/FRONTEND_BACKEND.md, implement endpoint..."

3. **Validation**: Cross-check AI outputs against documentation patterns
   - Verify API decorators match `docs/FRONTEND_BACKEND.md` examples
   - Confirm plugin structure matches `docs/PLUGIN_SYSTEM.md` specifications

4. **Constitution + Documentation**: AI should reference both
   - Constitution for governance and principles
   - Documentation for implementation details and patterns

## Development Workflow

### Feature Development Process

1. **Research & Discovery**
   - **Check existing functionality**: Review `docs/PLUGINS_REFERENCE.md` to avoid duplication
   - **Study similar implementations**: Find comparable plugins in `docs/PLUGINS_REFERENCE.md` and examine their patterns
   - **Understand integration points**: Read `docs/ARCHITECTURE.md` for system-level dependencies (RabbitMQ, PostgreSQL, Keycloak)

2. **Specification**
   - Use `/speckit.specify` to create feature spec with user stories and acceptance criteria
   - Reference architecture constraints from `docs/ARCHITECTURE.md`
   - Include security requirements from `docs/DEVELOPMENT_GUIDE.md` section "Security Considerations"

3. **Planning**
   - Use `/speckit.plan` to research integration points and design plugin structure
   - Follow plugin structure guidelines from `docs/PLUGIN_SYSTEM.md` section "Plugin Structure"
   - Plan API/RPC contracts using patterns from `docs/FRONTEND_BACKEND.md`
   - Design database models following multi-tenant patterns in `docs/ARCHITECTURE.md` section "Database Architecture"

4. **Clarification**
   - Use `/speckit.clarify` to resolve underspecified requirements before implementation
   - Consult `docs/DEVELOPMENT_GUIDE.md` for common pitfalls to avoid

5. **Task Generation**
   - Use `/speckit.tasks` to break down implementation into dependency-ordered tasks
   - Structure tasks following workflows in `docs/DEVELOPMENT_GUIDE.md` section "Common Development Tasks"

6. **Implementation**
   - Use `/speckit.implement` to execute tasks with tests (if required) preceding implementation
   - Follow code patterns from `docs/PLUGIN_SYSTEM.md` and `docs/FRONTEND_BACKEND.md`
   - Use code examples from `docs/DEVELOPMENT_GUIDE.md` tasks 1-5 as templates
   - Apply debugging techniques from `docs/DEVELOPMENT_GUIDE.md` section "Debugging"

7. **Testing & Validation**
   - Follow testing strategies from `docs/DEVELOPMENT_GUIDE.md` section "Testing"
   - Use debugging scenarios from `docs/DEVELOPMENT_GUIDE.md` section "Debugging"

8. **Analysis**
   - Use `/speckit.analyze` to verify consistency across spec, plan, and tasks
   - Verify compliance with constitutional principles
   - Check documentation has been updated if patterns changed

### Plugin Development Workflow

**Pre-Development**:
1. Read `docs/PLUGIN_SYSTEM.md` sections "Plugin Structure" and "Core Plugin Files"
2. Check `docs/PLUGINS_REFERENCE.md` for dependency patterns
3. Review similar plugins for implementation patterns

**Development**:
1. Create plugin directory and metadata.json following structure from `docs/PLUGIN_SYSTEM.md`
2. Implement `Module(ModuleModel)` class with `__init__`, `init`, `deinit` methods per `docs/PLUGIN_SYSTEM.md` examples
3. Add routes using patterns from `docs/FRONTEND_BACKEND.md` section "REST API Layer"
4. Add RPC methods using patterns from `docs/FRONTEND_BACKEND.md` section "RPC Layer"
5. Add background tasks referencing `docs/PLUGIN_SYSTEM.md` section "Background Tasks"
6. Test plugin in isolation before integration using `docs/DEVELOPMENT_GUIDE.md` testing guide
7. Document configuration options in config.yml with comments
8. Add plugin to market repository JSON for distribution

### Testing Strategy

**Test Pyramid:**
- Unit tests: Plugin-local logic (models, utilities)
- Integration tests: Plugin interaction with Pylon context, database, external services
- Contract tests: API/RPC interface compliance
- System tests: End-to-end user journeys across multiple plugins

**When tests are required:**
- New API endpoints: Contract test verifying request/response schema
- Database migrations: Test upgrade + downgrade
- Breaking changes: Test backward compatibility or document migration path
- User-reported bugs: Regression test before fix

**Resources:** Complete testing guide in `docs/DEVELOPMENT_GUIDE.md` section "Testing" with manual and automated testing examples.

### Code Review Requirements

- All changes via pull requests—no direct commits to main branch
- PR description references feature spec (e.g., `Implements spec 001-user-auth`)
- Constitution compliance checked: plugin structure, versioning, logging
- Documentation updated if patterns changed (see Documentation Maintenance section)
- Database migrations reviewed by DBA or senior engineer
- Breaking changes require explicit approval and migration guide
- Code follows patterns from `docs/DEVELOPMENT_GUIDE.md` section "Code Review Checklist"

### Git Workflow

**Branch Naming:**
- Features: `speckit-dev` or `feature/###-feature-name`
- Hotfixes: `hotfix/description`
- Releases: `release/vX.Y.Z`

**Commit Standards:**
- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Reference tasks: `feat: implement user login API (T042)`
- Co-authored commits with Claude: `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`

## Governance

### Constitution Authority

This constitution supersedes all other development practices, conventions, and tribal knowledge. When conflicts arise, constitution rules take precedence. Changes to this document require explicit rationale and stakeholder approval.

The constitution defines governance and principles ("why"). The technical documentation in `docs/` defines implementation patterns and workflows ("how"). Together they form the complete development framework.

### Amendment Process

**Minor amendments** (clarifications, examples, non-semantic changes):
- Proposed via pull request with justification
- Reviewed by 1-2 maintainers
- Merged after 48-hour review period
- Version: PATCH increment

**Major amendments** (new principles, removed principles, architectural changes):
- Proposed as RFC document with:
  - Problem statement
  - Proposed principle change
  - Impact analysis on existing code and templates
  - Migration plan for non-compliant code
  - Documentation update requirements
- Discussed in team meeting or async review (1 week minimum)
- Requires consensus or maintainer vote
- Version: MAJOR or MINOR increment
- Dependent templates updated atomically with amendment
- Technical documentation updated to reflect changes

### Compliance Reviews

**When required:**
- All feature specifications: Review against principles during planning phase
- Pull requests: Constitution check in review checklist
- Documentation changes: Verify alignment with constitutional principles
- Quarterly audits: Sample 5-10 recent features for compliance
- Pre-release: Constitution compliance gate before deployment

**Enforcement:**
- Non-compliant code flagged in code review with specific principle violation
- Complexity violations require explicit justification (see plan-template.md Complexity Tracking)
- Documentation drift flagged when code patterns diverge from documented examples
- Repeated violations trigger architecture review and team discussion

### Living Document

This constitution evolves with the project. As new patterns emerge or constraints change, principles adapt. However, stability is valued: frequent changes signal poor initial design. Aim for amendments no more than quarterly unless critical issues arise.

When patterns evolve significantly, both constitution and documentation update together:
1. Constitution updated for principle changes
2. Documentation updated for pattern changes
3. Templates updated for new workflows
4. Existing code assessed for migration needs

### Development Guidance

Runtime development guidance for AI agents and developers is maintained in:
- **This constitution**: Architectural principles and governance
- **Technical documentation** (`docs/`): Implementation patterns and workflows
- **Generated agent files** (`.specify/templates/agent-file-template.md`): Technology-specific conventions from feature plans

**Hierarchy:**
1. Constitution (highest authority): Non-negotiable principles and governance
2. Technical Documentation: Mandatory patterns and best practices
3. Generated Agent Files: Project-specific conventions and active technologies

Refer to the agent file for technology-specific conventions; refer to technical documentation for implementation patterns; refer to this constitution for architectural principles and governance.

**Version**: 1.2.0 | **Ratified**: 2026-02-09 | **Last Amended**: 2026-02-09

# Quarterly Constitution Review Checklist

Review and update the constitution every quarter to capture institutional knowledge and adapt to emerging patterns.

**Current Constitution Version**: 1.1.0
**Last Quarterly Review**: 2026-02-09 (Initial creation)
**Next Scheduled Review**: 2026-05-09 (Q2 2026)

---

## Review Schedule

- **Q1**: January-March → Review in early April
- **Q2**: April-June → Review in early July
- **Q3**: July-September → Review in early October
- **Q4**: October-December → Review in early January

Set calendar reminders for the first week of each review month.

---

## Pre-Review Preparation

### 1. Gather Data Sources

**Code Review Records** (Last Quarter):
```bash
# Count PRs merged last quarter
git log --since="3 months ago" --pretty=format:"%s" --grep="Merge pull request" | wc -l

# Review PR descriptions for constitution violations
git log --since="3 months ago" --grep="constitution" -i --oneline
```

**Lessons Learned File**:
```bash
# Review pending amendments
cat .specify/memory/lessons-learned.md | grep -A 20 "## Pending Amendments"

# Count pending items
grep -c "^### " .specify/memory/lessons-learned.md
```

**Bug/Issue Patterns**:
```bash
# Check GitHub issues for repeated problems
gh issue list --search "label:bug" --state closed --limit 50

# Search for keywords: "forgot", "missed", "unclear", "confused"
gh issue list --search "forgot OR unclear OR confused" --state closed
```

**Recent Incidents**:
- Production issues caused by missing governance
- Security vulnerabilities from missing constraints
- Performance problems from missing guidelines
- Integration failures from unclear contracts

### 2. Team Input Collection

Send questionnaire to team (1 week before review):

```markdown
## Quarterly Constitution Review - Team Input

Please respond with issues you encountered this quarter:

1. **Principle Clarity**: Which principles were confusing or unclear?
2. **Missing Guidance**: What situations lacked constitutional guidance?
3. **Repeated Mistakes**: What errors happened multiple times?
4. **New Patterns**: What new patterns emerged that should be standardized?
5. **Tech Stack Changes**: Any technology changes affecting principles?
6. **Process Gaps**: What process improvements are needed?

Submit responses to: [lessons-learned.md or team discussion]
```

---

## Review Checklist

### Phase 1: Analyze Accumulated Lessons

- [ ] **Read all pending lessons** in `lessons-learned.md`
- [ ] **Count by principle**: Which principles have most lessons?
- [ ] **Count by priority**: How many High/Medium/Low priority items?
- [ ] **Identify patterns**: Are similar lessons repeating?
- [ ] **Check dates**: How old are the oldest pending lessons?

**Output**: Summary table

| Principle | # Lessons | High Priority | Common Theme |
|-----------|-----------|---------------|--------------|
| I. Plugin-First | 3 | 2 | Dependency issues |
| IV. Database Migration | 5 | 3 | Schema switching forgotten |
| ... | ... | ... | ... |

### Phase 2: Review Compliance Violations

- [ ] **PR review feedback**: What constitution violations were caught in code review?
- [ ] **Audit results**: Any compliance issues from quarterly audits?
- [ ] **Documentation drift**: Do docs match current principles?
- [ ] **Template drift**: Do templates align with constitution?

**Check these files**:
- [ ] `docs/ARCHITECTURE.md` - Matches constitution technology stack?
- [ ] `docs/PLUGIN_SYSTEM.md` - Matches Principle I (Plugin-First)?
- [ ] `docs/FRONTEND_BACKEND.md` - Matches Principle II (Contracts)?
- [ ] `docs/DEVELOPMENT_GUIDE.md` - Matches testing/debugging principles?
- [ ] `.specify/templates/plan-template.md` - Constitution Check section current?
- [ ] `.specify/templates/spec-template.md` - Requirements align with principles?
- [ ] `.specify/templates/tasks-template.md` - Task structure matches principles?

### Phase 3: Identify New Patterns

- [ ] **Code patterns**: New architectural patterns emerged?
- [ ] **Testing patterns**: New testing strategies adopted?
- [ ] **Security patterns**: New security requirements discovered?
- [ ] **Performance patterns**: New performance constraints identified?
- [ ] **Integration patterns**: New integration approaches standardized?

**Questions to ask**:
- Did we adopt any new libraries/frameworks?
- Did we discover any anti-patterns?
- Did we create any new shared utilities?
- Did we change any deployment processes?

### Phase 4: Technology Stack Review

- [ ] **Language versions**: Any upgrades? (e.g., Python 3.10 → 3.11)
- [ ] **Framework versions**: Any upgrades? (e.g., Flask, Vue.js)
- [ ] **Database versions**: Any upgrades? (e.g., PostgreSQL 14 → 15)
- [ ] **Infrastructure changes**: Docker, Kubernetes, cloud services?
- [ ] **Tool changes**: CI/CD, monitoring, logging?

**Update constitution section**: "Technology Stack" if changes occurred

### Phase 5: Principle Effectiveness Review

For each of the 7 core principles, assess:

**I. Plugin-First Architecture**
- [ ] How many features followed this principle?
- [ ] How many violations occurred?
- [ ] Is the principle still correct?
- [ ] Does it need clarification or expansion?
- [ ] Should examples be added?

**II. Contract-Based Integration**
- [ ] Are API/RPC patterns being followed?
- [ ] Were there contract breaking changes?
- [ ] Is versioning discipline working?
- [ ] Need more specific guidelines?

**III. Test-First for Critical Paths**
- [ ] Are teams writing tests first?
- [ ] What's the test coverage trend?
- [ ] Are integration tests effective?
- [ ] Should testing be mandatory (not just recommended)?

**IV. Database Migration Discipline**
- [ ] Were migrations reversible?
- [ ] Any schema errors in production?
- [ ] Is multi-tenant isolation working?
- [ ] Schema switching being used consistently?

**V. Observability & Debugging**
- [ ] Are logs providing useful information?
- [ ] Can we debug issues effectively?
- [ ] Are correlation IDs being used?
- [ ] Is structured logging working?

**VI. Versioning & Breaking Changes**
- [ ] Is semantic versioning being followed?
- [ ] Were breaking changes handled properly?
- [ ] Is dependency management working?
- [ ] Need stricter version policies?

**VII. Simplicity & YAGNI**
- [ ] Are implementations staying simple?
- [ ] Any over-engineering incidents?
- [ ] Are abstractions appropriate?
- [ ] Need stronger guidance on complexity?

### Phase 6: Determine Amendment Type

For each issue identified, classify:

**MAJOR** (v1.X.Y → v2.0.0):
- [ ] Remove a core principle
- [ ] Fundamentally redefine a principle
- [ ] Breaking change to governance process
- [ ] Incompatible with previous version

**MINOR** (vX.1.Y → vX.2.0):
- [ ] Add new principle (VIII, IX, etc.)
- [ ] Significantly expand existing principle
- [ ] Add new section (e.g., "Performance Standards")
- [ ] Material guidance additions

**PATCH** (vX.Y.1 → vX.Y.2):
- [ ] Clarify existing wording
- [ ] Add examples to principles
- [ ] Fix typos or formatting
- [ ] Update documentation references

---

## Conducting the Review

### Step 1: Prepare Amendment Proposals

For each change, prepare:

```markdown
## Amendment Proposal [N]

**Principle**: [Which principle]
**Change Type**: [MAJOR/MINOR/PATCH]
**Root Cause**: [Why needed - reference lessons learned]
**Proposed Change**: [Specific text changes]
**Impact**: [Which templates/docs affected]
**Priority**: [High/Medium/Low]
```

### Step 2: Run Batch Amendment

Use `/speckit.amend` for each amendment or batch them:

```bash
# Individual amendments
/speckit.amend "Proposal 1: [details]"
/speckit.amend "Proposal 2: [details]"

# Batch amendment (for multiple PATCH changes)
/speckit.amend "Quarterly Q1 2026 review amendments:
1. Principle IV - Emphasize schema switching (3 incidents)
2. Principle V - Add correlation ID examples (2 incidents)
3. Principle VII - Add complexity justification threshold (5 incidents)
4. Technology Stack - Update PostgreSQL 14 → 15"
```

**Approval Process**:
- Each amendment will show proposed changes
- Review carefully before approving
- Team discussion for MAJOR/MINOR changes
- Single approver OK for PATCH changes

### Step 3: Update Documentation

After constitution updated:

```bash
# Check which docs need updates
ls docs/*.md

# Update each affected doc
# - ARCHITECTURE.md - Tech stack changes
# - PLUGIN_SYSTEM.md - Principle I changes
# - FRONTEND_BACKEND.md - Principle II, IV changes
# - DEVELOPMENT_GUIDE.md - Principle III, V changes

# Commit all together
git add .specify/memory/constitution.md docs/*.md
git commit -m "docs: quarterly constitution review Q1 2026 (v1.X.Y)"
```

### Step 4: Update Templates

Check and update if needed:

```bash
# Review templates
cat .specify/templates/plan-template.md | grep "Constitution Check"
cat .specify/templates/spec-template.md | head -50
cat .specify/templates/tasks-template.md | head -50

# Update if changes affect them
# Commit separately or with constitution
```

---

## Post-Review Actions

### 1. Archive Lessons Learned

- [ ] Move all applied lessons from "Pending" to "Archived" section
- [ ] Add amendment version numbers to archived lessons
- [ ] Commit updated `lessons-learned.md`

### 2. Communication

Announce constitutional changes to team:

```markdown
## Constitution Updated - Q1 2026 Review

**Version**: 1.X.Y → 1.Y.Z
**Changes**: [Summary]

**Key Updates**:
1. [Principle change 1]
2. [Principle change 2]
3. [Principle change 3]

**Action Required**:
- Review updated constitution: `.specify/memory/constitution.md`
- Check updated documentation: `docs/`
- Update any in-progress work to comply with new principles

**Questions?** Contact [constitution maintainer]
```

### 3. Update This Checklist

- [ ] Update "Last Quarterly Review" date at top
- [ ] Set "Next Scheduled Review" date
- [ ] Add any lessons learned about the review process itself
- [ ] Commit updated checklist

### 4. Schedule Next Review

- [ ] Add calendar event for next quarter
- [ ] Assign review owner for next quarter
- [ ] Set reminder 1 week before to send team questionnaire

---

## Review Metrics

Track over time to measure constitutional effectiveness:

| Quarter | Version Change | # Amendments | # Lessons Applied | MAJOR/MINOR/PATCH |
|---------|----------------|--------------|-------------------|-------------------|
| Q1 2026 | 1.1.0 → 1.2.0  | 5            | 12                | 0 / 1 / 4         |
| Q2 2026 | 1.2.0 → 1.2.1  | 2            | 5                 | 0 / 0 / 2         |
| Q3 2026 | 1.2.1 → 1.3.0  | 7            | 15                | 0 / 1 / 6         |

**Health Indicators**:
- ✅ **Good**: PATCH-only changes (stable principles)
- ⚠️ **Watch**: Frequent MINOR changes (principles evolving)
- 🚨 **Concern**: MAJOR changes (fundamental issues)

**Trend Analysis**:
- Are lessons decreasing over time? (Constitution improving)
- Are same principles getting repeated lessons? (Principle unclear)
- Are lessons being applied timely? (Process working)

---

## Quick Reference

**Files to Review**:
```
.specify/memory/constitution.md      # Main document
.specify/memory/lessons-learned.md   # Pending changes
.specify/templates/*.md              # Template alignment
docs/*.md                             # Documentation alignment
```

**Commands to Use**:
```bash
/speckit.amend "[lesson learned details]"  # Apply single amendment
/speckit.constitution                       # Manual full update
```

**Review Duration**: Plan for 2-4 hours quarterly
**Review Participants**: Constitution owner + 2-3 senior team members
**Decision Authority**: Team consensus for MAJOR/MINOR, owner for PATCH

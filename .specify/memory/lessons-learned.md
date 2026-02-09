# Lessons Learned & Constitution Amendments

Track issues, improvements, and lessons learned during development. Review quarterly to update constitution.

## Template

```markdown
### [Date] - [Feature/Issue]
**Context**: What were you working on?
**Problem**: What went wrong or could be improved?
**Root Cause**: Why did it happen?
**Proposed Amendment**: Which principle/section needs updating?
**Priority**: High/Medium/Low
```

---

## Pending Amendments

<!-- Add new lessons here -->

---

## Archived (Applied to Constitution)

### 2026-02-09 - UI Performance Quality Gate Metrics Enhancement - Branch Strategy
**Context**: Implementing changes to ui_performance plugin - attempted to create feature branch in main Centry repository during implementation workflow

**Problem**:
1. Created feature branch `001-ui-quality-gate-metrics` in the main Centry repository ❌
2. Should have stayed on `speckit-dev` branch in Centry repo ✅
3. Feature branch should ONLY exist in plugin repository (`pylon/plugins/ui_performance/`) ✅

**Root Cause**:
- Constitution didn't explicitly state Centry repo branch workflow
- CRITICAL RULE NOT DOCUMENTED: Centry repo ALWAYS stays on `speckit-dev` branch for all speckit work
- Plugin repositories are separate Git repos with independent branching
- Task breakdown (T001) didn't specify this two-repository workflow

**Amendment Applied**: Constitution v1.1.0 → v1.2.0

**Changes**:
- Added "Branch Strategy for Plugin Development" section to Principle I (Plugin-First Architecture)
- Documented dual-repository model: Centry on `speckit-dev` (stable), plugins on feature branches (independent)
- Specified workflow rules: verify Centry branch before implementation, create feature branches only in plugin repos
- Flagged templates for update: tasks-template.md (T001), speckit.implement.md (branch validation)

**Impact**: CRITICAL - Prevents repository confusion, incorrect branch creation, and manual cleanup. Establishes fundamental workflow rule for all plugin development.

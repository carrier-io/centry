---
description: Amend the constitution based on lessons learned during development with user approval required before applying changes.
handoffs:
  - label: Review Constitution
    agent: speckit.constitution
    prompt: Review the full updated constitution
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are helping the user amend the project constitution at `.specify/memory/constitution.md` based on lessons learned during development. This command provides a streamlined workflow for capturing institutional knowledge and improving governance.

**CRITICAL**: All constitutional amendments require **explicit user approval** before being applied. You MUST present proposed changes and wait for user confirmation.

Follow this execution flow:

### Phase 1: Analyze Lesson Learned

1. **Parse user input** to understand the lesson:
   - What problem or confusion occurred?
   - Which principle(s) are affected?
   - What improvement is proposed?
   - What priority level? (High/Medium/Low)

2. **Read current constitution** at `.specify/memory/constitution.md`:
   - Identify which principle(s) need updating
   - Determine if this is a MAJOR/MINOR/PATCH change:
     - **MAJOR**: Principle removal, complete redefinition, breaking change
     - **MINOR**: New principle added, significant expansion of existing principle
     - **PATCH**: Clarification, example added, wording improvement
   - Check current version number

3. **Read lessons-learned.md** at `.specify/memory/lessons-learned.md`:
   - Check if similar lesson already documented
   - Prepare to archive this lesson after applying

### Phase 2: Propose Amendment (WAIT FOR APPROVAL)

4. **Present proposed changes to user**:

   Format your proposal exactly like this:

   ```markdown
   ## Proposed Constitutional Amendment

   **Current Version**: X.Y.Z
   **New Version**: X.Y.Z+1
   **Bump Type**: [MAJOR/MINOR/PATCH]
   **Rationale**: [Why this version bump]

   ### Changes Proposed:

   **Principle [Roman Numeral]: [Principle Name]**
   - Change: [What will be added/modified/removed]
   - Before: [Current text if modifying]
   - After: [New text]
   - Reason: [Why this change addresses the lesson learned]

   [Repeat for each affected principle/section]

   ### Impact:
   - Templates affected: [List .specify/templates/*.md files that may need updates]
   - Documentation affected: [List docs/*.md files that may need updates]

   ---

   **Do you approve these changes?** (Reply "yes" to proceed, "no" to cancel, or provide feedback for revision)
   ```

5. **STOP and WAIT** for user response:
   - If user says **"yes"** or **"approve"** or **"proceed"**: Continue to Phase 3
   - If user says **"no"** or **"cancel"**: Stop and explain how to refine the proposal
   - If user provides **feedback**: Revise the proposal and present again
   - **DO NOT PROCEED** without explicit approval

### Phase 3: Apply Amendment (Only After Approval)

6. **Update constitution**:
   - Read current `.specify/memory/constitution.md`
   - Apply the approved changes
   - Increment version number according to bump type
   - Update `LAST_AMENDED_DATE` to today (ISO format: YYYY-MM-DD)
   - Add Sync Impact Report as HTML comment at top:
     ```html
     <!--
     Sync Impact Report:
     Version: X.Y.Z → X.Y.Z+1 (Amendment via /speckit.amend)
     Modified Principles: [List]
     Added Sections: [List or N/A]
     Removed Sections: [List or N/A]
     Reason: [User's lesson learned summary]
     Templates Status:
       ✅/⚠️ [template file] - [status]
     -->
     ```
   - Write updated constitution back to `.specify/memory/constitution.md`

7. **Archive lesson learned**:
   - Read `.specify/memory/lessons-learned.md`
   - Format the lesson:
     ```markdown
     ### [TODAY's DATE] - [Brief Description]
     **Context**: [What the user was working on]
     **Problem**: [What went wrong or was unclear]
     **Root Cause**: [Why it happened]
     **Amendment Applied**: Constitution v[OLD] → v[NEW]
     **Changes**: [Brief summary of changes]
     ```
   - Move to "Archived (Applied to Constitution)" section
   - Write updated lessons-learned.md back

8. **Check template consistency**:
   - Read `.specify/templates/plan-template.md` → Check "Constitution Check" section aligns
   - Read `.specify/templates/spec-template.md` → Check requirements align
   - Read `.specify/templates/tasks-template.md` → Check task structure aligns
   - Report which templates may need manual updates (flag with ⚠️)

9. **Provide completion summary**:
   ```markdown
   ## Constitutional Amendment Applied ✅

   **Version**: X.Y.Z → X.Y.Z+1
   **Changes Applied**:
   - [Summary of changes]

   **Lesson Archived**: `.specify/memory/lessons-learned.md` updated

   **Templates Reviewed**:
   - ✅ plan-template.md - No changes needed
   - ⚠️ spec-template.md - May need manual review (reason)

   **Suggested Commit Message**:
   ```
   docs: amend constitution to vX.Y.Z+1 ([change summary])

   [Detailed commit message based on changes]

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
   ```

   **Next Steps**:
   - Review the updated constitution: `.specify/memory/constitution.md`
   - Commit the changes if satisfied
   - Update any flagged templates if needed
   ```

## Special Cases

### Multiple Lessons at Once

If user provides multiple lessons (e.g., batch update), group them by principle and present a consolidated amendment proposal.

### Unclear Lesson

If the lesson learned is ambiguous:
1. Ask clarifying questions:
   - Which principle is affected?
   - Is this a clarification or new requirement?
   - What specific text should be added/changed?
2. Wait for user response before proceeding

### Principle Not Found

If the lesson doesn't fit any existing principle:
1. Propose creating a new principle (MINOR bump)
2. Suggest alternative: Expand existing related principle
3. Wait for user decision

### Template Updates Required

If templates clearly need updates based on amendment:
1. Flag them in the proposal with ⚠️
2. After amendment applied, ask: "Would you like me to update [template] now to align with the new principle?"
3. Only update if user approves

## Best Practices

**DO**:
- Always wait for explicit user approval before modifying constitution
- Present clear before/after comparisons
- Explain version bump rationale
- Archive lessons after applying
- Suggest commit messages

**DON'T**:
- Proceed without user approval
- Make assumptions about which principle to update
- Skip template consistency checks
- Forget to update lessons-learned.md
- Apply changes that contradict existing principles without user discussion

## Example Usage

**User Input**:
```
/speckit.amend "We forgot to use schema switching in 3 plugins this sprint.
Database queries failed in multi-tenant scenarios. Need to emphasize this in
the Database Migration principle."
```

**Your Response**:
```markdown
## Proposed Constitutional Amendment

**Current Version**: 1.1.0
**New Version**: 1.1.1
**Bump Type**: PATCH
**Rationale**: Clarification of existing principle with emphasis on critical requirement

### Changes Proposed:

**Principle IV: Database Migration Discipline**
- Change: Add emphasis box on multi-tenant schema switching
- After:
  ```
  **CRITICAL for Multi-Tenant Queries**: All database queries accessing
  tenant-specific data MUST be wrapped with schema switching:

  ```python
  with db.with_project_schema_session(project_id):
      items = MyModel.query.all()
  ```

  Failure to use schema switching will cause queries to run against the
  wrong tenant's data or fail entirely.
  ```
- Location: Add after "Non-negotiable rules" section, before "Rationale"
- Reason: Repeated mistakes (3 incidents this sprint) show this critical
  requirement needs stronger emphasis

**Resources Section** (Principle IV):
- Change: Add to existing resources list
- After: "⚠️ CRITICAL: Always wrap tenant queries with `with_project_schema_session()` -
  see docs/FRONTEND_BACKEND.md section 'Multi-Tenant Schema Switching'"

### Impact:
- Templates affected: None (implementation detail, not planning requirement)
- Documentation affected: None (docs already cover this, just emphasizing in constitution)

---

**Do you approve these changes?**
```

[Wait for user approval before proceeding]

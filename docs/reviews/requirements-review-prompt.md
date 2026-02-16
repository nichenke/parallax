# Requirements Review Subagent Prompt (v2)

**Task:** Review the requirements document for parallax:review after v1 review changes were applied. Validate fixes and surface remaining issues.

1. **Format & Style Quality** (re-evaluate after fixes)
2. **JTBD Effectiveness** (new section added — does it work?)
3. **Declarative Quality** (ADR separation done — is the doc now properly declarative?)
4. **Remaining Issues** (anything the v1 review missed or that the fixes introduced)

---

## Context

**Document to review:** `docs/requirements/parallax-review-requirements-v1.md`
**Decision log:** `docs/requirements/adr-001-requirements-v1-resolutions.md`
**Problem statement:** `docs/problem-statements/design-orchestrator.md`

**Background:**
- Requirements doc for a multi-agent adversarial design review skill
- v1 review completed, findings applied:
  - JTBD section added (5 jobs mapped to requirement categories)
  - Q1-Q8 resolutions extracted to ADR-001 (requirements are now declarative)
  - FR2.7/FR2.7.1 consolidated, FR6 deduplicated (53→48 FRs)
  - Inferred requirements marked as "Design assumption"
  - Implementation details removed from NFR2.4
- Current status: Draft v1.2 (Post-Review)

**v1 review findings that were applied:**
- Format: Redundancy in FR2.7/FR2.7.1, FR6.2/FR6.7 duplication, NFR2.4 over-specification
- JTBD: No outcomes section existed, 10% of requirements weakly traceable
- Necessity: Keep doc, but separate decision rationale from declarative requirements

---

## Review Focus Areas

### 1. Format & Style (Re-Evaluation)

**v1 found 5 issues. Verify fixes:**
- FR2.7/FR2.7.1 consolidation — is the merged requirement clear?
- FR6 reorder/dedup — is the new grouping logical? Any information lost?
- NFR2.4 cleanup — does the outcome statement still capture the requirement?
- Inferred requirements (NFR1.1, NFR1.2, C1.4) — are "Design assumption" labels clear?
- Decision Log section — does the summary table + ADR link work?

**Also evaluate (fresh eyes):**
- Are requirements atomic and testable?
- Is traceability (source citations) helpful or cluttered?
- Any NEW redundancy or ambiguity introduced by the edits?

---

### 2. JTBD Effectiveness

**The new JTBD section maps 5 pain points to requirement categories.**

**Evaluate:**
1. Do the 5 jobs cover the full scope of the requirements? (Any FRs/NFRs orphaned from a job?)
2. Is the pain→solution→requirements mapping convincing?
3. Does the "User outcome" summary line capture the value proposition?
4. Can you trace EACH requirement back to at least one job? (List any orphans)
5. Are the jobs themselves well-scoped? (Too broad? Too narrow? Overlapping?)

**Key test:** Read only the JTBD section. Could someone understand what this skill does and why, without reading the full requirements?

---

### 3. Declarative Quality

**Q1-Q8 resolutions were extracted to ADR-001. The requirements doc should now be declarative (WHAT, not WHY-WE-DECIDED-THIS).**

**Evaluate the requirements doc:**
1. Does it read as "what to build" without decision archaeology?
2. Are there still references to Q-resolutions or session history that belong in the ADR?
3. Is the Decision Log section (summary table + ADR link) the right level of cross-reference?
4. Do Source citations still reference MEMORY.md or session-specific context? (These should point to design docs or ADR)

**Evaluate the ADR:**
1. Is the ADR format clear? (Question → Alternatives → Decision → Rationale → Impact)
2. Does the Consequences section accurately capture what was added/removed?
3. Are there any decisions in the ADR that should be promoted to the requirements doc as constraints?

---

### 4. Remaining Issues

**Look for anything the v1 review missed:**
- Requirements that contradict each other
- Requirements that duplicate constraints or design doc content
- Missing acceptance criteria (how would you test this requirement?)
- Scope creep signals (requirements that don't serve any JTBD job)
- NFR5/NFR6 meta-requirements: are these properly distinguished from user-facing requirements?

---

## Output Format

**Produce 4 sections:**

### 1. Fix Verification
- For each v1 finding: Confirmed Fixed | Partially Fixed | Regression
- Any information lost in the edits?

### 2. JTBD Assessment
- Coverage: % of requirements mapped to a job
- Orphaned requirements (not served by any job)
- Job quality: Well-scoped | Too broad | Too narrow | Overlapping
- Standalone readability: Can JTBD section stand alone? (Yes/No)

### 3. Declarative Quality
- Requirements doc: Declarative | Still has decision archaeology | Mixed
- ADR quality: Clear | Needs work
- Cross-reference level: Right | Too much | Too little

### 4. Remaining Issues
- List as: [Severity: Critical|Important|Minor] Description
- Include requirement ID where applicable
- Suggest fix for each

---

## Success Criteria

Your review helps answer:
1. **Fixes:** Did the v1 review changes actually improve the doc?
2. **JTBD:** Does the new section effectively anchor requirements to user needs?
3. **Separation:** Is the requirements/ADR split clean?
4. **Gaps:** What still needs work before this doc is implementation-ready?

Output should be concise, evidence-based, and actionable. ~1500-2000 words.

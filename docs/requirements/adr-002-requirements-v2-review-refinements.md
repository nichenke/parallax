# ADR-002: parallax:review Requirements v1.2 — v2 Review Refinements

**Date:** 2026-02-16
**Status:** Accepted
**Deciders:** @nichenke

---

## Context

After applying v1 review findings (JTBD section, ADR separation, format consolidation), a v2 review was conducted to validate fixes and surface remaining issues. The v1 fixes were confirmed with no information loss. The v2 review identified 8 refinements (2 Critical, 3 Important, 3 Minor) to improve clarity, scope accuracy, and implementation readiness.

---

## Decision 1: Pattern Extraction in Critical Path (FR10.3/FR10.4)

**Question:** Should pattern extraction run asynchronously after synthesis, or in the critical path before finding processing?

**Alternatives:**
- (a) Async post-synthesis — user sees summary first, pattern extraction happens later
- (b) In critical path — extraction completes before user sees findings
- (c) Hybrid — in critical path with complexity threshold for skipping interactive processing

**Decision:** Option (c). Pattern extraction runs in critical path (after synthesis, before finding processing). Reviews with >50 findings skip interactive processing but still output pattern artifacts.

**Rationale:**
- Pattern analysis is part of the review output, not a side channel
- Async-first principle means artifacts always go to disk
- 50-finding threshold balances interactive feasibility with generous MVP scope
- Interactive processing of 50+ findings is impractical in-session

**Requirements impact:**
- Updated FR10.3: Pattern extraction in critical path (was: "not in critical path")
- Updated FR10.4: Changed threshold from 15 patterns to 50 findings, clarified interactive skip behavior

---

## Decision 2: JSONL Schema as Implementation Dependency (FR7.5)

**Question:** How should we handle the fact that FR7.5 requires schema validation but the schema isn't yet defined?

**Alternatives:**
- (a) Define schema inline in requirements doc (add FR6.1.1)
- (b) Acknowledge dependency and defer schema to separate task
- (c) Remove FR7.5 until schema exists

**Decision:** Option (b). Add dependency note to FR7.5, reference Next Steps #5 (JSONL schema implementation).

**Rationale:**
- Schema validation is a legitimate requirement
- Schema design is its own task (not a one-line requirement)
- Already tracked in Next Steps — dependency note makes the blocker explicit
- Premature to define schema structure before implementation prototyping

**Requirements impact:**
- Added dependency note to FR7.5: "Blocked on JSONL schema definition (Next Steps #5)"

---

## Decision 3: Systemic Detection Denominator Rationale (FR2.7)

**Question:** Why does systemic detection use only findings with `contributing_phase` set as the denominator, not all findings?

**Decision:** Add explicit rationale to FR2.7.

**Rationale:**
- Systemic issues indicate upstream root causes (contributing phase), not immediate symptoms (primary phase)
- A design flaw (primary) caused by a calibrate gap (contributing) signals a systemic calibrate problem
- Findings without a contributing phase are isolated to their primary phase — not systemic

**Requirements impact:**
- Added rationale to FR2.7 denominator line

---

## Decision 4: Developer Requirements Separation (NFR5/NFR6)

**Question:** Should eval reproducibility (NFR5) and eval testing (NFR6) be labeled differently from user-facing non-functional requirements?

**Alternatives:**
- (a) Add clarifying note inline
- (b) Move to separate "Developer Requirements (Skill QA)" section
- (c) Leave as-is — they're still non-functional requirements

**Decision:** Option (b). Create "Developer Requirements (Skill Quality Assurance)" section with preamble explaining these are not user-facing features.

**Rationale:**
- Previous confusion between production and eval requirements (Session 10 build-vs-leverage spike)
- NFR5/NFR6 serve skill developers (eval testing, prompt iteration), not skill users (design review)
- Users benefit indirectly via improved review quality
- Grouping related concerns improves navigability

**Requirements impact:**
- Created new section: "Developer Requirements (Skill Quality Assurance)"
- Moved NFR5 (7 requirements) and NFR6 (3 requirements) under new section
- Added preamble: "These requirements support skill development, testing, and iterative improvement. They are not user-facing features — users benefit indirectly via improved review quality."

---

## Decision 5: Document Source Scope Clarification (C1.3)

**Question:** C1.3 states reviewers access documents via Read/WebFetch tools, supporting "Confluence, Google Docs, Notion." But WebFetch doesn't support authenticated sources. What's the MVP scope?

**Alternatives:**
- (a) Add C1.3.1 constraint: authenticated sources require manual export to local files
- (b) Revise C1.3 to scope MVP accurately: local/public URLs only, defer auth sources to MCP
- (c) Leave as-is — assume future MCP support makes the constraint temporary

**Decision:** Option (b). Revise C1.3 to state MVP scope (local files, public URLs), reference D6 (MCP integration) for authenticated sources. Skip manual export workflow — go straight to MCP when needed.

**Rationale:**
- WebFetch does not support authenticated sessions (cookies, OAuth, API tokens)
- Manual export adds friction without long-term value
- MCP connectors are the correct solution for authenticated sources (already deferred to D6)
- C1.3 should accurately describe MVP capabilities, not overpromise

**Requirements impact:**
- Updated C1.3: "Design docs accessible via local file paths or public URLs (MVP scope)"
- Added MVP scope note: "Local files and public URLs only. Authenticated sources (Confluence, Google Docs, Notion) deferred to MCP integration (see D6)"

---

## Decision 6: Git Diff Availability Definition (FR8.4)

**Question:** FR8.4 says "highlight changed sections (git diff) when available" — what does "when available" mean?

**Decision:** Clarify that "when available" means git repo exists AND design doc has prior committed version.

**Rationale:**
- Removes ambiguity for implementers
- Makes edge case behavior explicit (first-time review → no diff highlighting)

**Requirements impact:**
- Added clarification to FR8.4: "When available: Git repo exists AND design doc has prior committed version. First-time review → no diff highlighting."

---

## Decision 7: Job 5 Outcome Specificity (JTBD Section)

**Question:** Job 5 outcome says "Get adversarial design review in <5 minutes" — but this is the overall skill outcome, not the Job 5-specific outcome.

**Decision:** Revise Job 5 outcome to: "Track review cost and quality metrics to iteratively improve reviewer effectiveness."

**Rationale:**
- Job 5 is about eval/improvement, not review delivery
- Outcome should reflect the specific job's value proposition
- Overall skill outcome is stated separately (line 38)

**Requirements impact:**
- Updated Job 5 outcome line

---

## Decision 8: Acceptance Criteria as Separate Task

**Question:** Many requirements lack explicit acceptance criteria (FR1.2 "non-overlapping blind spots", FR2.2 "deduplicate similar", NFR1.1 "5 minutes"). Should we add them now?

**Alternatives:**
- (a) Add acceptance criteria to 5-10 critical requirements inline
- (b) Defer to Next Steps as separate task
- (c) Reject as out of scope (belongs in test plan, not requirements)

**Decision:** Option (b). Add "Define acceptance criteria" to Next Steps.

**Rationale:**
- Requirements are testable in principle — criteria just need to be made explicit
- Adding criteria to 5-10 requirements is substantial work (separate task)
- Requirements doc is implementation-ready without criteria (criteria improve testability but don't block implementation)

**Requirements impact:**
- Added Next Steps #3: "Define acceptance criteria — Add explicit testability criteria to critical requirements (FR1.2, FR2.2, FR2.7, FR3.2, NFR1.1, 5-10 total)"

---

## Consequences

### Requirements Updated (by decision)

| Decision | Requirements Updated |
|----------|---------------------|
| D1 | FR10.3 (critical path), FR10.4 (50-finding threshold) |
| D2 | FR7.5 (dependency note) |
| D3 | FR2.7 (denominator rationale) |
| D4 | NFR5/NFR6 (new section: Developer Requirements) |
| D5 | C1.3 (MVP scope: local/public URLs) |
| D6 | FR8.4 (git diff availability definition) |
| D7 | Job 5 outcome (eval-specific) |
| D8 | Next Steps #3 (acceptance criteria task added) |

### Version Progression

- v1.0 (Session 10): Initial requirements with Q1-Q8 embedded
- v1.1 (Session 10): Q1-Q8 resolutions integrated
- v1.2 (Session 11): v1 review fixes applied (JTBD, ADR separation, format consolidation)
- v1.2 (Session 11): v2 review refinements applied (this ADR)

### Implementation Readiness

After v2 refinements, requirements doc is implementation-ready for MVP with two acknowledged blockers:
1. JSONL schema definition (Next Steps #5, blocks FR7.5)
2. Acceptance criteria specification (Next Steps #3, improves testability but does not block implementation)

All critical ambiguities resolved. Developer vs user-facing requirements clearly separated.

# Pattern Extraction Prototype Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Validate pattern-based systemic detection by extracting semantic patterns from v3 review sample findings.

**Architecture:** Skill-driven workflow using Claude Code native tools (Read/Write). No external dependencies. Sample JSONL creation → pattern extraction → schema validation.

**Tech Stack:** Claude Code CLI, JSONL, JSON Schema validation (existing Python script)

---

## Task 1: Create Sample JSONL - Part 1 (Assumption Hunter Findings)

**Files:**
- Create: `scripts/sample-findings-v3.jsonl`
- Read: `docs/reviews/parallax-review-v1/assumption-hunter.md`

**Step 1: Read Assumption Hunter findings**

Read the file to identify 3-4 findings to include (mix of Critical/Important).

**Step 2: Select representative findings**

Target findings:
- Finding 1 (Critical): Auto-fix assumes trivial classification
- Finding 2 (Critical): Git-based tracking assumes design in git
- Finding 3 (Critical): Stable finding IDs assume sections don't change
- Finding 5 (Important): Async-first assumes file system as SSOT

These cover auto-fix risks, assumption violations, and multi-machine concerns.

**Step 3: Convert first finding to JSONL**

Write the first finding to `scripts/sample-findings-v3.jsonl`:

```jsonl
{"type":"finding","id":"v3-assumption-hunter-001","title":"Auto-Fix Step Assumes It Can Correctly Identify Trivial Changes","severity":"Critical","phase":{"primary":"design","contributing":"calibrate"},"section":"Step 4: Auto-Fix","issue":"Design specifies auto-fix classifies findings as trivial and applies automatically. Assumes system can reliably distinguish trivial mechanical fixes from semantic changes. Example: broken internal link could be wrong file extension (trivial) or wrong target document (semantic). No validation mechanism beyond undefined conservative criteria.","why_it_matters":"Auto-fixes modify source files and commit changes automatically. Misclassified fix that changes meaning breaks design. If auto-fix runs before human review, user cannot reject bad auto-fixes—they're already applied and committed.","suggestion":"Add validation requirements: (1) Define conservative with concrete examples and exclusion criteria, (2) Require diffs for user approval before application, (3) Add rollback mechanism, (4) Defer auto-fix to post-human-processing."}
```

**Step 4: Commit first entry**

```bash
git add scripts/sample-findings-v3.jsonl
git commit -m "feat: start sample findings JSONL with assumption-hunter-001"
```

---

## Task 2: Add More Assumption Hunter Findings

**Files:**
- Modify: `scripts/sample-findings-v3.jsonl`

**Step 1: Add findings 2, 3, and 5**

Append to `scripts/sample-findings-v3.jsonl`:

```jsonl
{"type":"finding","id":"v3-assumption-hunter-002","title":"Git-Based Iteration Tracking Assumes Design Doc Lives in Git","severity":"Critical","phase":{"primary":"design","contributing":null},"section":"Output Artifacts, Cross-Iteration Finding Tracking","issue":"Design states iteration history tracked by git. Assumes design document being reviewed is git-tracked. If user reviews design doc outside repository (Google Doc exported to markdown, Confluence page, design from different repo), git diff fails. No fallback specified.","why_it_matters":"Requirements state this should be applicable to work contexts. Many teams use Confluence, Notion, or Google Docs for design documents, not git-tracked markdown. If parallax:review only works for git-tracked docs, excludes significant use cases. Cross-iteration tracking depends on git diff—without it, reviewers lose focus prioritization.","suggestion":"Add input validation checking whether design doc is git-tracked. If not: (1) Warn user that cross-iteration diff won't be available, (2) Fall back to file timestamp comparison or manual change notes, (3) Document git requirement as constraint, (4) Implement text-based diff as fallback."}
{"type":"finding","id":"v3-assumption-hunter-003","title":"Stable Finding IDs Assume Section Headings Don't Change","severity":"Critical","phase":{"primary":"design","contributing":null},"section":"Cross-Iteration Finding Tracking","issue":"Design specifies finding IDs as stable hash derived from section + issue content. Assumes design doc section headings remain stable across iterations. If designer refactors UX Flow into User Workflow and State Management between iterations, all findings anchored to UX Flow become orphaned. Hash-based IDs break when input text changes even if semantic content unchanged.","why_it_matters":"Section refactoring is normal during design iteration. Improving document structure shouldn't invalidate finding tracking. If implemented as designed, cross-iteration tracking will produce false negatives (findings marked resolved when section renamed) and false positives (findings marked new when actually rephrased).","suggestion":"Replace text-based hashing with semantic anchoring or LLM-based matching. Options: (1) Store section heading + offset position, fuzzy-match if heading changed, (2) Use LLM to semantically match findings, (3) Hybrid: hash as first pass, LLM disambiguation on miss, (4) Allow manual finding ID assignment for critical findings."}
{"type":"finding","id":"v3-assumption-hunter-005","title":"Async-First Architecture Assumes File System as Single Source of Truth","severity":"Important","phase":{"primary":"design","contributing":"calibrate"},"section":"UX Flow (async-first)","issue":"Design specifies review always writes artifacts to disk as baseline. Assumes all state lives in files under docs/reviews/<topic>/. If user runs review on machine A, processes findings on machine B (different clone), or collaborates with teammate, state diverges. File-based state requires all participants operate on same filesystem or rigorously sync via git. No synchronization mechanism specified.","why_it_matters":"Requirements emphasize applicable to work contexts and CLAUDE.md notes this repo may be worked on from multiple machines. File-based state doesn't handle distributed workflows without additional tooling. If two users process findings in parallel, last write wins—earlier dispositions silently lost.","suggestion":"Either (1) Document single-user, single-machine constraint explicitly as MVP limitation, (2) Add conflict detection (check if summary.md has uncommitted changes), (3) Require git commit after each disposition batch, (4) Evaluate external state management."}
```

**Step 2: Commit**

```bash
git add scripts/sample-findings-v3.jsonl
git commit -m "feat: add assumption-hunter findings 002, 003, 005 to sample"
```

---

## Task 3: Add Edge Case Prober Findings

**Files:**
- Modify: `scripts/sample-findings-v3.jsonl`
- Read: `docs/reviews/parallax-review-v1/edge-case-prober.md`

**Step 1: Select 3-4 Edge Case Prober findings**

Target findings covering edge cases and failure modes:
- Finding 1 (Critical): Hash brittleness on structure changes
- Finding 2 (Critical): Auto-fix re-review may loop
- Finding 3 (Critical): Partial completion breaks systemic detection
- Finding 4 (Critical): Severity range resolution creates false escalations

**Step 2: Add findings to JSONL**

Append to `scripts/sample-findings-v3.jsonl`:

```jsonl
{"type":"finding","id":"v3-edge-case-prober-001","title":"Cross-Iteration Matching Breaks When Design Structure Changes","severity":"Critical","phase":{"primary":"design","contributing":null},"section":"Cross-Iteration Finding Tracking","issue":"Design specifies stable finding IDs via hash of section + content. When designer refactors document structure (splits sections, renames headings, reorders content), hashes change. System treats structurally-relocated findings as resolved and creates duplicate new findings. Section-based anchoring fails when sections reorganize.","why_it_matters":"Major design iterations often involve restructuring for clarity. If cross-iteration tracking breaks on restructure, users lose history exactly when it's most valuable—during significant revision. False resolved signals mislead about progress. Duplicate new findings flood user with already-addressed issues.","suggestion":"Test with realistic structure change scenarios: section split, merge, rename, reorder. Implement semantic matching that survives structure changes. Consider content fingerprinting independent of section location, or LLM-based semantic equivalence checking."}
{"type":"finding","id":"v3-edge-case-prober-002","title":"Auto-Fix Re-Review Workflow May Loop Indefinitely","severity":"Critical","phase":{"primary":"design","contributing":null},"section":"Step 4: Auto-Fix","issue":"Design allows auto-fix to trigger re-review. If auto-fix produces changes that generate new findings requiring auto-fix, workflow loops. No termination condition specified. No iteration limit. No budget guard. Pathological case: auto-fix creates finding, re-review generates auto-fixable finding, infinite loop consuming API budget.","why_it_matters":"Infinite loops block workflow and burn budget. Even finite but excessive loops (10+ iterations) indicate design flaw. Without loop detection or iteration limits, user cannot safely enable auto-fix re-review feature. Must be addressed before auto-fix implementation.","suggestion":"Add termination conditions: (1) Maximum iteration limit (3-5 re-reviews), (2) Detect finding stability (stop if findings unchanged across iterations), (3) Budget guard (stop if cost exceeds threshold), (4) User approval before each re-review iteration."}
{"type":"finding","id":"v3-edge-case-prober-003","title":"Partial Reviewer Completion Corrupts Systemic Detection","severity":"Critical","phase":{"primary":"design","contributing":null},"section":"Systemic Issue Detection","issue":"Design allows 4/6 reviewers as minimum threshold for partial completion. Systemic detection counts findings by phase: if >30% share contributing phase, flag systemic issue. If 2 reviewers fail (especially if they'd flag underrepresented phases), detection percentages skew. Missing data biases results toward phases covered by completed reviewers.","why_it_matters":"Systemic detection drives escalation decisions. If partial results produce false positives (flag systemic when missing reviewers would have balanced), user escalates unnecessarily. If false negatives (don't flag systemic because missing reviewers would have pushed over threshold), user misses root cause. Partial data must not corrupt detection.","suggestion":"Options: (1) Disable systemic detection if any reviewer failed, (2) Require minimum diversity (at least one reviewer per expected phase coverage), (3) Weight detection by coverage (flag only if confidence high given partial data), (4) Mark systemic results as provisional when partial."}
{"type":"finding","id":"v3-edge-case-prober-004","title":"Severity Range Resolution Can Create False Escalations","severity":"Critical","phase":{"primary":"design","contributing":null},"section":"Verdict Logic","issue":"Design uses highest severity in range for verdict (conservative). If one pessimistic reviewer rates finding as Critical while others rate Important, verdict logic treats as Critical. Single outlier can trigger escalation. If reviewer calibration differs (one consistently rates higher), that reviewer controls verdict outcomes.","why_it_matters":"False escalations block progress when findings don't actually require escalation. If one reviewer is systematically more conservative, design never proceeds—every finding gets worst-case treatment. User loses benefit of multi-perspective review if single perspective dominates verdict.","suggestion":"Consider severity resolution strategies: (1) Majority vote (most reviewers win), (2) Escalate only if 2+ reviewers flag as Critical, (3) Present severity distribution to user, let them decide, (4) Calibrate reviewers to align severity scales, (5) Track per-reviewer severity distributions, flag outliers."}
```

**Step 3: Commit**

```bash
git add scripts/sample-findings-v3.jsonl
git commit -m "feat: add edge-case-prober findings (hash, loop, partial, escalation)"
```

---

## Task 4: Add Requirement Auditor and Feasibility Skeptic Findings

**Files:**
- Modify: `scripts/sample-findings-v3.jsonl`
- Read: `docs/reviews/parallax-review-v1/requirement-auditor.md`
- Read: `docs/reviews/parallax-review-v1/feasibility-skeptic.md`

**Step 1: Select 4-5 findings**

Target:
- Requirement Auditor Finding 2 (Critical): JSONL schema missing
- Requirement Auditor Finding 5 (Important): Model tiering unspecified
- Feasibility Skeptic Finding 3 (Critical): Prompt caching invalidation on calibration
- Feasibility Skeptic Finding 8 (Important): Reviewer coordination for external APIs
- Feasibility Skeptic Finding 11 (Critical): Test case validation missing

**Step 2: Add findings to JSONL**

Append to `scripts/sample-findings-v3.jsonl`:

```jsonl
{"type":"finding","id":"v3-requirement-auditor-002","title":"JSONL Output Format Schema Completely Missing","severity":"Critical","phase":{"primary":"calibrate","contributing":null},"section":"Output Artifacts (JSONL is canonical format)","issue":"Requirements specify JSONL is canonical output format for reviewer findings (FR6.1). Design references JSONL throughout (reviewers output JSONL, synthesizer reads JSONL, schema validation per FR7.5). But no schema definition exists. What fields? Required vs optional? Finding ID format? Severity enum values? Phase classification structure? Completely unspecified.","why_it_matters":"Four reviewers flagged this in v2 review. Issue persists in v3. Cannot implement FR7.5 (schema validation) without schema. Cannot implement JSONL output without field definitions. This is a design-blocking gap—referenced as decided but never specified. Must be resolved before any JSONL implementation.","suggestion":"Define JSONL schema immediately: (1) Create schema file in schemas/ directory, (2) Document required fields (finding ID, title, severity, phase, section, issue, rationale, suggestion), (3) Specify optional fields (disposition, tags, cross-refs), (4) Define enums (severity, phase labels), (5) Validate schema with JSON Schema specification."}
{"type":"finding","id":"v3-requirement-auditor-005","title":"Model Tiering Strategy Unspecified","severity":"Important","phase":{"primary":"design","contributing":"calibrate"},"section":"Reviewer Personas","issue":"Design references model tiering (Haiku for mechanical, Sonnet for analysis, Opus for deep review) but doesn't specify which reviewers use which models. Does Assumption Hunter need Opus-level reasoning? Can Prior Art Scout use Haiku for search? What's the quality vs cost tradeoff per persona? Requirements mention model tiering (NFR3.3) but assignment strategy unspecified.","why_it_matters":"Model choice impacts both cost and quality. Wrong model assignment (Haiku for complex reasoning, Opus for simple search) wastes budget or reduces quality. NFR2.1 targets <$1 per review at Sonnet pricing. If all reviewers use Opus, cost exceeds target. Need explicit model assignment with rationale.","suggestion":"Document model assignment per reviewer: (1) Specify model tier per persona with rationale, (2) Estimate cost impact (token counts x pricing), (3) Validate against NFR2.1 cost target, (4) Plan eval testing (Haiku vs Sonnet quality tradeoff), (5) Make model configurable for testing."}
{"type":"finding","id":"v3-feasibility-skeptic-003","title":"Prompt Caching Invalidation on Calibration Updates","severity":"Critical","phase":{"primary":"design","contributing":null},"section":"Reviewer Prompt Architecture","issue":"Design structures prompts as stable cacheable prefix + variable suffix. Calibration improvements (learning loop, false positive feedback) require modifying reviewer prompts. Adding calibration rules to stable prefix invalidates cache. Next review pays full input token cost. Cost optimization via caching conflicts with quality improvement via calibration.","why_it_matters":"Learning loop (Iteration 2 Finding 29 disposition) is core to improving reviewer quality over time. If every calibration change costs 90% cache benefit, improving prompts becomes prohibitively expensive. Design acknowledges conflict but provides no solution. Must resolve before implementing calibration.","suggestion":"Separate calibration rules from cacheable prefix. Three-part prompt structure: (1) Stable prefix (persona, methodology, format—rarely changes), (2) Calibration rules (versioned, changes based on feedback, NOT cached), (3) Variable suffix (artifact being reviewed). Cache stable prefix. Include calibration rules in non-cached middle section. Track calibration version separately."}
{"type":"finding","id":"v3-feasibility-skeptic-008","title":"Reviewer Tool Access Needs Coordination for External APIs","severity":"Important","phase":{"primary":"design","contributing":null},"section":"Reviewer Capabilities","issue":"Design specifies Prior Art Scout can use gh, curl for external research. Multiple reviewers independently querying same resource wastes quota. GitHub API has rate limits (60/hour unauthenticated, 5000/hour authenticated). If 6 reviewers all search GitHub for design review tools, that's 6 API calls. Expensive for same data. No coordination or caching specified.","why_it_matters":"External API quotas are finite. Redundant queries waste quota and slow review. If review runs in CI/CD (future automation), rate limits become blocking failures. Need result sharing across reviewers for quota-limited resources.","suggestion":"Add result caching for external API calls: (1) If Prior Art Scout searches GitHub for X, cache result, (2) Other reviewers can reference cached result, (3) Coordinate tool access (maybe only one reviewer per external resource), (4) Document which tools are quota-limited, (5) Plan for CI/CD rate limit handling."}
{"type":"finding","id":"v3-feasibility-skeptic-011","title":"Test Case Validation Still Missing After Three Review Iterations","severity":"Critical","phase":{"primary":"calibrate","contributing":null},"section":"Testing & Validation","issue":"After 3 review iterations, only self-review completed. Second Brain test case (real project with 40+ known design flaws) has not been run. Design claims reviewers catch design flaws, but no external validation performed. Self-review catches process issues but not effectiveness at finding real problems.","why_it_matters":"Without test case validation, unknown whether reviewers actually catch design flaws in real designs. Self-review is circular—reviewers find issues in review design, but that doesn't prove they'd find issues in Second Brain API design. Need external validation before claiming tool works. This is a requirements validation gap—build vs leverage decision deferred pending evaluation, but evaluation never performed.","suggestion":"Run Second Brain test case immediately: (1) Use known design with documented flaws, (2) Run parallax:review on Second Brain design, (3) Check if reviewers flag known issues, (4) Measure false positives (flagged non-issues), (5) Use results to validate approach before further development."}
```

**Step 3: Commit**

```bash
git add scripts/sample-findings-v3.jsonl
git commit -m "feat: add requirement-auditor and feasibility-skeptic findings"
```

---

## Task 5: Add First Principles and Prior Art Scout Findings

**Files:**
- Modify: `scripts/sample-findings-v3.jsonl`
- Read: `docs/reviews/parallax-review-v1/first-principles.md`
- Read: `docs/reviews/parallax-review-v1/prior-art-scout.md`

**Step 1: Select 3-4 final findings**

Target:
- First Principles Finding 2 (Critical): Problem framing inversion
- First Principles Finding 3 (Important): Adversarial naming mismatch
- Prior Art Scout Finding 1 (Important): Design updates lack specifications
- Prior Art Scout Finding 2 (Critical): Build vs leverage evaluation deferred

**Step 2: Add findings to JSONL**

Append to `scripts/sample-findings-v3.jsonl`:

```jsonl
{"type":"finding","id":"v3-first-principles-002","title":"Problem Framing Inversion: Requirements Review Higher Leverage Than Design Review","severity":"Critical","phase":{"primary":"calibrate","contributing":"survey"},"section":"Problem Statement","issue":"Requirements review prevents design flaws, design review detects them. Prevention > detection. Requirements stated as job-to-be-done in requirements doc: catch design flaws in phase that caused them (Job 2). Highest leverage is catching requirement gaps before design starts. But prototype focuses on design review, defers requirements review to later. Building detection before prevention inverts priority.","why_it_matters":"If requirements have gaps, design review will catch downstream symptoms but not root cause. Findings will escalate to calibrate phase, requiring requirements rework anyway. Building design review first means building symptom detection, then building root cause detection. More efficient to validate requirements review (higher leverage) before design review (lower leverage).","suggestion":"Consider prioritizing requirements review prototype: (1) Run adversarial review on requirements doc (parallax-review-requirements-v1.md), (2) Validate that requirement gaps are catchable via review, (3) Compare effort of fixing requirements vs fixing design, (4) If requirements review proves higher leverage, build that skill first."}
{"type":"finding","id":"v3-first-principles-003","title":"Adversarial Naming Mismatch: Coverage-Based Inspection Not Adversarial Debate","severity":"Important","phase":{"primary":"calibrate","contributing":null},"section":"Name (parallax:review)","issue":"Tool name references adversarial review but design implements coverage-based inspection with distinct personas. Adversarial implies conflicting incentives (debate, argument, competing positions). Distinct personas have non-overlapping focus areas (assumptions, edge cases, requirements, feasibility). Reviewers don't debate each other—they inspect from different angles. This is parallax (multiple viewpoints) not adversarial (opposing positions).","why_it_matters":"Naming shapes expectations. Users expecting adversarial debate may be confused by coverage-based output (6 independent reviews, no debate synthesis). Adversarial review in academic context means reviewers challenge each other's positions. This tool doesn't do that—it provides multi-perspective inspection. Naming mismatch may cause misaligned usage.","suggestion":"Consider whether adversarial accurately describes the approach: (1) If reviewers should debate (synthesizer presents contradictions for resolution), keep adversarial, (2) If reviewers provide independent coverage, consider multi-perspective review or parallax review (already in name), (3) If this is exploratory (defer to empirical eval), note naming assumption for future validation."}
{"type":"finding","id":"v3-prior-art-scout-001","title":"Design Doc Sync Addresses Decisions But Not Specifications","severity":"Important","phase":{"primary":"design","contributing":"calibrate"},"section":"Iteration 3 Changes","issue":"Iteration 2 flagged 67% documentation debt (Requirement Auditor). Between v2 and v3, 23 accepted dispositions were synchronized to design doc. Major improvement: auto-fix mechanism added, cross-iteration tracking expanded, primary + contributing phases specified. But design addresses what to do, not how it works. JSONL schema still missing despite being referenced. Auto-fix workflow added but classification criteria, validation, git safety unspecified. Prompt caching section added but cache boundary, versioning, invalidation strategy unspecified.","why_it_matters":"Documentation debt resolved (good) but architectural specification gaps remain (blocker). Saying we decided to use JSONL is different from defining the JSONL schema. Accepted decisions need implementation specifications. Without specifications, implementer makes unreviewed assumptions. Four architectural decisions documented as decided but unspecified.","suggestion":"Distinguish documentation debt (decided but not written down) from specification gaps (decided but not detailed). For each accepted decision that requires implementation: (1) Define the mechanism (JSONL schema, auto-fix workflow, finding ID algorithm), (2) Specify validation criteria, (3) Document edge cases, (4) Provide examples. Treating specifications as documentation debt incorrectly scopes the work."}
{"type":"finding","id":"v3-prior-art-scout-002","title":"Build vs Leverage Decision Deferred Despite Significant Prior Art","severity":"Critical","phase":{"primary":"calibrate","contributing":"survey"},"section":"Evaluation Strategy","issue":"Inspect AI, LangGraph, LangSmith, Braintrust identified as mature solutions solving 60-80% of custom infrastructure needs. Design defers evaluation to when limits hit. But limits are unknowable without building first. If parallax builds custom orchestration then discovers Inspect AI handles it, that's wasted effort. Build vs leverage decision should precede building, not follow it.","why_it_matters":"Iteration 2 Finding 46 flagged Compound Engineering (15 review agents, learning loop, 8.9k stars) as direct prior art. Disposition: evaluate during testing. But if evaluation discovers we should have leveraged existing tools, we've built unnecessarily. SWE principle: evaluate build vs leverage before building. Deferring to when limits hit means building first, evaluating later—backwards.","suggestion":"Time-box prior art evaluation before significant custom development: (1) Spend 2-4 hours testing Inspect AI with sample review task, (2) Validate whether it handles multi-agent review orchestration, (3) Test LangGraph for state management, (4) If existing tools handle 80%+ of needs, leverage them, (5) Only build custom if clear gaps identified. Evaluation before building, not after."}
```

**Step 3: Commit**

```bash
git add scripts/sample-findings-v3.jsonl
git commit -m "feat: complete sample JSONL with first-principles and prior-art findings"
```

---

## Task 6: Validate Sample JSONL Against Schema

**Files:**
- Validate: `scripts/sample-findings-v3.jsonl`
- Schema: `schemas/reviewer-findings-v1.0.0.schema.json`
- Tool: `scripts/validate-schemas.py`

**Step 1: Check validate-schemas.py usage**

Read the validator script to understand command-line arguments:

```bash
python scripts/validate-schemas.py --help
```

Expected: Usage instructions showing --schema and --data flags.

**Step 2: Run validation**

```bash
python scripts/validate-schemas.py \
  --schema schemas/reviewer-findings-v1.0.0.schema.json \
  --data scripts/sample-findings-v3.jsonl
```

Expected output: Validation successful, 17 findings validated (or error messages if schema violations found).

**Step 3: Fix any validation errors**

If validation fails:
- Check finding_id format (must be `v3-{reviewer}-{sequence}`)
- Verify severity values (Critical, Important, Minor)
- Confirm phase.primary and phase.contributing values (survey, calibrate, design, plan, or null)
- Ensure all required fields present

Iterate until validation passes.

**Step 4: Document validation success**

Once validation passes, note in git:

```bash
git add scripts/sample-findings-v3.jsonl
git commit -m "validate: sample JSONL passes reviewer-findings schema (17 findings)"
```

---

## Task 7: Extract Patterns from Sample Findings

**Files:**
- Read: `scripts/sample-findings-v3.jsonl`
- Read: `schemas/pattern-extraction-v1.0.0.schema.json`
- Create: `docs/reviews/parallax-review-v1/patterns-v3.json`

**Step 1: Read sample findings**

Read all 17 findings from `scripts/sample-findings-v3.jsonl` into context.

**Step 2: Read pattern extraction schema**

Understand the expected output format, required fields, constraints (max 15 patterns).

**Step 3: Analyze findings and identify patterns**

Using Claude's semantic understanding, group findings by root cause/theme:

Expected patterns:
1. **Architectural Specification Gaps** - JSONL schema missing, auto-fix workflow unspecified, finding ID mechanism undefined
2. **Assumption Violations** - Git-only, file system SSOT, stable sections, side-effect-free reads
3. **Edge Case Failures** - Hash brittleness, auto-fix loops, partial results corruption, false escalations
4. **Systemic Detection Issues** - Phase-based detection flaws, partial data bias
5. **Validation Gaps** - Test case missing, external validation needed
6. **Prior Art Evaluation Deferred** - Build vs leverage decision postponed
7. **Prompt Engineering Challenges** - Caching conflicts with calibration, model tiering unspecified
8. **Problem Framing Questions** - Requirements review priority, adversarial naming

For each pattern:
- Identify contributing findings (finding_ids)
- Determine severity range (union of finding severities)
- Identify affected phases (primary and contributing)
- Write summary (2-3 sentences)
- Provide actionable next step

**Step 4: Compute systemic issues**

Apply clustering logic:
- Count findings per pattern
- Identify patterns with 4+ findings OR >30% of total (>5 findings from 17)
- For high-clustering patterns, identify contributing phase
- Calculate percentage
- Flag as systemic if threshold exceeded

Expected systemic issues:
- Architectural specification gaps (5+ findings, ~29-35% depending on grouping)
- Assumption violations (4+ findings, ~23-29%)

**Step 5: Generate pattern extraction JSON**

Create structured output following schema. Include metadata:

```json
{
  "schema_version": "1.0.0",
  "type": "pattern_extraction",
  "metadata": {
    "review_run_id": "parallax-review-v1",
    "iteration": 3,
    "extraction_date": "2026-02-16T...",
    "total_findings": 17,
    "patterns_extracted": 8,
    "extraction_model": "claude-sonnet-4-5-20250929"
  },
  "patterns": [
    {
      "pattern_id": "p1",
      "title": "Architectural Specification Gaps",
      "finding_ids": ["v3-requirement-auditor-002", "v3-assumption-hunter-001", "v3-prior-art-scout-001", "..."],
      "finding_count": 5,
      "severity_range": ["Critical", "Important"],
      "affected_phases": {
        "primary": ["design", "calibrate"],
        "contributing": ["calibrate"]
      },
      "summary": "Multiple design decisions documented as accepted but lack implementation specifications. JSONL schema referenced throughout but never defined. Auto-fix workflow added to design but classification criteria, validation mechanisms, and git safety protocols unspecified. Finding ID mechanism mentioned but hash generation algorithm undefined.",
      "actionable_next_step": "Define schemas and specifications for all referenced-but-unspecified mechanisms: (1) JSONL schema with field definitions, (2) Auto-fix classification criteria with validation, (3) Finding ID generation algorithm with semantic matching fallback.",
      "reviewers": ["requirement-auditor", "assumption-hunter", "prior-art-scout"]
    },
    ...
  ],
  "systemic_issues": [
    {
      "contributing_phase": "calibrate",
      "finding_count": 5,
      "percentage": 29.4,
      "threshold_exceeded": false,
      "description": "Multiple findings trace to incomplete requirements phase - specifications missing for architectural decisions already made"
    }
  ]
}
```

**Step 6: Write pattern output**

Write the generated JSON to `docs/reviews/parallax-review-v1/patterns-v3.json`.

**Step 7: Commit pattern extraction**

```bash
git add docs/reviews/parallax-review-v1/patterns-v3.json
git commit -m "feat: extract patterns from v3 sample findings (8 patterns, 1 systemic)"
```

---

## Task 8: Validate Pattern Output Against Schema

**Files:**
- Validate: `docs/reviews/parallax-review-v1/patterns-v3.json`
- Schema: `schemas/pattern-extraction-v1.0.0.schema.json`

**Step 1: Run schema validation**

```bash
python scripts/validate-schemas.py \
  --schema schemas/pattern-extraction-v1.0.0.schema.json \
  --data docs/reviews/parallax-review-v1/patterns-v3.json
```

Expected: Validation successful.

**Step 2: Fix validation errors if any**

Common issues:
- pattern_id format (must be p1, p2, ..., p15)
- finding_ids format (must match `v\d+-[a-z-]+-\d{3}`)
- severity_range values (must be from enum)
- affected_phases structure (primary as array, contributing as array or null)
- Maximum 15 patterns

Iterate until validation passes.

**Step 3: Commit validation success**

```bash
git add docs/reviews/parallax-review-v1/patterns-v3.json
git commit -m "validate: patterns-v3.json passes pattern-extraction schema"
```

---

## Task 9: Review Pattern Quality

**Files:**
- Read: `docs/reviews/parallax-review-v1/patterns-v3.json`
- Read: `docs/reviews/parallax-review-v1/summary.md` (original v3 summary for comparison)

**Step 1: Review extracted patterns**

Manually review patterns against v3 summary findings categories:
- Do patterns capture the 5 critical categories from v3 summary?
- Are patterns actionable (clear next steps)?
- Do severity ranges make sense?
- Are reviewers properly attributed?

**Step 2: Validate systemic detection**

Check systemic issues:
- Do flagged systemic issues align with actual clustering?
- Are percentages computed correctly?
- Does contributing phase attribution make sense?

**Step 3: Document any gaps**

If patterns miss key themes or systemic detection is incorrect, document for iteration.

**Step 4: Note findings**

Create summary notes for issue #17 update.

---

## Task 10: Document Findings in Issue #17

**Files:**
- Update: GitHub issue #17

**Step 1: Generate summary**

Create comment summarizing:
- Sample size: 17 findings from 6 reviewers
- Patterns extracted: 8 patterns (list titles)
- Systemic issues: 1-2 flagged (describe)
- Validation: All schemas passed
- Next steps: Full conversion, requirements update, eval framework

**Step 2: Post to issue #17**

```bash
gh issue comment 17 --body "$(cat <<'EOF'
## Pattern Extraction Prototype Results

**Sample:** 17 findings from v3 review (6 reviewers, mix of C/I/M)

**Patterns extracted:** 8 patterns identified
1. Architectural Specification Gaps (5 findings)
2. Assumption Violations (4 findings)
3. Edge Case Failures (4 findings)
4. ...

**Systemic detection:** 1 systemic issue flagged
- Contributing phase: calibrate (29.4% of findings, just under 30% threshold)
- Description: Multiple findings trace to incomplete requirements phase

**Validation:** ✅ All schemas passed
- Sample JSONL validates against reviewer-findings-v1.0.0.schema.json
- Pattern output validates against pattern-extraction-v1.0.0.schema.json

**Key learnings:**
- Pattern-based systemic detection works well (semantic grouping)
- LLM-driven extraction identified themes matching v3 summary categories
- Schema validation caught format issues early

**Next steps:**
1. Run full conversion (Opus subagent converts all 83 v3 findings to JSONL)
2. Re-run pattern extraction on full dataset
3. Update FR2.7/FR10 in requirements (ADR documenting pattern-based approach)
4. Integrate into parallax:review skill

**Files:**
- `scripts/sample-findings-v3.jsonl` (17 findings)
- `docs/reviews/parallax-review-v1/patterns-v3.json` (8 patterns)
- `docs/plans/2026-02-16-pattern-extraction-design.md` (design doc)
EOF
)"
```

**Step 3: Commit documentation**

```bash
git commit --allow-empty -m "docs: document pattern extraction prototype results in issue #17"
```

---

## Task 11: Push Feature Branch and Create PR

**Files:**
- Branch: `feat/pattern-extraction-prototype`

**Step 1: Review all commits**

```bash
git log --oneline origin/main..HEAD
```

Expected: 10-12 commits covering sample creation, pattern extraction, validation, documentation.

**Step 2: Push branch**

```bash
git push -u origin feat/pattern-extraction-prototype
```

**Step 3: Create pull request**

```bash
gh pr create \
  --title "feat: pattern extraction prototype (Issue #17)" \
  --body "$(cat <<'EOF'
## Summary

Prototype pattern-based systemic detection using v3 review sample data.

## Changes

- Create `scripts/sample-findings-v3.jsonl` with 17 cherry-picked findings
- Extract 8 semantic patterns to `docs/reviews/parallax-review-v1/patterns-v3.json`
- Validate pattern-based systemic detection approach
- Document design in `docs/plans/2026-02-16-pattern-extraction-design.md`

## Validation

- ✅ Sample JSONL validates against reviewer-findings schema
- ✅ Pattern output validates against pattern-extraction schema
- ✅ Patterns match expected v3 themes
- ✅ Systemic detection identifies high-clustering themes

## Test Results

- 17 findings → 8 patterns (expected 8-12, within range)
- 1 systemic issue flagged (calibrate phase, 29.4%)
- All findings properly attributed to reviewers
- Severity ranges computed correctly

## Next Steps

- [ ] Full v3 conversion (83 findings → JSONL)
- [ ] Re-run pattern extraction on full dataset
- [ ] Update requirements FR2.7/FR10 with ADR
- [ ] Integrate into parallax:review skill

Closes #17

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Success Criteria

- ✅ Sample JSONL created and validated (17 findings)
- ✅ Pattern extraction completes without errors
- ✅ 8-12 patterns identified (target range)
- ✅ Patterns match expected v3 themes
- ✅ Systemic detection flags appropriate issues
- ✅ All schema validations pass
- ✅ Documentation updated in issue #17
- ✅ PR created and ready for review

---

## Notes

- This is a prototype validating approach, not production implementation
- Full markdown-to-JSONL conversion deferred to post-validation
- Pattern-based systemic detection is a clarification of FR2.7 (requires requirements update)
- LLM-driven extraction may produce slight variations across runs (expected, not a bug)

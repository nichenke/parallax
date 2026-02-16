# Pattern Extraction Prototype Design

**Date:** 2026-02-16
**Status:** Approved
**Issue:** #17
**Scope:** Test FR10.3/FR10.4 pattern extraction with v3 review data

---

## Overview

Prototype pattern extraction logic using sample findings from v3 review data (83 findings). This validates the pattern-based systemic detection approach before full pipeline integration.

**Key validation goals:**
- Test semantic pattern extraction (max 15 patterns from sample findings)
- Validate pattern-based systemic detection (clustering by theme/cause)
- Confirm JSONL schema compliance (input and output)
- Identify any design gaps before requirements update

---

## Architecture

**Skill-driven workflow** (Claude-native, no external tooling):

1. **Sample JSONL creation** - Cherry-pick 15-20 findings from v3 markdown, convert to JSONL
2. **Pattern extraction** - Analyze findings, identify semantic patterns (LLM-driven)
3. **Systemic detection** - Flag high-clustering patterns as systemic issues
4. **Schema validation** - Validate output against pattern extraction schema
5. **Documentation** - Summarize findings in issue #17

**File structure:**
```
scripts/
  sample-findings-v3.jsonl          # Handcrafted sample (new)
  validate-schemas.py               # Existing validator
schemas/
  reviewer-findings-v1.0.0.schema.json    # Input validation
  pattern-extraction-v1.0.0.schema.json   # Output validation
docs/reviews/parallax-review-v1/
  patterns-v3.json                  # Output (new)
```

**Execution:** Claude Code session (main or Sonnet subagent) using Read/Write tools.

---

## Sample Finding Selection

**Selection criteria for 15-20 findings:**

**Severity distribution (match v3 ratios):**
- 5-6 Critical (26% of v3 findings)
- 10-12 Important (57% of v3 findings)
- 2-3 Minor (17% of v3 findings)

**Reviewer diversity:**
- At least 2-3 findings from each of the 6 reviewers
- Ensures patterns span multiple perspectives

**Phase coverage:**
- Mix of primary phases: design, calibrate, survey, plan
- Include 5+ findings with contributing phases (tests systemic detection)

**Pattern-worthy themes (from v3 summary):**
- Architectural specification gaps (JSONL schema, finding IDs, auto-fix workflow)
- Assumption violations (git-only, single-user, stable sections)
- Edge case failures (hash brittleness, partial results, severity ranges)
- Auto-fix risks (unsafe workflow, infinite loops, no validation)

**Goal:** Representative sample that exercises pattern extraction across severity, phases, and themes.

---

## Pattern Extraction Logic

**LLM-driven semantic grouping:**

**Input to Claude:**
- All findings from `sample-findings-v3.jsonl` (15-20 findings)
- Pattern extraction schema definition
- Instructions: "Identify up to 15 semantic patterns across these findings"

**Pattern identification criteria:**
- **Semantic grouping:** Findings addressing same root cause/theme
- **Cross-reviewer validation:** Patterns should span multiple reviewers when possible
- **Actionable themes:** Each pattern needs clear next step
- **Phase attribution:** Primary + contributing phases per pattern

**Output structure (per schema):**
```json
{
  "pattern_id": "p1",
  "title": "Brief pattern name",
  "finding_ids": ["v3-assumption-hunter-001", "v3-edge-case-prober-002"],
  "finding_count": 3,
  "severity_range": ["Critical", "Important"],
  "affected_phases": {
    "primary": ["design"],
    "contributing": ["calibrate"]
  },
  "summary": "What the pattern represents",
  "actionable_next_step": "Concrete action to address",
  "reviewers": ["assumption-hunter", "edge-case-prober"]
}
```

**Constraints:**
- Max 15 patterns (FR10.1)
- Single pass extraction (no iterative refinement for MVP)
- Pattern IDs: p1, p2, ..., p15

---

## Systemic Detection (Pattern-Based)

**Clarified approach:** Systemic issues are patterns with high clustering (multiple findings sharing same root cause/theme). Phase attribution tells WHERE the systemic issue originated.

**Algorithm:**

1. **Extract patterns** (semantic grouping by theme/cause)
2. **Compute clustering strength** per pattern:
   - **High:** 4+ findings in pattern, OR >30% of findings with contributing_phase
   - **Medium:** 3 findings spanning 2+ reviewers
3. **Flag high-clustering patterns** as systemic issues
4. **Identify contributing phase** - Where the systemic root cause originated

**Example:**
- Pattern: "JSONL schema completely missing"
- 5 findings from 4 reviewers all flag this
- **Systemic issue:** Yes (high clustering, architectural gap)
- **Contributing phase:** calibrate (specification missing from requirements)

**Output structure:**
```json
{
  "systemic_issues": [
    {
      "contributing_phase": "calibrate",
      "finding_count": 5,
      "percentage": 33.3,
      "threshold_exceeded": true,
      "description": "JSONL schema referenced in multiple design decisions but never specified in requirements"
    }
  ]
}
```

**Post-prototype:** If this approach validates well, update FR2.7/FR10 in requirements to clarify pattern-based systemic detection (not simple phase counting).

---

## Schema Validation

**Two validation points:**

**Input validation:**
- Read `sample-findings-v3.jsonl`
- Validate each finding against `reviewer-findings-v1.0.0.schema.json`
- Ensures JSONL format is correct before pattern extraction
- Catches: missing required fields, invalid finding_id format, invalid severity/phase values

**Output validation:**
- After generating `patterns-v3.json`
- Validate against `pattern-extraction-v1.0.0.schema.json`
- Use existing `scripts/validate-schemas.py`
- Ensures: max 15 patterns, valid pattern_ids, required fields present

**Validation command:**
```bash
python scripts/validate-schemas.py \
  --schema schemas/pattern-extraction-v1.0.0.schema.json \
  --data docs/reviews/parallax-review-v1/patterns-v3.json
```

---

## Testing & Success Criteria

**Testing workflow:**

1. **Sample JSONL creation:**
   - Cherry-pick 15-20 findings from v3 markdown
   - Convert to JSONL following reviewer-findings schema
   - Validate sample against schema

2. **Pattern extraction:**
   - Run extraction (main session or Sonnet subagent)
   - Expect 8-12 patterns from 15-20 findings
   - Verify patterns capture v3 themes

3. **Systemic detection:**
   - Validate clustering logic identifies high-frequency themes
   - Check phase attribution makes sense
   - Confirm threshold logic works

4. **Output validation:**
   - Schema validation passes
   - patterns-v3.json is well-formed
   - All required fields present

**Success criteria:**
- ✅ Sample JSONL validates against reviewer-findings schema
- ✅ Pattern extraction completes without errors
- ✅ Output validates against pattern-extraction schema
- ✅ Patterns identified match expected v3 themes (manual review)
- ✅ Systemic detection flags 1-2 systemic issues
- ✅ Documentation updated (findings, next steps)

**Deliverables:**
- `scripts/sample-findings-v3.jsonl` (15-20 cherry-picked findings)
- `docs/reviews/parallax-review-v1/patterns-v3.json` (extracted patterns)
- Summary comment in issue #17 with findings and next steps

---

## Key Decisions

**1. Skill-driven (not Python script)**
**Rationale:** Claude-native approach aligns with project philosophy, no external dependencies, closer to eventual skill implementation.

**2. Manual sample creation (not full markdown conversion)**
**Rationale:** Prototype goal is validating pattern logic, not conversion tooling. Full conversion can be done later via Opus subagent once approach is validated.

**3. Pattern-based systemic detection (not simple phase counting)**
**Rationale:** Systemic issues are about theme clustering (multiple findings → same root cause). Phase attribution tells where the root cause originated. This is a clarification of FR2.7 requiring post-prototype requirements update.

**4. LLM-driven pattern extraction (not rule-based)**
**Rationale:** "Semantic patterns" (FR10.1) requires understanding meaning, not just grouping by attributes. Tests real-world behavior and prompt quality.

**5. Single-pass extraction (no iterative refinement)**
**Rationale:** MVP scope. Iterative refinement (user feedback → calibration rules) deferred to post-MVP.

---

## Next Steps

1. ✅ Design approved
2. Create implementation plan (writing-plans skill)
3. Execute: Create sample JSONL, extract patterns, validate output
4. Document findings in issue #17
5. If validated: Update FR2.7/FR10 in requirements (ADR documenting pattern-based approach)
6. If issues found: Iterate on design, update this doc

---

## Open Questions (Post-Prototype)

These questions will be answered by prototype results:

1. **Pattern count:** Do 15-20 findings produce 8-12 patterns, or fewer/more?
2. **Systemic threshold:** Is >30% the right threshold, or should it be adjusted?
3. **Phase attribution:** Can we reliably identify contributing phase for systemic patterns?
4. **Schema gaps:** Does the pattern-extraction schema need refinement?
5. **Requirements update:** What changes to FR2.7/FR10 are needed based on findings?

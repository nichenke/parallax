# Requirements: parallax:review

**Date:** 2026-02-16
**Status:** Draft v1.2 (Post-Review)
**Scope:** Multi-agent adversarial design review skill

---

## Jobs-to-Be-Done

This skill addresses five validated pain points from real design sessions (see `docs/problem-statements/design-orchestrator.md`):

**Job 1: Eliminate manual review orchestration overhead**
- Pain: Manually prompting 3+ reviewers, waiting, consolidating findings takes 15+ minutes per iteration
- Solution: Parallel multi-agent dispatch with automatic consolidation
- Requirements: FR1 (dispatch), FR2 (consolidation), FR7 (failure handling)

**Job 2: Catch design flaws in the phase that caused them**
- Pain: Design flaws discovered late, traced back to missing requirements or incomplete research
- Solution: Phase classification routes findings to the upstream phase that failed
- Requirements: FR2.5-FR2.7 (phase classification, systemic detection)

**Job 3: Provide clear go/no-go decisions at checkpoints**
- Pain: Ambiguous review outcomes, unclear whether to proceed or revise
- Solution: Computed verdict (proceed/revise/escalate) with human approval gate
- Requirements: FR3 (verdict), FR4 (human-in-the-loop)

**Job 4: Track design iteration progress across review cycles**
- Pain: No way to know if issues from previous review were addressed without manual cross-reference
- Solution: Cross-iteration pattern extraction and delta detection
- Requirements: FR5 (iteration tracking), FR10 (pattern extraction)

**Job 5: Enable data-driven improvement of the review process itself**
- Pain: No way to measure reviewer effectiveness or iterate on prompts empirically
- Solution: Structured output with cost/token tracking, eval-compatible format
- Requirements: FR6 (output artifacts), NFR2 (cost tracking), NFR5 (eval reproducibility), NFR6 (eval testing)
- Outcome: Track review cost and quality metrics to iteratively improve reviewer effectiveness

**User outcome:** Get adversarial design review in <5 minutes, with clear finding disposition and go/no-go decision.

---

## Functional Requirements

### FR1: Multi-Agent Review Dispatch

**FR1.1:** Dispatch 6+ reviewer agents in parallel
- **Rationale:** Parallel execution reduces wall-clock time, enables coverage-based inspection
- **Source:** design-orchestrator.md (subagent orchestration), design v3 (6 personas)

**FR1.2:** Each reviewer has distinct critical lens with non-overlapping blind spots
- **Rationale:** Multi-perspective review catches gaps that single-perspective misses (parallax principle)
- **Source:** design-orchestrator.md (persona engineering), design v3 (persona activation matrix)
- **Acceptance Criteria:**
  - Diversity: <30% of findings are flagged by >3 reviewers (shows distinct perspectives)
  - Coverage: Union of all reviewer findings covers >70% of planted issues in test cases (shows completeness)
  - Blind spot quality: Each reviewer's blind spot check identifies ≥1 gap in their own perspective
  - Measured via eval framework with ground-truth test cases containing known design flaws

**FR1.3:** Reviewers operate independently without cross-contamination
- **Rationale:** Avoid groupthink, preserve diversity of perspectives
- **Source:** MEMORY.md (clean reviews > anchored reviews), Q3 resolution (no prior context in reviewer prompts)

**FR1.4:** Support multiple review stages (requirements, design, plan) with stage-specific personas
- **Rationale:** Different phases need different critical lenses
- **Source:** design v3 (persona activation matrix: 9 personas, 4-6 active per stage)

---

### FR2: Finding Consolidation

**FR2.1:** Synthesizer consolidates findings across reviewers
- **Rationale:** Deduplicate overlapping findings, surface consensus
- **Source:** design v3 (synthesis section)

**FR2.2:** Deduplicate identical/similar findings, noting reviewer consensus
- **Rationale:** 5 reviewers flagging same issue = high-confidence signal
- **Source:** design v3 (synthesis responsibilities), v3 review (18 multi-reviewer findings)
- **Acceptance Criteria:**
  - Summary contains no duplicate findings (human evaluator confirms no redundancy)
  - When ≥3 reviewers flag semantically equivalent finding, summary notes consensus count
  - Eval framework tests with planted duplicates: >80% deduplication rate, <10% false merges

**FR2.3:** Classify findings by severity (Critical | Important | Minor)
- **Rationale:** Prioritize user attention, determine verdict
- **Source:** design v3 (per-reviewer output format), verdict logic

**FR2.4:** Report severity ranges when reviewers disagree
- **Rationale:** Transparency when different reviewers rate same issue differently
- **Source:** design v3 (synthesis responsibilities #4)

**FR2.5:** Classify findings by pipeline phase (survey | calibrate | design | plan)
- **Rationale:** Route findings to the phase that failed, enable self-error-detection
- **Source:** design-orchestrator.md (finding classification), design v3 (phase classification)

**FR2.6:** Support primary + contributing phase classification
- **Rationale:** "Design flaw (primary) caused by calibrate gap (contributing)" enables immediate fix + systemic correction
- **Source:** design v3 (finding phase classification), v3 review (11 findings with contributing phase)

**FR2.7:** Flag systemic issues when >30% of findings with a contributing phase share the same contributing phase
- **Rationale:** Detect upstream root causes requiring escalation
- **Source:** design v3 (finding phase classification), v3 review summary
- **Denominator:** Findings with `contributing_phase` set (not all findings). Systemic issues are upstream root causes, not immediate symptoms — only findings with a contributing phase signal upstream problems.
- **MVP scope:** Exact phase label matching. Semantic root cause clustering deferred (see D13)
- **Acceptance Criteria:**
  - Eval framework tests with planted systemic issues (multiple findings tracing to same upstream phase)
  - System correctly flags systemic when threshold exceeded, identifies the problematic upstream phase

**FR2.8:** Surface contradictions when reviewers disagree
- **Rationale:** Present both positions, user resolves tension
- **Source:** design v3 (synthesis responsibilities #3), v3 review (5 contradictions)

---

### FR3: Verdict Determination

**FR3.1:** Compute verdict: `proceed` | `revise` | `escalate`
- **Rationale:** Clear go/no-go decision at human checkpoint
- **Source:** design v3 (verdict logic)

**FR3.2:** Any Critical finding → `revise` (or `escalate` if survey/calibrate gap)
- **Rationale:** Critical findings block progress until addressed
- **Source:** design v3 (verdict logic)
- **Acceptance Criteria:**
  - Review with ≥1 Critical finding (design/plan phase) → verdict = revise
  - Review with ≥1 Critical finding (survey/calibrate phase) → verdict = escalate
  - Review with 0 Critical findings → verdict follows FR3.5 logic (proceed if only Important/Minor)
  - Eval framework tests verdict logic with test cases covering all severity/phase combinations

**FR3.3:** Survey or calibrate gap at any severity → `escalate`
- **Rationale:** Design can't be fixed without fixing upstream requirements/research
- **Source:** design v3 (verdict logic), design-orchestrator.md (finding classification)

**FR3.4:** Use highest severity in range for verdict computation (conservative)
- **Rationale:** One reviewer's Critical rating shouldn't be silently downgraded
- **Source:** design v3 (verdict logic, synthesis #6)

**FR3.5:** Only Important/Minor findings → `proceed` with noted improvements
- **Rationale:** Allow progression when no blocking issues exist
- **Source:** design v3 (verdict logic)

---

### FR4: Human-in-the-Loop

**FR4.1:** Present findings for interactive disposition (accept | reject-with-note | discuss)
- **Rationale:** Human judgment required for architectural decisions
- **Source:** design v3 (skill interface: "async-first, interactive processing as convenience layer")

**FR4.2:** Support async-first workflow (artifacts to disk, interactive processing optional)
- **Rationale:** Enable resumption, JSONL-based workflows, finding processing across sessions
- **Source:** design v3 (skill interface), MEMORY.md (async-first decision)

**FR4.3:** Track disposition outcomes in findings JSONL (append disposition field)
- **Rationale:** Single file, all context together, git tracks disposition history
- **Source:** design v3 (summary format: "Finding Dispositions"), design-orchestrator.md (ADR-style finding documentation), Q4.2 resolution

**FR4.4:** Human approval required before auto-proceeding to next phase
- **Rationale:** Never auto-proceed past checkpoint without human decision
- **Source:** design-orchestrator.md (human checkpoints)

---

### FR5: Cross-Iteration Tracking

**FR5.1:** Track findings with per-iteration IDs (no cross-run stability required)
- **Format:** `v{iteration}-{reviewer}-{sequence}` (e.g., `v3-assumption-hunter-001`)
- **Rationale:** Simple, unique per run, no hash brittleness
- **Source:** Q3 resolution (simple per-iteration IDs, pattern extraction handles cross-run comparison)

**FR5.2:** Identify new, resolved, and persisting findings via post-synthesis pattern extraction
- **Rationale:** Clean reviews (no prior context taints reviewers), semantic matching via LLM
- **Source:** Q3 resolution (two-pass post-synthesis flow)

**FR5.3:** Git commit per iteration (diffable history)
- **Rationale:** Full history, design doc + review artifacts evolve together
- **Source:** design-orchestrator.md (resolved questions #5), design v3 (output artifacts)

---

### FR6: Output Artifacts

**FR6.1:** JSONL is the canonical output format for all reviewer findings
- **Rationale:** Single source of truth, structured from the start, token efficient for synthesizer, enables CLI filtering (jq)
- **Source:** design v3, reviewer output format decision

**FR6.2:** Human-readable markdown files rendered from JSONL (synthesized summary + per-reviewer audit trail)
- **Rationale:** Markdown is a derived view for human consumption, not a source of truth
- **Source:** reviewer output format decision

**FR6.3:** All artifacts saved to `docs/reviews/<topic>/`
- **Rationale:** Git-tracked review history, organized by topic
- **Source:** design v3 (output artifacts)

**FR6.4:** Topic labels validated against safe character set
- **Rationale:** Prevent filesystem issues, enable reliable path construction
- **Source:** design v3 (skill interface)

**FR6.5:** Timestamped folders when re-running reviews of an existing topic
- **Rationale:** Re-runs (FR7.4) produce separate output without overwriting prior results
- **Source:** design v3 (collision handling)

---

### FR7: Partial Failure Handling

**FR7.1:** Proceed with partial results if minimum threshold met (4/6 agents)
- **Rationale:** Transient failures (rate limits, network errors) shouldn't block entire review
- **Source:** design v3 (parallel agent failure handling)

**FR7.2:** Timeout per agent (60-120s), with 1 retry + exponential backoff
- **Rationale:** Balance responsiveness with resilience to transient failures
- **Source:** design v3 (parallel agent failure handling)

**FR7.3:** Mark summary as partial if <100% reviewers completed
- **Rationale:** Transparency about review coverage
- **Source:** design v3 (parallel agent failure handling: "5/6 reviewers completed, Feasibility Skeptic timed out")

**FR7.4:** Support selective re-run of failed reviewers without redoing successful ones (error recovery)
- **Rationale:** Efficiency—don't re-run what already succeeded
- **Source:** design v3 (parallel agent failure handling), Q1 resolution (error recovery, not deterministic replay)

**FR7.5:** Validate reviewer JSONL output before synthesis (schema check, retry on malformed JSON)
- **Rationale:** Malformed output triggers retry, then fail-fast (prevents synthesizer errors)
- **Source:** design v3 (parallel agent failure handling), Q4 resolution (reviewers output JSONL)
- **Dependency:** Blocked on JSONL schema definition (Next Steps #4)

**FR7.6:** Clean up partial/corrupted output files before re-running failed reviewers
- **Rationale:** Avoid stale data contaminating re-run results
- **Source:** Q1 resolution (error recovery workflow)

---

### FR8: Reviewer Prompt Architecture

**FR8.1:** Three-part prompt structure: (1) Stable prefix (cached: persona, mandate, format, voice), (2) Calibration rules (not cached, versioned), (3) Variable suffix (file paths, not document content)
- **Rationale:** Cache optimization (90% savings) + quality iteration (calibration) without cache invalidation
- **Source:** design-orchestrator.md (prompt structure for caching), design v3 (reviewer prompt architecture), Q6 resolution

**FR8.2:** Track two versions: stable prefix (rarely changes, invalidates cache) and calibration rules (frequently changes, does not invalidate cache)
- **Rationale:** Enable prompt quality improvement without losing cache benefits
- **Source:** design v3 (reviewer prompt architecture: "changes to stable prefix should be tracked as versioned changes"), Q6 resolution

**FR8.3:** Reviewers read design/requirements documents via Read tool (supports multi-file designs, non-git docs)
- **Rationale:** Flexible document access (local files, URLs), enables selective reading, solves git-only assumption
- **Source:** Q6 resolution (tool use instead of prompt inclusion), resolves v3 Critical Finding C4

**FR8.4:** Highlight changed sections (git diff) when available for focus prioritization
- **Rationale:** Reviewers focus extra scrutiny on newly-changed sections
- **"When available":** Git repo exists AND design doc has prior committed version. First-time review → no diff highlighting.
- **Source:** design v3 (reviewer prompt architecture, variable suffix)

---

### FR9: Output Voice & Format

**FR9.1:** Active voice, lead with impact, then evidence
- **Rationale:** Engineer-targeted, direct communication
- **Source:** design v3 (output voice guidelines), design-orchestrator.md (output voice)

**FR9.2:** No hedging language ("might", "could", "possibly")
- **Rationale:** Clear, actionable findings
- **Source:** design v3 (output voice guidelines)

**FR9.3:** Quantify blast radius where possible
- **Rationale:** SRE-style framing for decision-making
- **Source:** design v3 (output voice guidelines)

**FR9.4:** Blind spot check per reviewer
- **Rationale:** Self-error-detection, transparency about limitations
- **Source:** design v3 (per-reviewer output format)

---

### FR10: Post-Synthesis Analysis (Cross-Iteration Delta Detection)

**FR10.1:** Extract semantic patterns from findings (group related issues into actionable themes)
- **Rationale:** Enable cross-iteration comparison without tainting clean reviews
- **Source:** Q3 resolution (two-pass post-synthesis flow)
- **Cap:** 15 patterns per review (sanity limit)
- **Output:** `docs/reviews/<topic>/patterns-v{N}.json`

**FR10.2:** Compare patterns across review runs automatically when prior review exists
- **Rationale:** Semantic matching (LLM handles equivalence), identify resolved/persisting/new patterns
- **Source:** Q3 resolution (delta detection)
- **Output:** `docs/reviews/<topic>/delta-v{N-1}-v{N}.json`

**FR10.3:** Pattern extraction and delta detection run in the critical path (after synthesis, before finding processing)
- **Rationale:** Pattern analysis is part of the review output, not a side channel. Artifacts always written to disk (async-first).
- **Source:** Q3 resolution, v2 review refinement

**FR10.4:** Reviews with >50 findings skip interactive pattern processing
- **≤50 findings:** Pattern extraction runs, artifacts to disk, interactive finding processing (FR4.1) includes pattern context
- **>50 findings:** Pattern extraction runs, artifacts to disk, summary notes finding count. User processes findings async.
- **Rationale:** Generous MVP threshold. Interactive processing of 50+ findings is impractical in-session.
- **Source:** Q3 resolution refinement, v2 review

**FR10.5:** Pattern extraction enables semantic root cause clustering (post-MVP enhancement to systemic detection)
- **Rationale:** After eval framework exists, add deeper analysis beyond simple phase counts
- **Source:** Q8 resolution (semantic clustering deferred to post-MVP)

---

## Non-Functional Requirements

### NFR1: Performance

**NFR1.1:** Review completes as quickly as possible (optimize for speed without sacrificing quality)
- **Rationale:** Rapid iteration workflow, minimize user wait time
- **Design assumption:** Parallel dispatch + 60-120s reviewer timeout suggests ~2-5 min total. Validate empirically.
- **Acceptance Criteria:**
  - Eval framework tracks P95 latency over time (no hard gate — complexity varies by design)
  - Performance regression testing alerts on >20% increase
  - Developer target: ≤5 minutes for typical design doc with 6 reviewers (happy path)

**NFR1.2:** Synthesizer processes 100+ findings without timeout
- **Rationale:** v3 review produced 83 findings, expect larger designs to exceed 100
- **Design assumption:** Extrapolated from v3 data. Validate with larger design artifacts.

---

### NFR2: Cost

**NFR2.1:** Review cost < $1 per run at Sonnet pricing (with prompt caching)
- **Rationale:** Budget sustainability—$200-400/month for hundreds of reviews
- **Source:** CLAUDE.md ($150-400 projected API spend), design-orchestrator.md (prompt caching)

**NFR2.2:** Cost logging per review run (token counts, cache hit rates, total cost)
- **Rationale:** Track budget burn, validate cost assumptions, inform model tiering
- **Source:** design v3 (line 323: "cost logging per review run in JSONL output"), v3 review (3 reviewers flagged missing cost data)

**NFR2.3:** Support prompt caching for 90% input cost reduction on stable prefix
- **Rationale:** Budget efficiency for repeated reviews
- **Source:** CLAUDE.md (prompt caching), design v3 (reviewer prompt architecture)

**NFR2.4:** Per-reviewer cost and duration tracking (token counts, wall clock time, model used)
- **Rationale:** Budget validation, model tiering decisions, cache effectiveness analysis
- **Source:** Q4.3 resolution

**NFR2.5:** Run-level metadata tracking
- **Vendor, model IDs, prompt versions:** Differentiate runs for eval framework
- **Run parameters:** Deep consolidation, auto-fix enabled, etc.
- **Enables:** Model comparison, prompt iteration analysis, vendor portability testing, cache effectiveness analysis
- **Source:** Q4.3+ resolution

**NFR2.6:** Calibration rules enable prompt quality improvement without cache invalidation
- **Rationale:** Cost optimization + quality iteration (add calibration rules without losing cache benefits)
- **Source:** Q6 resolution (three-part prompt structure)

---

### NFR3: Extensibility

**NFR3.1:** Add new reviewer personas without changing orchestration logic
- **Rationale:** Persona tuning is iterative, orchestration should be stable
- **Source:** design v3 (persona activation matrix: 9 personas, extensible)

**NFR3.2:** Support multiple review stages with stage-specific persona activation
- **Rationale:** Pipeline extends to requirements/plan review
- **Source:** design v3 (persona activation matrix)

**NFR3.3:** Pluggable model routing (Haiku | Sonnet | Opus) per persona
- **Rationale:** Cost optimization via model tiering
- **Source:** CLAUDE.md (model tiering), design-orchestrator.md (model routing), v3 review (Requirement Auditor Finding 5: model tiering unspecified)

**NFR3.4:** Configurable verdict thresholds (severity ranges, systemic issue %)
- **Rationale:** Enable tuning based on empirical data from eval framework
- **Source:** design v3 (verdict logic: "if false escalations become problem, investigate prompt tuning"), systemic issue 30% threshold

---

### NFR4: Reliability

**NFR4.1:** No infinite loops in auto-fix or re-review workflow
- **Rationale:** Prevent budget burn and workflow blocking
- **Source:** v3 review (Edge Case Prober Finding 2, Critical: "auto-fix re-review may loop indefinitely")
- **Note:** Auto-fix deferred to post-MVP (Q2 resolution)

**NFR4.2:** Partial reviewer failure doesn't corrupt verdict or systemic issue detection
- **Rationale:** Missing reviewers shouldn't produce misleading conclusions
- **Source:** v3 review (Edge Case Prober Finding 3, Critical: "partial completion breaks systemic detection")

**NFR4.3:** Git Safety Protocol compliance (no auto-commits without user approval)
- **Rationale:** Align with Claude Code git safety rules
- **Source:** v3 review (Assumption Hunter Finding 1, Critical: "auto-fix git workflow unsafe")

---

## Developer Requirements (Skill Quality Assurance)

These requirements support skill development, testing, and iterative improvement. They are not user-facing features — users benefit indirectly via improved review quality.

### NFR5: Eval Reproducibility

**NFR5.1:** Git-tracked prompts with version tagging (stable + calibration versions)
- **Rationale:** Eval framework can differentiate runs by prompt version
- **Source:** Q1 resolution (eval reproducibility), Q6 resolution (two version numbers)

**NFR5.2:** JSONL output enables cross-run comparison
- **Rationale:** Machine-comparable findings for eval analysis
- **Source:** Q1 resolution, Q4 resolution

**NFR5.3:** Cost/token logging per review run
- **Rationale:** Validate budget assumptions, correlate cost with quality
- **Source:** Q1 resolution, NFR2.2

**NFR5.4:** Measure finding variance across runs (low variance = stable prompts)
- **Rationale:** Non-deterministic output is expected, measure stability instead
- **Source:** Q1 resolution (accept variance, don't eliminate it)

**NFR5.5:** Prompt quality improves via feedback loop (eval framework → calibration rules)
- **Rationale:** Correction compounding pattern (false pos/neg → calibration rules)
- **Source:** Q1 resolution, design-orchestrator.md (correction compounding)

**NFR5.6:** Metadata enables run differentiation for eval testing
- **Model comparison:** Sonnet vs Opus quality
- **Prompt iteration:** v1.5 vs v2.1 effectiveness
- **Vendor portability:** Claude vs Codex compatibility
- **Cache effectiveness:** Correlate cache hit rate with cost savings
- **Source:** Q4.3+ resolution

**NFR5.7:** Metadata tracks stable + calibration versions separately
- **Rationale:** Eval framework can isolate version impacts (stable vs calibration changes)
- **Source:** Q6 resolution

---

### NFR6: Eval Testing for Pattern Extraction

**NFR6.1:** Eval framework tests pattern extraction accuracy
- **Ground truth:** Known patterns planted in test cases
- **Metric:** Pattern detection precision/recall
- **Source:** Q3 resolution (pattern extraction needs eval testing)

**NFR6.2:** Eval framework tests delta detection accuracy
- **Ground truth:** Planted resolved/persisting/new patterns across iterations
- **Metric:** Delta classification accuracy
- **Source:** Q3 resolution

**NFR6.3:** Pattern extraction prompt calibration based on false positives/negatives
- **Rationale:** Iterative improvement via correction compounding
- **Source:** Q3 resolution

---

## Constraints

### C1: Environment

**C1.1:** Claude Code CLI (primary execution environment)
- **Source:** CLAUDE.md (development philosophy)

**C1.2:** Codex CLI portability target
- **Rationale:** Multi-LLM compatibility, avoid Claude-specific assumptions
- **Source:** CLAUDE.md (Codex portability checks), design-orchestrator.md (portability sanity check script)

**C1.3:** Design docs accessible via local file paths or public URLs (MVP scope)
- **Reviewers use Read/WebFetch tools** to access documents (not inline in prompts)
- **MVP:** Local files and public URLs only. Authenticated sources (Confluence, Google Docs, Notion) deferred to MCP integration (see D6)
- **Rationale:** Supports non-git workflows, multi-file designs. MCP connectors required for authenticated sources.
- **Source:** Q6 resolution (tool use for document access), resolves v3 Critical Finding C4

**C1.4:** Local filesystem (single-user workflow)
- **Rationale:** Not multi-user collaboration, no concurrent review sessions
- **Design assumption:** Inferred from git-based tracking, async-first workflow

---

### C2: Budget

**C2.1:** $2000/month total budget
- **Source:** CLAUDE.md (budget & tooling)

**C2.2:** $150-400/month projected API spend
- **Source:** CLAUDE.md (budget & tooling)

**C2.3:** Batch API + prompt caching for cost reduction
- **Rationale:** 50% discount (batch) + 90% reduction (caching) = ~95% savings at scale
- **Source:** CLAUDE.md (cost strategy)

---

### C3: Workflow

**C3.1:** Human-driven iteration (not autonomous)
- **Rationale:** Human approval at checkpoints, no auto-proceed
- **Source:** design-orchestrator.md (human checkpoints)

**C3.2:** Single review session per topic (no concurrent reviews)
- **Rationale:** Simplifies state management, aligns with single-user constraint
- **Source:** Inferred from filesystem-based artifact storage

---

## Decision Log

Eight open questions (Q1-Q8) were resolved during requirements finalization. Full rationale, alternatives considered, and requirements impact are documented in:

**[ADR-001: Requirements v1.1 Resolutions](adr-001-requirements-v1-resolutions.md)**

Summary of decisions:

| Question | Decision |
|----------|----------|
| Q1: Deterministic execution | Error recovery (production) + eval reproducibility (testing), not replay |
| Q2: Auto-fix | Defer entirely to post-MVP |
| Q3: Cross-iteration matching | Clean reviews + post-synthesis pattern extraction |
| Q4: Output schema | JSONL canonical, markdown rendered, per-reviewer + run-level metadata |
| Q5: TOON format | Defer to post-MVP |
| Q6: Prompt caching | Three-part prompt (stable/calibration/variable) |
| Q7: Model tiering | Sonnet for MVP, eval framework tests Haiku post-MVP |
| Q8: Systemic detection | Simple phase count (>30% threshold) for MVP |

---

## Out of Scope (for MVP)

### Explicitly Deferred

**D1:** Multi-session memory/checkpointing
- **Rationale:** Stateless reviews for simplicity (not for determinism)
- **Source:** design-orchestrator.md (deferred considerations), Q1 resolution

**D2:** Real-time collaboration (multi-user review)
- **Rationale:** Single-user local filesystem workflow
- **Source:** Inferred from constraints

**D3:** Automatic requirement refinement
- **Rationale:** Human-driven calibrate phase, requires judgment
- **Source:** design-orchestrator.md (requirement refinement)

**D4:** Self-improvement/learning loop
- **Rationale:** Correction compounding deferred to Phase 3+
- **Source:** design-orchestrator.md (deferred considerations)

**D5:** Custom persona authoring UI
- **Rationale:** Use agent files directly, edit prompts manually
- **Source:** Inferred from agent-based architecture

**D6:** MCP integration
- **Rationale:** CLI-first, MCP deferred to Phase 2+
- **Source:** design-orchestrator.md (tooling), CLAUDE.md (CLI-first, MCP deferred)

**D7:** Optimal reviewer count determination
- **Rationale:** Empirical question for eval framework
- **Source:** design-orchestrator.md (resolved questions #3)

**D8:** Codex for execution phases
- **Rationale:** Prototype with Claude, evaluate Codex later
- **Source:** CLAUDE.md (Codex portability checks)

**D9:** LangGraph state machines (for cross-LLM orchestration and Full-Auto bounded iteration)
- **Rationale:** Nice-to-have for later, not needed for checkpoint/resume
- **Source:** Q1 resolution

**D10:** Auto-fix mechanism
- **Rationale:** v3 review had 0 auto-fixable findings, Git Safety violations, complexity
- **Source:** Q2 resolution

**D11:** TOON format (token-optimized output)
- **Rationale:** JSONL already optimized, further optimization premature
- **Source:** Q5 resolution

**D12:** Model tiering (Haiku for mechanical reviewers)
- **Rationale:** Eval framework tests quality tradeoffs first
- **Source:** Q7 resolution

**D13:** Semantic root cause clustering for systemic detection
- **Rationale:** Pattern extraction (FR10) handles this post-MVP
- **Source:** Q8 resolution

---

## Requirements Traceability

### Sources

- **design-orchestrator.md** — Problem statement, pain points, desired workflow
- **parallax-review-design.md** — Design v3 (post-v2 sync)
- **CLAUDE.md** — Project philosophy, budget, cost strategy
- **ADR-001** — Q1-Q8 resolutions (2026-02-16)
- **v3 review summary** — 83 findings, 22 Critical, reviewer consensus

### Coverage

**Jobs-to-Be-Done:** 5 validated pain points
**Functional requirements:** 10 categories, 48 discrete requirements
**Non-functional requirements:** 6 categories, 26 discrete requirements
**Constraints:** 3 categories, 8 discrete requirements
**Decision log:** 8 resolved questions (ADR-001)
**Out of scope:** 13 explicitly deferred items

---

## Next Steps

1. ✅ **Open questions resolved** (Q1-Q8) → ADR-001
2. ✅ **Requirements review** — Format/style, JTBD gap analysis, necessity assessment
3. **Define acceptance criteria** — Add explicit testability criteria to critical requirements (FR1.2, FR2.2, FR2.7, FR3.2, NFR1.1, 5-10 total)
4. **Update design doc** — Sync design v4 with finalized requirements
5. **JSONL schema implementation** — Define exact structure per FR6.1 (blocks FR7.5)
6. **Pattern extraction prototype** — Test FR10 workflow with existing v3 review data
7. **Token efficiency validation** — Measure savings from clean reviews (FR1.3) + tool-based document access (FR8.3)

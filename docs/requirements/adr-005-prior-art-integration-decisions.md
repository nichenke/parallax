# ADR-005: Prior Art Integration — Inspect AI and LangGraph Evaluation

**Date:** 2026-02-16
**Status:** Accepted
**Deciders:** @nichenke
**Related:** Issue #41 (Prior Art Spike), Issue #5 (Eval Framework), ADR-001 (LangGraph deferral)

---

## Context

Session 16 validated `parallax:requirements --light` with three test runs (42, 44, 92 findings). The next phase requires systematic evaluation infrastructure to:
1. Validate severity calibration across test cases
2. Measure finding quality (actionability, specificity, evidence)
3. Compare reviewer configurations (Sonnet vs Opus vs Haiku)
4. Detect agent configuration bugs via transcript analysis (Issue #37)

Before building custom eval infrastructure (Issue #5), an 8-10 hour prior art spike evaluated two mature frameworks:
- **Inspect AI** — LLM evaluation framework (UK AI Safety Institute)
- **LangGraph** — Multi-agent orchestration framework (LangChain)

**Research question:** Can we leverage existing tools instead of building custom infrastructure?

---

## Decision Summary

### 1. Integrate Inspect AI for Eval Framework (Issue #5)

**Decision:** Use Inspect AI as the foundation for parallax eval infrastructure.

**Rationale:**
- Provides 90% of needed infrastructure out-of-the-box (runner, logging, metrics, batch API, multi-model comparison)
- Native Claude support with zero integration friction
- LLM-as-judge patterns proven at scale (used by Anthropic, DeepMind, Grok)
- 50% cost reduction via batch API for offline eval runs
- Parallax only needs to build domain-specific scorers (~10% of work)
- Production-ready (47M+ PyPI downloads, MIT license, active development)

**Scope reduction for Issue #5:**
- ❌ Build eval runner infrastructure
- ❌ Build logging/metrics system
- ❌ Build batch API integration
- ❌ Build multi-model comparison tooling
- ✅ Build custom scorers for parallax-specific validation
- ✅ Define test datasets from review artifacts
- ✅ Integrate Inspect AI into CI/CD pipeline

### 2. Defer LangGraph for Orchestration

**Decision:** Use Claude Code native patterns (dispatching-parallel-agents skill) for MVP orchestration. Defer LangGraph integration.

**Rationale:**
- Parallax review pattern is simple: spawn 6 independent reviewers, collect findings, synthesize
- No inter-reviewer communication needed (reviewers don't debate each other)
- No state dependencies between reviewers
- No cyclic workflows (single-pass review, not iterative refinement)
- LangGraph optimizes for complex, stateful workflows — parallax doesn't have this complexity yet
- Code-first framework adds development friction without solving a current problem
- YAGNI: Build simplest thing that works, add complexity when needed

**When to reconsider LangGraph:**
- Cross-iteration state tracking becomes valuable (findings from review N inform review N+1)
- Inter-reviewer debate patterns emerge (competing hypotheses, adversarial critique)
- Cyclic refinement loops (design → review → redesign → review)
- Enterprise auditability requirements (workflow visualization, resumability)
- Multi-model orchestration (GPT critique, Claude execution, Gemini grading)

---

## Inspect AI Analysis

### What Inspect AI Provides

| Feature | Capability | Parallax Relevance |
|---------|-----------|-------------------|
| **Eval runner** | CLI + Python API, `@task` decorator pattern | Direct use |
| **LLM-as-judge** | Built-in `model_graded_fact()` scorer | Finding quality validation |
| **Custom scorers** | `@scorer` decorator for domain-specific logic | Severity calibration, pattern extraction |
| **Multi-model comparison** | Model roles pattern (red_team, blue_team, grader) | Reviewer selection (Sonnet vs Opus vs Haiku) |
| **Batch API** | Native Anthropic batch support, 50% cost reduction | Offline evals (not interactive sessions) |
| **Logging & metrics** | EvalLog captures inputs, outputs, scores, tokens, latency | FR8.3 (per-reviewer metrics), NFR2.1 (cost efficiency) |
| **Pre-built evals** | 100+ ready-to-run evaluations (ARC, MMLU, GSM8K, CTF) | Learning from patterns, adapting existing evals |
| **Claude integration** | Native Anthropic provider, streaming support, beta features | Zero integration friction |
| **Log viewer** | Inspect View (web UI), VS Code extension | Development tooling |

### What Parallax Must Build

**Custom Scorers (Python):**
1. `severity_calibration_scorer.py` — Validates severity distribution matches expected thresholds (e.g., Critical < 30%, Important 40-50%, Minor 20-30%)
2. `finding_quality_scorer.py` — LLM-as-judge for finding actionability, specificity, evidence quality
3. `pattern_extraction_scorer.py` — Validates semantic clustering produces coherent, non-overlapping patterns
4. `transcript_analysis_scorer.py` — Detects agent configuration bugs from conversation transcripts (Issue #37)

**Test Datasets:**
- Convert `docs/reviews/*/` artifacts to Inspect AI dataset format
- Ground truth: v3 review (87 findings, 12 patterns, known severity distribution)
- Test cases: requirements-light (42 findings), pattern-extraction (44 findings), parallax-review (92 findings)

**Evaluation Suite:**
- `evals/severity_calibration.py` — Run across test cases, compare distributions
- `evals/finding_quality.py` — LLM-as-judge validation of finding actionability
- `evals/pattern_extraction.py` — Validate clustering coherence
- `evals/multi_model_comparison.py` — Sonnet vs Opus vs Haiku reviewer selection

### Integration Architecture

```
parallax/
├── evals/                          # Inspect AI evaluation definitions (Python)
│   ├── severity_calibration.py
│   ├── finding_quality.py
│   ├── pattern_extraction.py
│   ├── transcript_analysis.py
│   └── multi_model_comparison.py
├── scorers/                        # Custom scoring functions
│   ├── severity_scorer.py
│   ├── quality_scorer.py
│   ├── pattern_scorer.py
│   └── transcript_scorer.py
├── skills/                         # Claude Code skills (Markdown)
│   └── parallax:requirements/      # Existing skill (no change)
├── docs/reviews/                   # Review artifacts (test datasets)
│   ├── requirements-light/
│   ├── pattern-extraction/
│   └── parallax-review/
└── .github/workflows/
    └── eval.yml                    # CI/CD integration (run evals on PR)
```

**Workflow:**
1. Develop skills in Claude Code (Markdown, natural language)
2. Define evals in Inspect AI (Python, structured datasets)
3. Run evals via CLI or CI/CD
4. Review results in Inspect View (web UI)
5. Iterate on skills based on eval findings

**Cost optimization:**
- Use batch API for all offline eval runs (50% discount)
- Prompt caching for repeated system prompts (90% input cost reduction on cache hits)
- Model tiering: Haiku for mechanical scorers, Sonnet for LLM-as-judge, Opus sparingly

### Limitations

1. **Python-based:** Eval definitions require Python (not Markdown). Acceptable — evals are separate from skills.
2. **Batch timing:** 1-24 hour delays unsuitable for interactive review sessions. Acceptable — batch only for offline evals, not production reviews.
3. **Learning curve:** Team needs to understand Dataset/Solver/Scorer patterns. Mitigated — start with examples from 100+ pre-built evals.

---

## LangGraph Analysis

### What LangGraph Provides

**Core capabilities:**
- DAG-based orchestration (nodes = agents, edges = data flow)
- Centralized state management (immutable state versioning)
- Conditional branching, parallel execution, cyclic workflows
- Multi-agent coordination (hierarchical, supervisor, fully connected)
- Human-in-the-loop interrupts
- Production features (streaming, horizontal scaling, resumability)
- Model-agnostic (Claude, GPT, Gemini, local models)

**Strengths:**
- Clear execution flow visualization
- Supports complex, deterministic workflows
- Auditability and resumability
- Enterprise deployments proven
- LangSmith integration (observability, debugging)

**Limitations:**
- Code-first (requires graph definition, state schema design)
- Configuration scales with complexity (simple = dozens of lines, production = hundreds)
- Requires distributed systems expertise for production
- State management creates potential bottlenecks
- Critical failure points: state corruption, deadlocks, memory exhaustion

### Parallax Review Pattern Analysis

**Current workflow:**
1. Spawn 6 reviewers in parallel (assumption-hunter, edge-case-prober, requirement-auditor, feasibility-skeptic, first-principles, prior-art-scout)
2. Each reviewer analyzes design independently
3. Synthesizer collects findings from all reviewers
4. Consolidate and classify findings (semantic clustering)
5. Generate summary report

**Key characteristics:**
- ❌ No inter-reviewer communication (reviewers don't debate each other)
- ❌ No state dependencies between reviewers
- ❌ No cyclic workflows (single-pass review, not iterative refinement)
- ❌ No conditional branching based on reviewer outputs
- ✅ Simple parallel execution + centralized synthesis

**Verdict:** LangGraph is **overkill for parallax MVP**. The review pattern is straightforward — exactly what `dispatching-parallel-agents` skill handles.

### Comparison: LangGraph vs Claude Code Native Patterns

| Feature | LangGraph | Claude Swarms | dispatching-parallel-agents |
|---------|-----------|---------------|----------------------------|
| **Setup** | Code-first (Python) | Natural language | Natural language |
| **State** | Centralized StateGraph | Shared task list | Main agent context |
| **Communication** | Via shared state | Direct messaging | Via main agent |
| **Multi-model** | ✅ Yes | ❌ Claude only | ❌ Claude only |
| **Cyclic workflows** | ✅ Yes | ❌ No | ❌ No |
| **Auditability** | ✅ High (graph viz) | ⚠️ Medium | ⚠️ Medium |
| **Resumability** | ✅ Yes | ❌ Known issue | ❌ No |
| **Token cost** | High (state overhead) | Very high (N instances) | Medium (results only) |
| **Learning curve** | High (graph DSL) | Low (natural language) | Low (skill pattern) |
| **Production maturity** | ✅ Proven | ⚠️ Experimental | ✅ Proven |

**Parallax MVP needs:**
- ✅ Independent reviewers (no inter-agent communication) → `dispatching-parallel-agents`
- ✅ Centralized synthesis (main agent collects findings) → `dispatching-parallel-agents`
- ✅ Simple workflow (spawn → collect → synthesize) → `dispatching-parallel-agents`
- ❌ No state dependencies → LangGraph not needed
- ❌ No cyclic refinement → LangGraph not needed
- ❌ No complex branching → LangGraph not needed

**Decision:** Use `dispatching-parallel-agents` for MVP. Defer LangGraph until complexity demands it.

---

## Consequences

### Positive

1. **Leverage proven infrastructure:** Inspect AI eliminates 90% of custom eval framework build
2. **Cost efficiency:** Batch API + prompt caching target <$0.50 per eval run (vs $2-5 custom build)
3. **Multi-model support:** Model roles pattern enables Sonnet vs Opus vs Haiku comparison
4. **Production-ready:** Used by AISI, Anthropic, DeepMind — trust the foundation
5. **Focus on value:** Build domain-specific scorers, not infrastructure plumbing
6. **Simplicity:** Native Claude Code patterns for orchestration (no LangGraph complexity)

### Negative

1. **Python dependency:** Eval definitions require Python (separate from Markdown skills)
2. **Learning curve:** Team needs to understand Inspect AI Dataset/Solver/Scorer patterns
3. **Framework lock-in:** Choosing Inspect AI commits to their architecture (mitigated by MIT license, open-source)
4. **Defer LangGraph benefits:** Auditability, resumability, workflow visualization deferred to post-MVP

### Neutral

1. **Two-language codebase:** Skills in Markdown, evals in Python (acceptable separation of concerns)
2. **Batch timing:** 1-24 hour eval runs unsuitable for interactive workflows (acceptable for offline validation)
3. **LangGraph deferral:** Revisit when complexity demands (consistent with YAGNI philosophy)

---

## Alternatives Considered

### Alternative 1: Build Custom Eval Infrastructure

**Pros:**
- Complete control over architecture
- No external dependencies
- Tailored to parallax-specific needs

**Cons:**
- 10x development effort (build runner, logging, metrics, batch API, multi-model, viewer)
- Reinventing proven infrastructure (UK AISI, Anthropic use Inspect AI)
- Maintenance burden (security updates, bug fixes, feature requests)
- Delayed validation (can't test skills until eval framework complete)

**Verdict:** Rejected. YAGNI — build only what Inspect AI doesn't provide.

### Alternative 2: Use LangGraph for Orchestration

**Pros:**
- Auditability (workflow visualization)
- Resumability (recover from failures)
- Multi-model orchestration (GPT + Claude + Gemini)
- Production-proven (enterprise deployments)

**Cons:**
- Code-first complexity (graph definition, state schema design)
- Solves problems parallax doesn't have (cyclic workflows, state dependencies, inter-agent communication)
- Learning curve (distributed systems expertise required)
- Development friction (Python DSL vs natural language skills)

**Verdict:** Deferred. Parallax MVP doesn't need LangGraph's complexity. Revisit when workflow demands it.

### Alternative 3: Use Claude Code Swarms for Orchestration

**Pros:**
- Native to Claude Code (zero setup)
- Direct agent messaging (inter-agent communication)
- Shared task list with dependency tracking
- Natural language control

**Cons:**
- Experimental (known issues: session resumption, task status lag)
- Overkill for parallax pattern (reviewers don't need to communicate)
- Higher token cost than dispatching-parallel-agents (N full Claude instances)
- Claude-only (no multi-model support)

**Verdict:** Rejected. Parallax reviewers operate independently — Swarms adds complexity without value.

---

## References

**Research artifacts:**
- Prior art spike findings: `docs/research/prior-art-spike-findings.md`
- Issue #41: Prior art spike tracking
- Issue #5: Eval framework (scope updated based on this ADR)

**Inspect AI:**
- Docs: https://inspect.aisi.org.uk/
- GitHub: https://github.com/UKGovernmentBEIS/inspect_ai
- Tutorial: https://inspect.aisi.org.uk/tutorial.html
- Batch mode: https://inspect.aisi.org.uk/models-batch.html

**LangGraph:**
- Main site: https://www.langchain.com/langgraph
- Docs: https://docs.langchain.com/oss/python/langgraph/workflows-agents
- Multi-agent guide: https://latenode.com/blog/ai-frameworks-technical-infrastructure/langgraph-multi-agent-orchestration/

**Claude Code Swarms:**
- Official docs: https://code.claude.com/docs/en/agent-teams
- Analysis: https://addyosmani.com/blog/claude-code-agent-teams/

---

## Revision History

- **2026-02-16:** Initial version (8-10 hour prior art spike)
- **Next review:** After Phase 1 (Inspect AI setup complete)

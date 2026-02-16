# Prior Art Spike: Inspect AI + LangGraph

**Issue:** #41
**Date:** 2026-02-16
**Investigator:** Claude Sonnet 4.5
**Duration:** ~3 hours (ongoing)

## Executive Summary

**Inspect AI:** Strong fit for parallax eval framework. Provides 90% of needed infrastructure out-of-the-box. Recommend integration.

**LangGraph:** Overkill for parallax MVP. Native Claude Code patterns (dispatching-parallel-agents) are sufficient for current orchestration needs. Defer until complexity demands it.

**Recommendation:** Integrate Inspect AI for Issue #5 (eval framework), use Claude Code native patterns for orchestration, document decision in ADR-005.

---

## Inspect AI Analysis

### Overview

- **Project:** UK AI Safety Institute (AISI), open-source (MIT license)
- **Latest release:** Feb 12, 2026
- **Maturity:** Production-ready, used by Anthropic, DeepMind, Grok
- **Downloads:** 47M+ PyPI downloads
- **Documentation:** https://inspect.aisi.org.uk/

### Core Architecture

Three-component evaluation pattern:

1. **Dataset**: Labeled samples with inputs and target values
2. **Solver**: Chained processing (generate(), chain_of_thought(), self_critique())
3. **Scorer**: Evaluation functions (exact(), match(), model_graded_fact(), custom)

Defined with `@task` decorator, executed via CLI or Python API.

### Key Features for Parallax

#### 1. LLM-as-Judge Infrastructure ✅

- Built-in `model_graded_fact()` scorer for subjective evaluation
- Custom scorer pattern via `@scorer` decorator
- Supports semantic equivalence checking (not just string matching)
- Examples: expression_equivalence (math), theory_of_mind (subjective)

**Parallax relevance:** Finding quality grading, severity calibration

#### 2. Multi-Model Comparison ✅

- **Model roles pattern**: Assign aliases (red_team, blue_team, grader) to different models
- **Eval Sets**: Systematic comparison via `task_with()`
- Supports swapping models across runs

**Parallax relevance:** Reviewer selection (Sonnet vs Opus vs Haiku), cross-model validation

#### 3. Comprehensive Logging & Metrics ✅

EvalLog captures:
- Complete solver plan documentation
- Per-sample inputs, outputs, scores
- Token usage at every step (cost proxy)
- Latency metrics with retries
- Aggregated results and error logs

**Parallax relevance:** FR8.3 (per-reviewer metrics), NFR2.1 (cost efficiency)

#### 4. Batch API Support ✅

- Native integration with Anthropic batch API
- **50% cost reduction** (typical: complete within 1 hour, max 24 hours)
- `BatchConfig(size=100, send_delay=15, max_batches=100)`
- Good fit: Sequential, low-volume evals (QA + model scorer)
- Poor fit: Agentic tasks with variable generation volumes

**Parallax relevance:** Eval runs (not interactive review sessions)

#### 5. Claude Integration ✅

- Native Anthropic provider (built-in)
- Setup: `export ANTHROPIC_API_KEY=...`
- Streaming support (auto-enabled for long requests)
- Beta features: `--model anthropic/claude-sonnet-4-0 -M betas=context-1m-2025-08-07`
- Supports Bedrock + direct API

**Parallax relevance:** Zero integration friction

#### 6. Pre-built Evaluations ✅

- 100+ ready-to-run evals (ARC, MMLU, GSM8K, CTF challenges)
- Agent evaluation support (ReAct, tool use, sandbox execution)
- Multi-turn dialogue patterns

**Parallax relevance:** Learning from existing patterns, potentially adapting CTF-style evals for design review

### What Inspect AI Provides vs. What Parallax Needs

| Need | Inspect AI | Parallax Build |
|------|-----------|----------------|
| Eval runner infrastructure | ✅ Built-in | ❌ Not needed |
| Token/cost tracking | ✅ EvalStats | ❌ Not needed |
| Multi-model comparison | ✅ Model roles | ❌ Not needed |
| LLM-as-judge patterns | ✅ model_graded_fact() | ❌ Not needed |
| Batch API integration | ✅ BatchConfig | ❌ Not needed |
| Dataset management | ✅ HuggingFace + custom | ❌ Not needed |
| Log viewer | ✅ Inspect View (web UI) | ❌ Not needed |
| VS Code extension | ✅ Built-in | ❌ Not needed |
| Severity calibration | ❌ Not built-in | ✅ Custom scorer |
| Finding quality grading | ❌ Not built-in | ✅ Custom scorer |
| Transcript analysis | ❌ Not built-in | ✅ Custom eval |
| Pattern extraction validation | ❌ Not built-in | ✅ Custom scorer |

**Assessment:** Inspect AI eliminates ~90% of custom infrastructure work. Parallax builds domain-specific scorers, leverages everything else.

### Limitations for Parallax

1. **Python-based:** Parallax is Claude Code skill-based (Markdown, not Python). Integration requires Python eval definitions.
2. **Batch timing:** 1-24 hour delays unsuitable for interactive review sessions (fine for offline evals).
3. **Learning curve:** Teams need to understand Dataset/Solver/Scorer patterns.

### Recommended Integration Strategy

**Phase 1: Parallel development**
- Build parallax:review skill using Claude Code native patterns
- Simultaneously build Inspect AI evals for validation
- Eval definitions in `evals/` directory (Python)

**Phase 2: Custom scorers**
- `severity_calibration_scorer.py` - validates severity distribution matches expectations
- `finding_quality_scorer.py` - LLM-as-judge for finding actionability, specificity, evidence
- `pattern_extraction_scorer.py` - validates semantic clustering quality
- `transcript_analysis_scorer.py` - detects agent configuration issues (Issue #37)

**Phase 3: Test suite**
- Test cases from `docs/reviews/*/` as datasets
- Ground truth: v3 review findings (87 findings, 12 patterns)
- Multi-model comparison: Sonnet vs Opus vs Haiku for reviewer selection

**Phase 4: Continuous validation**
- CI/CD integration: Run evals on PR branches
- Regression detection: New skill versions vs baseline
- Cost optimization: Batch API for all eval runs

---

## LangGraph Analysis

### Overview

- **Project:** LangChain team, open-source (MIT license)
- **Maturity:** Production-tested, enterprise deployments
- **Downloads:** 47M+ PyPI (part of LangChain ecosystem)
- **Documentation:** https://www.langchain.com/langgraph

### Core Architecture

DAG-based orchestration with three components:

1. **StateGraph**: Centralized workflow context (immutable state versioning)
2. **Nodes**: Agents, functions, decision points
3. **Edges**: Data flow paths (conditional, parallel, cyclic)

Graph compiled before execution (validation, cycle detection, optimization).

### Key Features

#### 1. Multi-Agent Orchestration Patterns

- Sequential workflows
- Scatter-gather parallelism
- Conditional branching
- Cyclic refinement loops
- Hierarchical agent structures
- Multi-actor applications

#### 2. State Management

- Centralized state object (agents process inputs, return updated state)
- Immutable data structures (prevents race conditions)
- Memory overhead grows with workflow scale
- "Time-travel" capabilities (rewind state, explore alternatives)

#### 3. Control Flow Mechanisms

- Conditional edges (route based on outputs/state)
- Parallel execution (multiple agents simultaneously)
- Subgraphs (modularity via grouping)
- Human-in-the-loop interrupts

#### 4. Production Features

- MIT-licensed (free to use)
- Zero-overhead performance design
- Token-by-token streaming
- Enterprise deployment (SaaS + VPC)
- Horizontal scalability (task queues, retries)
- LangSmith integration (observability, debugging)

### Strengths vs. Limitations

**Strengths:**
- Clear execution flow visualization
- Immutable state prevents certain concurrency issues
- Supports deterministic workflows
- Model-agnostic (Claude, GPT, Gemini, local models)
- Human-in-the-loop patterns
- External API integration

**Limitations:**
- Requires distributed systems expertise for production
- State management creates potential bottlenecks
- Configuration scales with complexity (simple = dozens of lines, production = hundreds)
- Schema updates tightly controlled (increases maintenance burden)
- No native low-code abstraction
- Debugging distributed agents demands deep understanding

**Critical Failure Points:**
- State corruption from simultaneous updates (race conditions)
- Deadlock from circular dependencies
- Memory exhaustion from long-duration workflows (immutable state versioning)
- Error propagation across shared states

### Use Cases: Good vs. Bad Fit

**Good fit:**
- Complex, deterministic workflows
- Multi-step reasoning with state dependencies
- Cyclic refinement (e.g., critique → revise → critique)
- Workflows requiring auditability/resumability
- Multi-model orchestration (GPT critique, Claude execution, Gemini grading)

**Bad fit:**
- Simple parallel execution (LangGraph adds unnecessary complexity)
- Independent agents without cross-communication
- Workflows without state dependencies
- Rapid prototyping (code-first adds friction)

### Parallax Review Pattern Analysis

**Parallax's review workflow:**
1. Spawn 6 reviewers in parallel
2. Each reviewer analyzes design independently
3. Synthesizer collects findings
4. Consolidate and classify findings
5. Generate report

**Key characteristics:**
- Reviewers don't communicate with each other
- No state dependencies between reviewers
- No cyclic refinement (single-pass review)
- Synthesizer is centralized (not distributed)
- Sequential phases (brainstorm → requirements → design → review → plan)

**LangGraph fit assessment:**
- ❌ No inter-reviewer state sharing needed
- ❌ No conditional branching based on reviewer outputs
- ❌ No cyclic workflows (critique loops)
- ❌ No complex dependencies
- ✅ Could visualize workflow as graph (but not a driver for choosing LangGraph)

**Verdict:** LangGraph is **overkill for parallax MVP**. The review pattern is straightforward parallel execution + centralized synthesis, which Claude Code native patterns already handle.

### When to Reconsider LangGraph

Revisit if parallax adds:
1. **Cross-iteration state tracking**: Findings from review N inform review N+1
2. **Inter-reviewer communication**: Reviewers debate/challenge each other
3. **Cyclic refinement**: Design → review → redesign → review loops
4. **Complex conditional branching**: Different review paths based on artifact type
5. **Auditability requirements**: Enterprise customers need workflow visualization

### Comparison to Claude Code Native Patterns

#### Claude Code Swarms (native)

**Architecture:**
- Team lead + independent teammates
- Shared task list with dependency tracking
- Direct agent messaging (peer-to-peer)
- No code required (natural language spawning)

**Strengths:**
- Zero setup (built into Claude Code)
- Natural language control
- Direct messaging between agents
- Task dependencies automatic

**Limitations:**
- Experimental (known issues: session resumption, task status lag)
- Claude-only (no multi-model support)
- One team per session
- No nested teams
- Split-pane mode requires tmux/iTerm2

**Best for:** Parallel exploration, competing hypotheses, cross-layer work

#### dispatching-parallel-agents (skill)

**Architecture:**
- Main agent spawns N independent subagents
- Subagents report back to main agent (no inter-subagent communication)
- Results synthesized by main agent

**Strengths:**
- Simple, proven pattern
- No framework overhead
- Works in any Claude Code session
- Lower token cost than Swarms

**Limitations:**
- No inter-subagent communication
- No shared task list
- Manual coordination by main agent

**Best for:** Independent tasks with centralized synthesis (exactly parallax's pattern)

#### Comparison Table

| Feature | LangGraph | Claude Swarms | dispatching-parallel-agents |
|---------|-----------|---------------|----------------------------|
| **Setup** | Code-first (Python) | Natural language | Natural language |
| **State management** | Centralized StateGraph | Shared task list | Main agent context |
| **Agent communication** | Via shared state | Direct messaging | Via main agent |
| **Multi-model** | ✅ Yes | ❌ Claude only | ❌ Claude only |
| **Cyclic workflows** | ✅ Yes | ❌ No | ❌ No |
| **Human-in-loop** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Auditability** | ✅ High (graph viz) | ⚠️ Medium | ⚠️ Medium |
| **Resumability** | ✅ Yes | ❌ Known issue | ❌ No |
| **Token cost** | High (state overhead) | Very high (N instances) | Medium (results only) |
| **Learning curve** | High (graph DSL) | Low (natural language) | Low (skill pattern) |
| **Production maturity** | ✅ Proven | ⚠️ Experimental | ✅ Proven |

**Parallax needs:**
- ✅ Independent reviewers (no inter-agent communication)
- ✅ Centralized synthesis (main agent collects findings)
- ✅ Simple workflow (spawn → collect → synthesize)
- ❌ No state dependencies
- ❌ No cyclic refinement
- ❌ No complex branching

**Verdict:** `dispatching-parallel-agents` is the right fit for parallax MVP. LangGraph adds complexity without solving a problem.

---

## Architecture Decision

### For Eval Framework (Issue #5)

**Decision:** Integrate Inspect AI

**Rationale:**
1. Provides 90% of needed infrastructure (runner, logs, metrics, batch API, multi-model)
2. LLM-as-judge patterns proven at scale (AISI, Anthropic, DeepMind)
3. Native Claude support (zero integration friction)
4. 50% cost reduction via batch API for eval runs
5. Parallax only needs to build domain-specific scorers (~10% of work)

**Implementation:**
- Eval definitions in `evals/` (Python, isolated from skill code)
- Custom scorers: severity calibration, finding quality, pattern extraction, transcript analysis
- Test cases from `docs/reviews/*/` as datasets
- Ground truth: v3 review (87 findings, 12 patterns)
- CI/CD integration for regression detection

**Scope reduction for Issue #5:**
- ❌ Build eval runner infrastructure
- ❌ Build logging/metrics system
- ❌ Build batch API integration
- ❌ Build multi-model comparison tooling
- ✅ Build custom scorers for parallax-specific validation
- ✅ Define test datasets from review artifacts
- ✅ Integrate Inspect AI into CI/CD pipeline

### For Orchestration

**Decision:** Use Claude Code native patterns (dispatching-parallel-agents), defer LangGraph

**Rationale:**
1. Parallax review pattern is simple parallel execution + centralized synthesis
2. No inter-reviewer communication needed
3. No state dependencies between reviewers
4. No cyclic workflows (single-pass review)
5. dispatching-parallel-agents skill already proven for this pattern
6. LangGraph adds code-first complexity without solving a problem
7. YAGNI: Build simplest thing that works, add complexity when needed

**When to reconsider LangGraph:**
- Cross-iteration state tracking becomes valuable
- Inter-reviewer debate/challenge patterns emerge
- Cyclic refinement loops (design → review → redesign → review)
- Enterprise auditability requirements (workflow visualization)
- Multi-model orchestration (GPT critique, Claude execution, Gemini grading)

**Current approach:**
- parallax:review skill spawns 6 reviewers via Task tool (parallel invocation)
- Each reviewer analyzes design independently
- Results collected by main agent
- Synthesizer consolidates findings
- No LangGraph, no Claude Swarms (overkill), just Task tool parallelism

---

## Next Steps

1. **Create ADR-005** documenting these decisions
2. **Update Issue #5** scope based on Inspect AI integration
3. **Create evaluation spike tasks:**
   - Set up Inspect AI in `evals/` directory
   - Build first custom scorer (severity calibration)
   - Define test dataset from v3 review
   - Run baseline eval (Sonnet vs Opus vs Haiku)
4. **Validate assumption:** Test dispatching-parallel-agents pattern with 6 reviewers + synthesizer
5. **Document integration patterns** in CLAUDE.md

---

## References

### Inspect AI
- **Docs:** https://inspect.aisi.org.uk/
- **Tutorial:** https://inspect.aisi.org.uk/tutorial.html
- **Model providers:** https://inspect.aisi.org.uk/providers.html
- **Batch mode:** https://inspect.aisi.org.uk/models-batch.html
- **Eval logs:** https://inspect.aisi.org.uk/eval-logs.html
- **GitHub:** https://github.com/UKGovernmentBEIS/inspect_ai
- **Hamel's guide:** https://hamel.dev/notes/llm/evals/inspect.html

### LangGraph
- **Main site:** https://www.langchain.com/langgraph
- **Docs:** https://docs.langchain.com/oss/python/langgraph/workflows-agents
- **Anthropic integration:** https://docs.langchain.com/oss/python/integrations/providers/anthropic
- **Multi-agent guide:** https://latenode.com/blog/ai-frameworks-technical-infrastructure/langgraph-multi-agent-orchestration/langgraph-multi-agent-orchestration-complete-framework-guide-architecture-analysis-2025
- **Benchmarking:** https://blog.langchain.com/benchmarking-multi-agent-architectures/

### Claude Code Swarms
- **Official docs:** https://code.claude.com/docs/en/agent-teams
- **Addy Osmani analysis:** https://addyosmani.com/blog/claude-code-agent-teams/
- **Gist guide:** https://gist.github.com/kieranklaassen/4f2aba89594a4aea4ad64d753984b2ea

### Cost & Pricing
- **Claude pricing guide:** https://www.nops.io/blog/anthropic-api-pricing/
- **Batch API savings:** https://www.aifreeapi.com/en/posts/claude-opus-4-pricing
- **Usage & Cost API:** https://platform.claude.com/docs/en/build-with-claude/usage-cost-api

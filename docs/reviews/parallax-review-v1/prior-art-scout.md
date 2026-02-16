# Prior Art Scout Review

## Prior Art Landscape

The design leverages Claude Code's native orchestration (TeammateTool/dispatching-parallel-agents) and defers to future phases on LangGraph/LangSmith/Promptfoo/Braintrust. It mentions adversarial-spec patterns and compound-engineering learning loops without adopting them. The key architectural choices are sound, but there are specific gaps where existing tools solve problems better than custom implementation would.

---

### Finding 1: Inspect AI Already Provides Multi-Agent Review Orchestration
- **Severity:** Important
- **Phase:** design
- **Section:** Reviewer Personas, Pipeline Integration
- **Issue:** The design builds custom parallel reviewer dispatch, finding consolidation, and severity classification. Inspect AI (already listed as an eval framework) has built-in multi-agent orchestration, finding deduplication, scoring normalization, and agent comparison features. This is being reimplemented rather than leveraged.
- **Why it matters:** Inspect AI is MIT-licensed, actively maintained (UK AISI project), supports Claude + Codex, and has 100+ pre-built evals including multi-agent patterns. Building custom orchestration means maintaining code for agent dispatch, result collection, retries, timeout handling, etc. Inspect AI handles this as infrastructure. The design claims "evaluate LangGraph when limits are hit" but doesn't evaluate whether Inspect AI already provides what's being built.
- **Suggestion:** Prototype reviewer personas as Inspect AI solvers with custom system prompts. Use Inspect's `multi_agent` pattern for parallel dispatch and `scorer` API for finding consolidation. Reserve custom orchestration only if Inspect's patterns prove insufficient. This positions parallax:review as prompt engineering (the novel contribution) rather than orchestration infrastructure (already solved). See: https://inspect.ai-safety-institute.org.uk/multi-agent.html

### Finding 2: LangSmith Provides Ready-Made Finding Classification and Human-In-The-Loop Review
- **Severity:** Important
- **Phase:** design
- **Section:** Synthesis, UX Flow
- **Issue:** The Synthesizer agent and interactive finding processing (accept/reject/discuss) are being custom-built. LangSmith (already in the tooling budget) provides dataset annotation, human feedback collection, finding tagging by phase/severity, and a web UI for accept/reject/comment workflows. This is production-grade infrastructure for exactly this use case.
- **Why it matters:** Building a custom finding queue, disposition tracking, and "discuss" conversation threading is complex UI/UX work. LangSmith's human review UI is battle-tested, supports team collaboration, and integrates with LangChain/LangGraph for automated classification. The 5k traces/month free tier covers months of prototyping. Custom implementation means building what LangSmith already provides.
- **Suggestion:** Evaluate LangSmith's annotation UI for finding processing. Each reviewer run becomes a trace, findings become tags, human disposition (accept/reject) becomes feedback. If the UI works, the skill becomes a thin wrapper that launches reviews and posts results to LangSmith for human processing. Reserve custom implementation if LangSmith's UI/workflow doesn't fit.

### Finding 3: Promptfoo Covers Reviewer Prompt Iteration and Severity Calibration
- **Severity:** Important
- **Phase:** design
- **Section:** Open Questions (severity calibration, persona tuning)
- **Issue:** The design lists "severity calibration across different personas" and "prompt engineering for personas" as open questions, with Promptfoo listed as an available tool but not mapped to these problems. Promptfoo is specifically built for prompt comparison, multi-model testing, and output consistency evaluation — exactly what's needed for tuning reviewer personas.
- **Why it matters:** Reviewer quality depends on prompt engineering. Testing whether "Assumption Hunter finds implicit assumptions" or "Edge Case Prober assigns Critical vs Important consistently" requires systematic prompt iteration with side-by-side comparison. Doing this manually (edit prompt, run review, check output, repeat) is slow and subjective. Promptfoo automates this: define test cases, run N prompt variants, score outputs, surface regressions.
- **Suggestion:** Use Promptfoo for reviewer persona development. Each persona becomes a prompt variant, test cases are design docs with known flaws (from the Second Brain test case), and assertions check whether findings match expected severity/phase. This makes "optimal number of personas" and "severity calibration" empirical rather than subjective. Already budgeted (10k probes/month free tier).

### Finding 4: Tree-Sitter and Semgrep Are Listed But Not Integrated for Code-Aware Review
- **Severity:** Minor
- **Phase:** plan
- **Section:** Tooling
- **Issue:** The problem statement lists `tree-sitter` (AST parsing) and `semgrep` (security patterns) under "Investigate" but the design doc has no integration points. Yet the plan stage includes "Systems Architect" and "Code Realist" personas reviewing implementation plans, which would benefit from AST-level analysis (dependency ordering, API contract violations) and security pattern detection (credential leaks, unsafe defaults).
- **Why it matters:** Plan-stage review of implementation steps could leverage static analysis. For example, detecting that a plan modifies a file before reading it (dependency order violation) or writes secrets to a non-gitignored path (security risk). These are mechanical checks that don't require LLM inference. Using Sonnet tokens for mechanical analysis is expensive; using tree-sitter + semgrep is free.
- **Suggestion:** Defer to plan-stage implementation, but design the reviewer interface to accept optional tool outputs. If semgrep flags a security pattern in the planned changes, pass that to the Security Reviewer as context. If tree-sitter detects dependency conflicts, pass that to Code Realist. Reviewers interpret tool findings, tools don't replace reviewers. This is the standard linter-plus-human-review pattern.

### Finding 5: Braintrust LLM-as-Judge for "Design Quality Scoring" Is Undefined
- **Severity:** Important
- **Phase:** calibrate
- **Section:** Key Frameworks (Braintrust)
- **Issue:** Braintrust is listed as "LLM-as-judge for design quality scoring" but there's no definition of what "design quality" means as a metric. The design doc defines finding severity (Critical/Important/Minor) and verdict (proceed/revise/escalate), but doesn't specify how Braintrust would score these or what the eval success criteria are.
- **Why it matters:** LLM-as-judge requires a rubric. "Did the reviewers catch the known flaw?" is measurable. "Is the design high quality?" is not — it's subjective without operationalization. If Braintrust is scoring reviewer performance (precision/recall on known issues), that's one rubric. If it's scoring design artifact quality (completeness, clarity, consistency), that's a different rubric. The design assumes Braintrust is useful but doesn't define the evaluation contract.
- **Suggestion:** Defer Braintrust integration until eval framework design (parallax:eval). When that skill is scoped, define concrete metrics: reviewer precision (% of flagged issues that are real), recall (% of known issues that were caught), severity agreement (Cohen's kappa across reviewers), etc. Use Inspect AI's built-in scorers first; add Braintrust only if custom LLM-judge logic is needed beyond Inspect's capabilities.

### Finding 6: Git Commit Per Review Iteration Could Use `gh api` for Metadata Enrichment
- **Severity:** Minor
- **Phase:** design
- **Section:** Output Artifacts, Pipeline Integration
- **Issue:** The design commits review artifacts to git for version tracking and diffability. This is sound, but git commits alone don't capture review metadata (which reviewers flagged what, disposition outcomes, time spent per finding). The problem statement lists `gh` (GitHub CLI) as an available tool and CLAUDE.md mentions using `gh` for GitHub operations, but there's no integration point for enriching commits with structured metadata.
- **Why it matters:** Diffs show what changed between reviews, but not why or who decided. If a finding was rejected in iteration 1 and reappears in iteration 2, git history won't surface that pattern. GitHub's commit API supports custom metadata via trailers, and `gh api` can post review summaries as commit comments or gist links. This makes review history queryable (e.g., "show me all Critical findings rejected by the user in the past month").
- **Suggestion:** Append review metadata to commit messages as structured trailers (e.g., `Reviewers: assumption-hunter,edge-case-prober` and `Findings: 3C/5I/2M`). Optionally post full `summary.md` as a gist and link it in the commit message. This is low-effort (gh CLI already available) and makes review history machine-readable for future analytics. Pure enhancement, not blocking.

---

## Blind Spot Check

**What I might have missed:**
- **Claude-specific orchestration patterns** — I'm flagging standard multi-agent frameworks (Inspect AI, LangSmith) but not evaluating whether Claude Code's native TeammateTool or the superpowers plugin's `dispatching-parallel-agents` provides equivalent functionality with less integration overhead. The design may be correctly choosing native tools over external frameworks for simplicity, but that tradeoff isn't explicit.
- **Prompt caching architecture** — The problem statement emphasizes prompt caching (90% cost reduction) with stable system prompts, but I didn't evaluate whether the proposed reviewer persona structure (persona + methodology + output format as cacheable prefix) aligns with Inspect AI or LangSmith's caching behavior. If those frameworks don't expose cache control, the custom implementation may be necessary.
- **Test case validation** — I flagged missing evaluation metrics but didn't check whether the four listed test cases (Second Brain, Semantic Memory Search, etc.) already provide the ground truth data needed to validate reviewer performance. If those test cases include known flaws with documented severity, the eval rubric might be implicit.
- **Build-vs-buy for novel contributions** — I'm biased toward leveraging existing tools, but the design's core claim is that finding classification (routing back to the phase that failed) is novel. If Inspect AI and LangSmith don't support phase-based classification, that's justification for custom synthesis logic. I didn't confirm whether those tools already do this.

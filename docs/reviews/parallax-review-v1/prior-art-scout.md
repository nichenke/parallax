# Prior Art Scout Review

## Changes from Prior Review

**Previously flagged findings:**
- **Finding 30 (Important): Inspect AI Already Provides Multi-Agent Review Orchestration** — Still an issue. The design does not address whether Inspect AI's orchestration patterns should be leveraged.
- **Finding 41 (Minor): LangSmith Provides Ready-Made Finding Classification and Human-In-The-Loop Review** — Still an issue. Not evaluated for finding processing UX.

**New findings identified in this review:**
- Multiple mature orchestration frameworks with specific design patterns that map directly to parallax:review's needs (LangGraph stateful workflows, Inspect AI multi-agent primitives)
- Industry-standard practices for requirements refinement (MoSCoW), decision documentation (ADR/RFC), and finding classification that parallax is reinventing
- Production-grade tools for every major component being custom-built (Braintrust for scoring, Promptfoo for adversarial testing, LangSmith for annotation)
- Architectural patterns from Google's 8 multi-agent design patterns that directly address parallel reviewer orchestration
- EveryInc's Compound Engineering demonstrates the exact learning loop pattern described in problem statement requirements

**Resolution status:** None of the prior findings have been addressed. This re-review surfaces additional prior art that strengthens those findings and adds new ones.

## Prior Art Landscape

The 2026 multi-agent AI ecosystem has matured significantly. Three categories of prior art are directly relevant:

### 1. Multi-Agent Orchestration Frameworks (Infrastructure Layer)
- **Inspect AI** (UK AISI, MIT license): Multi-agent primitives, handoff patterns, agent-as-tool composition, supports Claude + Codex, 100+ pre-built evals
- **LangGraph** (LangChain, MIT license): Stateful graph workflows, human-in-the-loop gates, persistent memory, conditional branching
- **LangSmith** (LangChain, free tier): Annotation queues, human feedback UI, finding tagging by severity/phase, team collaboration
- **Braintrust** (free tier): LLM-as-judge scoring, trace-driven evaluation, automated review scoring, 1M spans/month free
- **Promptfoo** (open source): Adversarial probe generation, 50+ vulnerability types, OWASP LLM Top 10, 10k probes/month free

All five tools are already in the CLAUDE.md tooling budget. None are being evaluated as implementation substrates.

### 2. Multi-Agent Review Systems (Application Layer)
- **Compound Engineering** (EveryInc, 8.9k stars): 15 review agents, `/compound` learning loop for capturing patterns, Plan → Work → Review → Compound cycle
- **adversarial-spec** (zscole, 487 stars): Multi-LLM debate for spec refinement, skepticism of early consensus, model personas, iterative refinement until consensus
- **Qodo** (2026): 15+ specialized review agents for code quality, context-aware maintainability, AI pre-review before human reviewers (81% quality improvement per 2025 report)

All three demonstrate production patterns for parallel reviewer dispatch, finding consolidation, and iterative refinement. None are integrated or evaluated.

### 3. Industry Standards and Patterns
- **ADR (Architecture Decision Records)**: Lightweight format for capturing design decisions with context, alternatives, consequences — standard practice in 2026
- **MoSCoW prioritization**: Must/Should/Could/Won't framework for requirements refinement, explicitly documents anti-goals via "Won't-Have" category
- **Google's 8 Multi-Agent Design Patterns** (2026): Sequential, parallel, loop patterns with role-based agents (Parser, Critic, Dispatcher) — modular, testable, reliable
- **OWASP LLM Top 10 + NIST AI RMF**: Industry standards for adversarial testing and vulnerability classification that Promptfoo implements

Parallax's problem statement requires "outcome-focused requirement refinement" and "ADR-style finding documentation" but the design doesn't reference MoSCoW or ADR patterns despite both being industry standards.

### Key Finding: Build vs Leverage Imbalance

CLAUDE.md states: "BUILD adversarial review (novel), LEVERAGE LangGraph + Inspect AI + Claude Code Swarms (mature)."

Current design: BUILD orchestration infrastructure + finding consolidation + severity classification + annotation UI + learning loop.

Novel contribution per CLAUDE.md: "Finding classification routes errors back to the pipeline phase that failed."

**Gap:** Parallax is building the entire stack (infrastructure + application + standards) when mature solutions exist for 80% of it. The 20% that's novel (phase classification logic, persona prompt engineering) could be built on top of existing frameworks.

## Findings

### Finding 1: Inspect AI Multi-Agent Patterns Already Solve Orchestration Architecture
- **Severity:** Critical
- **Phase:** design (primary), calibrate (contributing — build vs leverage decision should have been explicit)
- **Section:** Entire design — Reviewer Personas, Synthesis, UX Flow, Pipeline Integration
- **Issue:** The design custom-builds parallel reviewer dispatch, finding consolidation, retry logic, timeout handling, and result aggregation. Inspect AI (already in tooling budget, MIT license, supports Claude + Codex) provides `multi_agent` pattern with handoff primitives, agent-as-tool composition, built-in retry/timeout, and trace collection. The design doc states "evaluate LangGraph when limits are hit" but doesn't evaluate whether Inspect AI already provides what's being built. Prior Art Scout flagged this in Finding 30 (Important), but it's Critical because it affects the entire architecture.
- **Why it matters:** Building custom orchestration means maintaining code for agent dispatch, result collection, retries, timeout handling, progress tracking, cost estimation, and failure recovery. This is 40-60% of the implementation surface area per Feasibility Skeptic's estimate. Inspect AI is production-grade infrastructure (UK AI Safety Institute project, used by AISI for agent evaluations), actively maintained, and designed specifically for multi-agent LLM evaluation. Using Inspect positions parallax:review as domain-specific prompt engineering (the novel contribution) rather than infrastructure work (already solved). CLAUDE.md explicitly says "LEVERAGE Inspect AI" but design doesn't reference it.
- **Suggestion:** Evaluate Inspect AI as the implementation substrate. Prototype reviewer personas as Inspect solvers with custom system prompts. Use Inspect's `multi_agent` pattern for parallel dispatch, `scorer` API for finding consolidation, and trace collection for cost tracking. Reserve custom orchestration only if Inspect's patterns prove insufficient after prototyping. See: [Inspect AI multi-agent documentation](https://inspect.aisi.org.uk/agents.html). This shifts implementation focus from plumbing (weeks) to personas (days), and validates CLAUDE.md's "BUILD adversarial review, LEVERAGE mature frameworks" principle.
- **Iteration status:** Still an issue (escalated from prior Finding 30)

### Finding 2: LangGraph Solves Stateful Workflow and Human-in-the-Loop Gates
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** UX Flow (human checkpoints), Interactive Finding Processing, Iteration Loops
- **Issue:** The design describes stateful workflows (process findings one-at-a-time, maintain disposition state, resume after discussion, track cross-iteration finding history) and human approval gates (verdict → human processing → wrap up) but custom-builds the state management. LangGraph (already in tooling budget, MIT license) is specifically designed for stateful, controllable AI workflows with built-in graph-based state management, conditional transitions, human-in-the-loop pause points, and persistent memory across sessions. Problem statement explicitly lists LangGraph as "natural fit for pipeline control" but design doesn't address it.
- **Why it matters:** State management for "discuss" mode (Finding 6 in prior review, flagged Critical by 4 reviewers) is estimated at 30-50% of implementation time. LangGraph provides this as a core primitive: workflows pause for human input, context persists, and conversation resumes from exact state. Additionally, cross-iteration finding tracking (Finding 5 in prior review, Critical) requires persistent state across review runs — LangGraph's state graphs support this natively. Custom state management in a CLI skill is complex (modal UI, conversation threading, exit conditions) and error-prone. LangGraph is battle-tested production infrastructure with 20k+ stars, maintained by LangChain team.
- **Suggestion:** Evaluate LangGraph for the skill's control flow. Model the review process as a state graph: dispatch reviewers (parallel) → synthesize findings (sequential) → human processing loop (conditional, stateful) → wrap up. Use LangGraph's `interrupt` for human approval gates and `state` for finding disposition tracking. See: [LangGraph workflows and agents documentation](https://docs.langchain.com/oss/python/langgraph/workflows-agents). This eliminates custom state management, makes "discuss" mode tractable, and provides automatic tracing for debugging. If LangGraph proves too heavyweight for a single skill, defer to orchestrator phase (where pipeline state is essential).
- **Iteration status:** New finding

### Finding 3: LangSmith Annotation UI Solves Finding Processing UX
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Step 5: Process Findings, Interactive Finding Processing, Summary Format (dispositions)
- **Issue:** The design custom-builds interactive finding processing (accept/reject/discuss one-at-a-time in CLI) with disposition tracking in markdown. LangSmith (already in tooling budget, 5k traces/month free tier) provides production-grade annotation queues with web UI for human feedback, finding tagging by severity/phase, accept/reject/comment workflows, team collaboration, and historical disposition tracking. Prior Art Scout flagged this in Finding 41 (Minor) but it's Important because it directly addresses multiple prior Critical findings: Finding 2 (async workflows), Finding 6 (discuss mode complexity), Finding 14 (large finding counts overwhelming interactive processing).
- **Why it matters:** Custom CLI-based finding processing has UX limitations: no async mode (user must be present), no filtering/batching (40+ findings processed one-at-a-time), no collaboration (single user), no historical view (dispositions in markdown files). LangSmith's annotation UI supports: async review (SMEs process findings on their schedule), filtering (show only Critical, show only from specific reviewer), batch operations (accept all Minor), team collaboration (multiple reviewers), and integration with LangChain/LangGraph traces (each finding links back to the reviewer run that produced it). This is production infrastructure used by thousands of teams.
- **Suggestion:** Evaluate LangSmith's annotation queues for finding processing. Each reviewer run becomes a trace, findings become annotations, human disposition (accept/reject with notes) becomes feedback. Skill writes findings to LangSmith, user processes them in the web UI (async-first), and skill reads back dispositions to update summary.md. If UI/workflow doesn't fit parallax's needs, fall back to custom implementation. But default to leverage before build. See: [LangSmith human feedback documentation](https://apxml.com/courses/langchain-production-llm/chapter-5-evaluation-monitoring-observability/human-feedback-annotation). This also addresses Finding 2 (async workflows) and Finding 14 (bulk operations) from prior review without custom development.
- **Iteration status:** Still an issue (escalated from prior Finding 41)

### Finding 4: Braintrust LLM-as-Judge Solves Severity Normalization
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Synthesis (severity ranges, deduplication), Verdict Logic
- **Issue:** The design describes synthesizer responsibilities (deduplicate findings, reconcile severity ranges, classify by phase) but treats it as a custom prompt engineering problem. Braintrust (already in tooling budget, 1M spans/10k scores free tier) is specifically designed for LLM-as-judge evaluation with autoevals library for scoring, chain-of-thought reasoning for severity assessment, and configurable scorers for classification tasks. Prior review Finding 8 (Critical) and Finding 13 (Important) identify that synthesizer role requires judgment (not "purely editorial") and severity ranges create verdict ambiguity. These are standard LLM-as-judge problems with production tooling.
- **Why it matters:** Synthesizer must: (1) judge if two findings are "the same issue" (semantic similarity + deduplication threshold), (2) reconcile severity ranges when reviewers disagree (consensus scoring), (3) classify findings by phase (multi-class classification with reasoning). All three are LLM-as-judge tasks. Custom implementation means writing prompts, managing model calls, handling edge cases, validating outputs. Braintrust provides autoevals library with built-in scorers for similarity, consensus, and classification, plus chain-of-thought debugging for when scores disagree. Using Braintrust positions synthesis as a standard evaluation workflow (traces → scorers → results) rather than custom orchestration.
- **Suggestion:** Evaluate Braintrust for synthesis logic. Each reviewer output becomes a trace. Scorers classify findings (deduplication scorer identifies duplicates via semantic similarity, severity scorer reconciles ranges via consensus voting, phase scorer assigns pipeline phase via chain-of-thought classification). Synthesizer becomes a Braintrust experiment that runs scorers and produces summary.md from results. See: [Braintrust scorers documentation](https://www.braintrust.dev/docs/guides/functions/scorers) and [autoevals library](https://github.com/braintrustdata/autoevals). This also provides free observability (all synthesis runs traced), debugging (inspect scorer reasoning), and tuning (compare scorer configurations). If Braintrust's model is too heavyweight for synthesis, fall back to custom prompts.
- **Iteration status:** New finding

### Finding 5: Promptfoo Adversarial Testing Is Exact Prior Art for Reviewer Personas
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing — should have researched adversarial testing tools)
- **Section:** Reviewer Personas, Open Questions (optimal persona count)
- **Issue:** The design defines 6-9 reviewer personas with adversarial lenses (Assumption Hunter, Edge Case Prober, etc.) and flags persona tuning as an empirical question for the eval framework. Promptfoo (already in tooling budget, open source, 10k probes/month free) is specifically designed for adversarial LLM testing with 50+ vulnerability types, automated probe generation, OWASP LLM Top 10 coverage, and plugin-based test strategies. The design treats reviewer persona development as custom prompt engineering but it's a specialized domain (adversarial testing) with production tooling and industry standards.
- **Why it matters:** Reviewer personas are adversarial probes applied to design artifacts rather than LLM outputs, but the underlying pattern is identical: generate diverse attacks (reviewers), stress-test the target (design), classify vulnerabilities (findings by phase). Promptfoo's plugin architecture maps directly to parallax personas (each plugin = reviewer lens, strategies = finding generation approaches). Using Promptfoo's patterns (or collaborating with their community) accelerates persona development and validates against industry standards (OWASP, NIST AI RMF). Additionally, Promptfoo supports evaluation of LangGraph agents, so integration with Finding 2 (LangGraph for orchestration) is proven.
- **Suggestion:** Study Promptfoo's adversarial testing architecture before finalizing reviewer personas. Map parallax personas to Promptfoo vulnerability types (e.g., Assumption Hunter → implicit-assumptions probe, Edge Case Prober → boundary-condition probe). Evaluate whether Promptfoo's test generation patterns can accelerate persona prompt development. Consider contributing parallax-specific probes back to Promptfoo (design-time vulnerabilities vs runtime). See: [Promptfoo adversarial testing architecture](https://www.promptfoo.dev/docs/red-team/architecture/). This doesn't mean using Promptfoo as infrastructure (parallax targets design docs, not LLM outputs), but leveraging their adversarial testing methodology and 50+ vulnerability taxonomy as a reference.
- **Iteration status:** New finding

### Finding 6: Compound Engineering Is Exact Prior Art for Learning Loop
- **Severity:** Important
- **Phase:** calibrate (primary — this should have been in requirements as explicit leverage target)
- **Section:** Problem Statement "Correction Compounding", Reviewer Calibration Feedback Loop (prior Finding 29)
- **Issue:** Problem statement describes "correction compounding" where false negatives/positives become permanent calibration rules in reviewer prompts, creating a learning loop that improves over time. EveryInc's Compound Engineering plugin (8.9k stars, production use at Every) implements exactly this pattern: Plan → Work → Review → Compound → Repeat, where the Review step captures learnings and the Compound step feeds them back into the system. The design mentions calibration (Finding 29 from prior review, deferred to eval phase) but doesn't acknowledge this is a solved pattern with production tooling.
- **Why it matters:** Compound Engineering demonstrates that reviewer learning loops are viable and valuable in production (Every uses it daily for all development work). Their `/compound` skill captures patterns from review cycles and makes future reviews better. This validates parallax's hypothesis but also shows parallax is reinventing a mature pattern. Additionally, Compound Engineering's 15 review agents are all implementation-focused (code review), whereas parallax targets design review — complementary domains, not competitors. Collaboration opportunity: propose design-stage review agents to EveryInc (extending their pipeline upstream), or study their learning loop architecture before building parallax's version.
- **Suggestion:** Study Compound Engineering's learning loop implementation before building parallax's calibration mechanism. Read the [Compound Engineering methodology guide](https://every.to/guides/compound-engineering) and review their [plugin source code](https://github.com/EveryInc/compound-engineering-plugin). Key questions: (1) How do they capture learnings from review cycles? (2) How do they structure calibration data to feed back into agents? (3) What's their prompt update workflow? (4) Do they version prompts to track calibration history? Use their patterns as reference architecture. Consider: propose collaboration where parallax contributes design-stage reviewers to Compound Engineering, positioning parallax:review as upstream extension (requirements/design) of their downstream focus (implementation/testing).
- **Iteration status:** New finding

### Finding 7: adversarial-spec Demonstrates Multi-LLM Debate Pattern
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Reviewer Personas (prior Finding 26: adversarial pairs), Contradictions (synthesis)
- **Issue:** The design uses parallel personas with domain-scoped lenses (coverage-based). Prior review Finding 26 (Important, accepted) suggested adversarial pairs with opposing incentives (stance-based) to force genuine debate. adversarial-spec (zscole, 487 stars) implements exactly this: multi-LLM debate where models critique each other iteratively until consensus, with explicit skepticism of early consensus and model personas defending different positions. This is production code demonstrating the adversarial pairs pattern works.
- **Why it matters:** adversarial-spec validates that stance-based adversarial review (multiple agents arguing) produces better outcomes than coverage-based review (multiple agents inspecting). Their approach: Claude drafts spec → opponents (GPT, Gemini, etc.) critique in parallel → Claude synthesizes and critiques → revise → repeat until consensus. The key insight: debate surfaces gaps better than independent inspection. Prior Finding 26 was accepted with priority for early eval, but this finding shows the pattern is already proven in production. Study their implementation before reinventing.
- **Suggestion:** Read [adversarial-spec source code](https://github.com/zscole/adversarial-spec) and methodology. Key patterns to study: (1) How do they frame opponent critiques? (2) How do they detect consensus vs genuine disagreement? (3) How many debate rounds before convergence? (4) Do they use same model with different personas, or different models? (5) What's their synthesis logic? Use these answers to inform parallax's persona design (Finding 26 implementation). Consider: prototype 2-3 adversarial pairs (Ship Fast vs Ship Right, User-Centric vs Operator-Centric) using adversarial-spec's debate pattern and compare finding quality against current coverage-based personas. This addresses prior Finding 26 with proven reference implementation.
- **Iteration status:** New finding

### Finding 8: Google's 8 Multi-Agent Design Patterns Map to Parallax Architecture
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Pipeline Integration, Reviewer Personas (role-based agents)
- **Issue:** The design describes parallel reviewer dispatch, synthesizer consolidation, and human approval gates but doesn't reference industry patterns for multi-agent architectures. Google published 8 fundamental multi-agent design patterns in 2026 (sequential, loop, parallel execution with role-based agents like Parser, Critic, Dispatcher) that map directly to parallax's architecture. The design custom-builds these patterns without acknowledging they're standard.
- **Why it matters:** Google's patterns are industry-validated approaches for building modular, testable, reliable multi-agent systems. Parallax architecture maps to: (1) **Parallel pattern** for reviewer dispatch (multiple Critic agents), (2) **Sequential pattern** for pipeline stages (survey → calibrate → design → review), (3) **Dispatcher pattern** for skill invocation (orchestrator routes to appropriate stage). Using standard patterns makes the architecture more recognizable to engineers familiar with multi-agent systems, easier to debug (well-understood failure modes), and simpler to extend (new personas are new Critic agents). Additionally, Google's Agent Development Kit (ADK) provides reference implementations.
- **Suggestion:** Map parallax architecture to Google's 8 patterns and document the mapping in design doc. Reviewer personas = **Critic agents** (evaluate input against criteria). Synthesizer = **Parser agent** (consolidate and structure findings). Orchestrator (future) = **Dispatcher agent** (route to appropriate review stage). This provides common vocabulary with industry standards and validates architectural choices. See: [Google's 8 Multi-Agent Design Patterns](https://www.infoq.com/news/2026/01/multi-agent-design-patterns/). Additionally, study Agent Development Kit patterns for inspiration on persona composition and failure handling.
- **Iteration status:** New finding

### Finding 9: MoSCoW Is Industry Standard for Requirement Refinement
- **Severity:** Important
- **Phase:** calibrate (primary — requirements doc should reference this explicitly)
- **Section:** Problem Statement "Requirement Refinement", Missing from Design
- **Issue:** Problem statement requires "MoSCoW (Must / Should / Could / Won't) or similar prioritization framework" and "Anti-goals should be explicit." Design doesn't implement requirement refinement (deferred to parallax:calibrate skill) but also doesn't acknowledge MoSCoW is an industry standard (created at Oracle, used in Agile/Scrum/DSDM, standard practice in 2026). Anti-goals mapping: MoSCoW's "Won't-Have" category serves this purpose — explicitly defining what will NOT be delivered to manage scope creep.
- **Why it matters:** When parallax:calibrate is built, reinventing requirement prioritization is unnecessary. MoSCoW has 25+ years of production use, well-documented patterns, and widespread recognition in engineering teams. Using the standard framework provides: (1) common vocabulary ("this is a Must-Have vs Should-Have"), (2) proven facilitation techniques (how to run MoSCoW workshops), (3) existing tooling (project management software supports MoSCoW natively). Additionally, "Won't-Have" as anti-goals is more actionable than custom anti-goal formulation — it's tied directly to prioritization decisions.
- **Suggestion:** When building parallax:calibrate (requirement refinement skill), use MoSCoW as the default framework. Don't reinvent prioritization. Study existing MoSCoW facilitation guides and adapt for AI-assisted requirement sessions. See: [MoSCoW prioritization comprehensive guide](https://hypersense-software.com/blog/2024/12/03/moscow-prioritization-guide/) and [Won't-Have category for scope management](https://www.productplan.com/glossary/moscow-prioritization/). Key design question: should calibrate skill (1) educate user on MoSCoW and facilitate human-led prioritization, or (2) suggest initial MoSCoW classification based on problem statement and let user refine? Evaluate both during prototyping.
- **Iteration status:** New finding

### Finding 10: ADR Is Industry Standard for Design Decision Documentation
- **Severity:** Important
- **Phase:** calibrate (primary — requirements doc should reference this explicitly)
- **Section:** Problem Statement "Document Chain as RFC", "ADR-style finding documentation"
- **Issue:** Problem statement requires "ADR-style finding documentation — each review cycle produces a record of what was found, what was decided, and why" and describes document chain as "something RFC-like." Design doesn't specify output format for decision documentation. ADR (Architecture Decision Records) is an industry standard lightweight format for capturing design decisions with context, alternatives considered, and consequences. Problem statement name-drops ADR but design doesn't use the standard format.
- **Why it matters:** ADRs have standardized structure (Status, Context, Decision, Consequences, Alternatives), are version-controlled alongside code, and are widely recognized in 2026 engineering teams. Using ADR format for review summaries provides: (1) consistent structure for finding documentation, (2) explicit alternatives-considered section (critical for understanding why one approach was chosen over another), (3) consequences section (what's the blast radius of accepting vs rejecting this finding?), (4) status tracking (proposed → accepted → superseded). This is exactly what parallax needs for review findings but more mature than custom markdown format.
- **Suggestion:** When designing summary.md format (or improving current format), adopt ADR structure for findings. Each finding becomes a mini-ADR: **Context** (section of design, why this matters), **Decision** (accept/reject disposition with rationale), **Alternatives Considered** (reviewer suggestion vs user's approach), **Consequences** (what happens if addressed vs deferred), **Status** (open → accepted → implemented). This positions review findings as architecture decisions (which they are) and integrates with existing ADR tooling/workflows. See industry references on [ADR format and version control](https://www.sciencedirect.com/topics/computer-science/architecture-validation). Also addresses prior Finding 24 (Document Chain RFC Mechanism) with proven standard.
- **Iteration status:** New finding

### Finding 11: AI Agents for Architecture Validation Already Exist
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Reviewer Personas (architectural lens), Requirements Stage "Systems Architect" persona
- **Issue:** Design includes Systems Architect persona (plan stage) and implies architectural review is part of parallax's scope. AI agents are already being used in production (2026) to enforce architectural standards — reviewing code in PRs for violations like direct database calls from presentation layers, validating architecture diagrams against real-world configs, and running in CI/CD pipelines. Parallax positions itself as novel ("no production tools exist for this" per CLAUDE.md) but architectural validation agents are in production.
- **Why it matters:** If architectural validation agents already exist for code review, parallax's value proposition should be more precise: design-time architectural review (before code exists) vs implementation-time validation (after code written). The gap: existing tools validate code against architecture, parallax validates architecture against requirements. This is a genuine gap but the design doesn't articulate the distinction clearly. Risk: users evaluate parallax against existing architectural validation tools and see duplication rather than complementary positioning.
- **Suggestion:** Clarify parallax's positioning relative to existing architectural validation tools. Parallax operates upstream: it validates design decisions before implementation, catching architectural flaws when fixing them is cheap (design doc revision vs code refactor). Existing tools (Axivion, SonarQube, AI agents in PRs) operate downstream: validating implementation matches architecture. Complementary, not competitive. Update CLAUDE.md's "no production tools exist" claim to be more precise: "no production tools for design-time adversarial review" (accurate) vs "no production tools for architectural review" (false). See: [AI agents enforcing architectural standards in PRs](https://medium.com/@dave-patten/using-ai-agents-to-enforce-architectural-standards-41d58af235a0).
- **Iteration status:** New finding

### Finding 12: Bug Triage Severity Classification Is Standard Prior Art
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Synthesis (severity classification), Verdict Logic
- **Issue:** Design treats severity classification (Critical/Important/Minor) and deduplication as novel synthesis problems. Bug triage in software testing has 30+ years of established patterns for severity classification (based on impact and complexity), automated triage systems (assign severity via rules or ML models), and deduplication methods (semantic similarity of bug reports). Parallax is applying bug triage patterns to design findings but doesn't reference this prior art.
- **Why it matters:** Bug triage literature provides proven heuristics for severity classification (e.g., Critical = system failure, Major = feature broken, Minor = cosmetic), consensus-based severity assignment when multiple reviewers disagree, and automated deduplication via text similarity. These are solved problems. Using bug triage patterns accelerates synthesis logic design and provides reference implementations to study. Additionally, bug tracking tools (Jira, Linear, GitHub Issues) have built-in severity workflows that users are familiar with — adopting similar patterns reduces cognitive load.
- **Suggestion:** Study bug triage severity classification standards before finalizing synthesis logic. Map parallax findings to bug triage patterns: **Critical** = design cannot proceed (blocking), **Important** = design flaw that should be fixed (non-blocking), **Minor** = improvement opportunity (defer). Use consensus voting for severity ranges (if 2+ reviewers flag Critical, classify as Critical). See: [Bug severity classification guide](https://www.frugaltesting.com/blog/how-to-classify-bug-severity-in-qa-testing-a-complete-guide-for-software-teams/) and [automated triage methods](https://www.mdpi.com/2076-3417/13/15/8788). This provides battle-tested heuristics rather than custom prompt engineering.
- **Iteration status:** New finding

### Finding 13: Qodo Demonstrates Production Multi-Agent Code Review at Scale
- **Severity:** Minor
- **Phase:** calibrate (contributing — useful reference for value proposition)
- **Section:** Problem Statement (pain points, value hypothesis)
- **Issue:** Design positions multi-agent review as experimental/novel but Qodo (production tool, 2026) uses 15+ specialized review agents for code quality with measurable impact: 81% quality improvements (up from 55%), AI pre-review before human reviewers, context-aware maintainability. This validates parallax's hypothesis (multi-agent review works) but shows it's proven at scale for implementation review. Parallax's gap: design review (upstream).
- **Why it matters:** Qodo provides empirical evidence that parallax's architecture (multiple specialized reviewers in parallel) produces measurable quality gains. This strengthens the value proposition but also narrows the novelty claim. Parallax should position as "Qodo for design-time" — applying proven multi-agent review patterns to earlier lifecycle phases where fixing issues is 10-100x cheaper. Additionally, Qodo's 81% quality improvement metric is a useful benchmark: parallax evals should measure design quality improvement pre/post review to validate similar impact.
- **Suggestion:** Reference Qodo as validation that multi-agent review produces measurable quality gains. Position parallax as upstream application of proven patterns (design-time vs code-time). Steal their metrics approach: measure quality improvement (% of designs improved by review) as primary success criterion. See: [Qodo multi-agent code review results](https://www.clickittech.com/ai/multi-agent-system-architecture/). This addresses "does multi-agent review actually work?" with production data (yes, 81% improvement) and focuses parallax's novelty claim on design-phase application (gap in market).
- **Iteration status:** New finding

### Finding 14: OWASP LLM Top 10 Provides Adversarial Testing Taxonomy
- **Severity:** Minor
- **Phase:** design (contributing — useful for persona design)
- **Section:** Reviewer Personas (adversarial lenses)
- **Issue:** Design defines 6 design-stage personas with adversarial lenses but doesn't reference industry standards for adversarial testing. OWASP LLM Top 10 and NIST AI Risk Management Framework provide taxonomies of vulnerabilities that map to design flaws (e.g., prompt injection → assumption injection, model inversion → requirement contradictions). Promptfoo implements these standards. Parallax personas are domain-scoped (what to look for) rather than standards-aligned.
- **Why it matters:** Aligning reviewer personas with industry vulnerability taxonomies provides: (1) standard vocabulary for findings (e.g., "this is an implicit assumption, categorized as undocumented dependency"), (2) validation that personas cover known vulnerability types, (3) comparison against security testing standards. Additionally, if parallax eventually reviews AI system designs (likely use case), OWASP LLM Top 10 is directly applicable. Considering this early prevents redesign later.
- **Suggestion:** Map parallax reviewer personas to OWASP LLM Top 10 / NIST AI RMF categories where applicable. Not all will map (design-time vulnerabilities differ from runtime), but some will (e.g., Assumption Hunter → undocumented dependencies, Edge Case Prober → boundary condition failures). Document the mapping to validate persona coverage and identify gaps. See: [Promptfoo OWASP LLM Top 10 implementation](https://www.promptfoo.dev/docs/red-team/) for reference. This is low-priority for prototype (defer to eval phase) but worth flagging as future alignment work.
- **Iteration status:** New finding

## Blind Spot Check

Given my focus on existing solutions and standards, what might I have missed?

**Novel aspects that genuinely require custom work:**
1. **Phase classification logic** — routing findings back to the failed pipeline phase (survey/calibrate/design/plan) is genuinely novel per problem statement. No existing tool does this. This is the core differentiator and should be built, not bought.
2. **Design-time adversarial review** — all production tools (Qodo, Compound Engineering, architectural validation) operate on code. Parallax operates on design docs. Domain shift requires custom personas, not just reuse.
3. **Persona prompt engineering** — the specific adversarial lenses (Assumption Hunter, First Principles Challenger, etc.) are domain expertise captured in prompts. This is the novel IP, not the orchestration plumbing.

**What I may have over-emphasized:**
- Using existing frameworks (Inspect AI, LangGraph, LangSmith) may introduce dependencies, learning curves, or constraints that custom implementation avoids. Prototype-first philosophy (CLAUDE.md: "build to understand") suggests building minimal working version before committing to frameworks.
- adversarial-spec and Compound Engineering are GitHub plugins, not libraries. Integration may be harder than "use their patterns" suggests.

**Recommendation:** Build the novel parts (phase classification, persona prompts), leverage existing infrastructure where it's clearly superior (Inspect AI for orchestration, LangSmith for annotation UI), and defer framework decisions until prototyping reveals which abstractions help vs hinder.

---

## Sources

- [Anthropic 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf?hsLang=en)
- [Google's Eight Essential Multi-Agent Design Patterns - InfoQ](https://www.infoq.com/news/2026/01/multi-agent-design-patterns/)
- [Multi-Agent System Architecture Guide for 2026 - ClickIT](https://www.clickittech.com/ai/multi-agent-system-architecture/)
- [AI Coding Agents in 2026: Coherence Through Orchestration - Mike Mason](https://mikemason.ca/writing/ai-coding-agents-jan-2026/)
- [AI Agent Evaluation: Frameworks, Strategies, and Best Practices - Medium](https://medium.com/online-inference/ai-agent-evaluation-frameworks-strategies-and-best-practices-9dc3cfdf9890)
- [Inspect AI Multi-Agent Documentation - UK AISI](https://inspect.aisi.org.uk/agents.html)
- [Frontier AI Trends Report - AISI](https://www.aisi.gov.uk/frontier-ai-trends-report)
- [Top 10+ Agentic Orchestration Frameworks & Tools in 2026 - AIMultiple](https://aimultiple.com/agentic-orchestration)
- [LangGraph: Agent Orchestration Framework - LangChain](https://www.langchain.com/langgraph)
- [LangGraph Workflows and Agents Documentation](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
- [Building AI Workflows with LangGraph - Scalable Path](https://www.scalablepath.com/machine-learning/langgraph)
- [Compound Engineering: How Every Codes With Agents](https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents)
- [Compound Engineering Methodology Guide](https://every.to/guides/compound-engineering)
- [EveryInc Compound Engineering Plugin - GitHub](https://github.com/EveryInc/compound-engineering-plugin)
- [adversarial-spec Plugin - GitHub](https://github.com/zscole/adversarial-spec)
- [Adversarial Multi-Agent Evaluation of LLMs - OpenReview](https://openreview.net/forum?id=06ZvHHBR0i)
- [Debate, Deliberate, Decide (D3): Adversarial Framework - arXiv](https://arxiv.org/html/2410.04663)
- [MoSCoW Prioritization Comprehensive Guide - Hypersense](https://hypersense-software.com/blog/2024/12/03/moscow-prioritization-guide/)
- [MoSCoW Prioritization Method - ProductPlan](https://www.productplan.com/glossary/moscow-prioritization/)
- [MoSCoW Method - Wikipedia](https://en.wikipedia.org/wiki/MoSCoW_method)
- [LangSmith Evaluation Platform](https://www.langchain.com/langsmith/evaluation)
- [Human Feedback & Annotation for LangChain - APXML](https://apxml.com/courses/langchain-production-llm/chapter-5-evaluation-monitoring-observability/human-feedback-annotation)
- [What Is LangSmith? Complete 2026 Guide - Trantor](https://www.trantorinc.com/blog/what-is-langsmith)
- [Braintrust LLM Evaluation Metrics Guide](https://www.braintrust.dev/articles/llm-evaluation-metrics-guide)
- [Braintrust AutoEvals - GitHub](https://github.com/braintrustdata/autoevals)
- [Braintrust Scorers Documentation](https://www.braintrust.dev/docs/guides/functions/scorers)
- [Custom LLM as a Judge - OpenAI Cookbook](https://cookbook.openai.com/examples/custom-llm-as-a-judge)
- [Promptfoo: Build Secure AI Applications](https://www.promptfoo.dev/)
- [Promptfoo Adversarial Testing Architecture](https://www.promptfoo.dev/docs/red-team/architecture/)
- [Promptfoo GitHub Repository](https://github.com/promptfoo/promptfoo)
- [Using AI Agents to Enforce Architectural Standards - Medium](https://medium.com/@dave-patten/using-ai-agents-to-enforce-architectural-standards-41d58af235a0)
- [Software Architecture Validation - ScienceDirect](https://www.sciencedirect.com/topics/computer-science/architecture-validation)
- [Bug Severity Classification Guide - Frugal Testing](https://www.frugaltesting.com/blog/how-to-classify-bug-severity-in-qa-testing-a-complete-guide-for-software-teams/)
- [Survey on Bug Deduplication and Triage - MDPI](https://www.mdpi.com/2076-3417/13/15/8788)
- [OWASP LLM Top 10 - Promptfoo](https://www.promptfoo.dev/docs/red-team/)

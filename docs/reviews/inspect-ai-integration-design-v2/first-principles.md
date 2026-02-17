# First Principles Review — Inspect AI Integration Design v2

**Reviewer:** First Principles Challenger
**Date:** 2026-02-17
**Artifact:** Inspect AI Integration Design v2 + Requirements v2

---

## Problem Reframe

The core problem is: "We cannot tell whether changes to parallax reviewer agents improve or degrade finding quality." From first principles, that problem requires three things — a representative corpus of known-good findings, a way to run a reviewer against that corpus, and a metric that distinguishes good-from-bad output. The design delivers all three, and the per-reviewer task decomposition (v2's key insight over v1) is correct. Where the design goes wrong is not in the direction chosen but in the scope of what it claims to validate: the eval tests whether each isolated agent detects pre-categorized findings in isolation, which is a necessary but not sufficient condition for validating whether the full parallax review workflow produces high-quality findings for real users.

---

## Findings

### Finding 1: The eval validates a stripped-down proxy, not the actual artifact under test

- **Severity:** Critical
- **Phase:** calibrate (primary), design (contributing)
- **Section:** Overview and Context / Per-Reviewer Task Architecture
- **Issue:** The design tests individual reviewer agents reading a document in a single-turn, tool-free context. But the thing parallax ships to users is an orchestration workflow that dispatches those agents with tools, collects their output, runs a synthesizer, deduplicates findings, and produces a consolidated report. The design explicitly acknowledges v1 failed because it tested the wrong artifact (the skill, not the agents). V2 overcorrects: it now tests agents in a context so stripped-down that eval pass/fail tells you almost nothing about whether the full pipeline produces valid output. An agent that scores 90% recall in eval might produce 50% recall inside the actual orchestration workflow if the tool-calling context, system prompt layering, or synthesizer deduplication eliminates findings downstream.
- **Why it matters:** The stated problem is "we cannot measure skill effectiveness." The proposed solution measures something easier — isolated agent detection in a clean lab context. If the lab and production contexts diverge significantly (which they do: tools, system prompt layering, context window state, synthesizer filtering), a green eval dashboard gives false confidence that the full skill works. This is exactly the kind of nearby-problem substitution that fails silently in production.
- **Suggestion:** Reframe the eval as explicitly validating a layer, not the full system. The requirements and design should state: "Phase 1 validates the signal layer (do agents detect findings when given a clean document?). Phase 3 validates the system layer (does the orchestration pipeline preserve those findings through synthesis?). Passing Phase 1 does not imply the full skill works end-to-end." This framing is honest and prevents the dashboard from being misread as a full system green light.

---

### Finding 2: Ground truth is sourced from the same agents under test — the eval is partially self-referential

- **Severity:** Critical
- **Phase:** calibrate (primary)
- **Section:** Ground Truth Management / Phase 1 Test Plan
- **Issue:** The 10 Critical findings used as ground truth were produced by the parallax review skill (which dispatches these same reviewer agents), then manually validated by a human. The eval then tests whether each reviewer agent detects findings from its own prior output. This creates a self-referential loop: assumption-hunter is tested on findings that assumption-hunter produced. The human validation step breaks the loop partially — but only if the validator assessed whether each finding was a real design flaw, not whether the finding was attributable to a specific agent. If reviewer attribution was inferred from finding ID prefixes (e.g., `assumption-hunter-001`) rather than established independently, the ground truth labels "which agent should detect this" are circular by construction.
- **Why it matters:** If the eval asks "does assumption-hunter detect assumption-hunter-001?" and assumption-hunter produced that finding, high recall is almost tautologically guaranteed regardless of prompt quality. The eval measures prompt stability (does the agent reproduce its own output?) rather than detection capability (does the agent catch real design flaws it hasn't seen before?). These are different properties, and optimizing for the former can mask failures in the latter.
- **Suggestion:** The ground truth requires two independent properties: (a) each finding is a real design flaw (human validation addresses this), and (b) each finding is attributable to a specific reviewer persona based on the nature of the finding, not based on who produced it. Attribution should be assigned by the persona's stated focus areas, not by the finding ID prefix. Additionally, the eval should include at least a few findings the agents have never seen (from a different review artifact) to test generalization, not just reproduction.

---

### Finding 3: Per-reviewer task decomposition treats recall as the signal when precision is the actual bottleneck

- **Severity:** Important
- **Phase:** calibrate (primary), design (contributing)
- **Section:** Phase 1 Test Plan / FR-ARCH-1
- **Issue:** The design's success metric is recall (does the agent detect ground truth findings?). But the stated problem in v1 requirements is that parallax produces "too many Important findings" — the calibration failure was excess findings, not missed findings. The eval optimizes for the wrong direction. High recall is easy to achieve: instruct the agent to produce many findings, and recall climbs. The harder problem — precision (does the agent avoid false positives, stay in its lane, avoid duplicating other reviewers?) — is not measured in Phase 1 at all. The Phase 1 test plan treats "≥1 reviewer achieves recall ≥0.90" as the completion gate, which an agent can pass by flooding its output with findings.
- **Why it matters:** A recall-only eval that doesn't penalize false positives creates a perverse incentive during prompt tuning: adding "be aggressive, find more issues" to any agent prompt will improve recall scores while degrading the actual user experience (too many findings, too much noise). This is measurably the wrong optimization target given the stated calibration problem.
- **Suggestion:** Phase 1 must measure precision alongside recall. The completion gate should be F1 or a precision floor (e.g., precision ≥0.60 at the same time as recall ≥0.70). Without a precision constraint, the eval scores can improve while the skill gets worse for users.

---

### Finding 4: The design's JSONL output alignment fix addresses the symptom, not the root cause

- **Severity:** Important
- **Phase:** design (primary)
- **Section:** JSONL Output Alignment
- **Issue:** The design identifies that `assumption-hunter.md` outputs markdown instead of JSONL, and proposes fixing its output format section. This treats the symptom. The root cause is structural: agent system prompts embed output format instructions inline, with no schema enforcement mechanism and no canonical source of truth. The design does not specify where the authoritative schema lives, how agents reference it, or how the scorer discovers schema changes. The requirements review (summary.md) identified schema fragmentation across three locations as Important finding #17. The design's proposed fix (update one agent's output format section) adds a fourth location rather than consolidating to one.
- **Why it matters:** The next time any agent prompt is updated, format drift re-emerges. The fix is not durable — it's a patch on a structural problem. The blast radius is silent: if an agent reverts to markdown output, the scorer returns 0 findings, which is indistinguishable from "agent found nothing." Zero findings from a format mismatch looks identical to zero findings from a genuinely flawless document. This ambiguity is undetectable from eval results alone.
- **Suggestion:** Establish a canonical schema artifact (a JSON Schema file or Python dataclass in `evals/schema.py`). Agent prompts reference the schema by embedding it at load time or linking to the file explicitly. The scorer validates against the same schema object. Schema changes require a single update to one file. This is the fix — updating one agent's instructions is not.

---

### Finding 5: The per-reviewer task architecture inherits Inspect AI's eval model when the actual need is agent behavior testing

- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Per-Reviewer Task Architecture
- **Issue:** Inspect AI's task model is: given an input, produce an output, score the output against ground truth. The design forces parallax reviewer agents into this model by stripping their tools, delivering document content inline, and scoring their single-turn output. This works for Inspect AI's native use case (testing LLM capabilities on well-defined tasks with clean inputs). It does not naturally fit the actual parallax use case: testing whether a persona-driven reviewer, operating with its full tool set and system context, produces coverage of a known finding space across diverse document types. The design has inherited Inspect AI's evaluation model uncritically and bent the problem to fit the tool.
- **Why it matters:** The consequence is that agent behavior in eval context (single-turn, no tools, document in prompt) systematically differs from agent behavior in production context (multi-turn, tools enabled, document read via file system). Any findings about agent quality from the eval transfer imperfectly to production. Prompt optimizations that improve eval scores may degrade production behavior if the optimization exploits the clean eval context (e.g., optimizing for in-prompt document structure that doesn't match real file content).
- **Suggestion:** Acknowledge this gap explicitly in the design. Add a section: "Eval Context vs Production Context Gaps — known behavioral differences and how they bound the validity of eval conclusions." This is not a reason to abandon the approach (single-turn eval is the correct Phase 1 starting point), but the gap needs to be documented so that eval results are interpreted correctly and the Phase 3 agent bridge is understood as necessary for full system validation, not optional.

---

### Finding 6: The design solves v1's failure mode but carries forward v1's dataset assumption unchallenged

- **Severity:** Important
- **Phase:** calibrate (primary)
- **Section:** Ground Truth Management / "Ground truth: 10 validated Critical findings across 5 reviewers"
- **Issue:** The design states "10 validated Critical findings across 5 reviewers. 9 testable." With per-reviewer filtering, the average per-reviewer ground truth is ~2 findings. The design does not address this statistical reality anywhere. A reviewer with 2 ground truth findings has binary recall: 0%, 50%, or 100%. At this granularity, a single missed finding is a 50-point recall swing. The design cannot distinguish "this agent has a systematic gap" from "this agent missed one edge-case finding in a 2-finding dataset." The Phase 1 test plan completion criterion — "≥1 reviewer achieves recall ≥0.90" — is statistically meaningless at N=2 (0.90 recall rounds to either 1/1 or 2/2 depending on rounding, there is no intermediate state).
- **Why it matters:** Phase 1 will produce numbers that look like signal but are actually noise. Prompt tuning decisions made on N=2 per-reviewer data will be arbitrary. The blast radius: any iteration cycle that uses these numbers to guide prompt changes will produce random walk optimization — changes will appear to improve scores when they happen to match the 2 edge cases in ground truth, then appear to degrade when tested on new documents.
- **Suggestion:** Either (a) explicitly frame Phase 1 as a smoke test (does recall > 0.0? is the plumbing working?) with no prompt tuning decisions until ground truth expands to ≥5 findings per reviewer, or (b) expand ground truth before Phase 1 begins by adding Important-severity findings from the same review artifact. The design must state which path is taken — leaving N=2 unaddressed while calling Phase 1 a "detection baseline" is misleading.

---

### Finding 7: The post-review finding exclusion creates an undocumented gap in what the eval can detect

- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** "Post-review finding excluded (not detectable from requirements doc alone)"
- **Issue:** The design excludes 1 of 10 findings from the testable set because it was identified post-review and cannot be detected from the requirements document alone. This exclusion is pragmatic but creates an untested category of findings: those that require cross-artifact context (prior review output, session notes, implementation experience) to identify. The design does not document what type of finding this is, why it's in that category, or whether this category systematically represents the hardest-to-detect findings that matter most.
- **Why it matters:** If post-review, cross-artifact findings represent the highest-value detection (because they require synthesis across sources), excluding them from the eval corpus means the eval systematically cannot measure performance on the highest-value finding category. Over time, optimizing for the testable corpus may produce agents that are good at isolated-document findings and blind to the cross-artifact class.
- **Suggestion:** Document the excluded finding's category and the structural reason for exclusion. Add a note: "Cross-artifact findings are not testable in Phase 1 single-turn eval context. Phase 3 agent bridge testing is the correct evaluation vehicle for this class." This makes the exclusion principled rather than invisible.

---

## Blind Spot Check

My focus on problem framing may underweight pragmatic implementation concerns that other reviewers catch more readily.

**What I may have underweighted:**

- **Environmental blockers** — Python version pinning, Inspect AI version pinning, working directory sensitivity. These are Phase 1 blockers that the requirements review already surfaced (11 Critical findings). I treated them as outside scope for first-principles analysis, but they represent concrete failure modes that will stop the design from running at all before any of my framing concerns become relevant.

- **The design is genuinely correct on its core bet.** V1's failure was real (skill-as-system-prompt produced 0.000 accuracy). Per-reviewer task decomposition is the right architectural fix. My Critical findings challenge the scope and interpretation of what the eval can validly claim — they do not challenge the fundamental correctness of the per-reviewer approach.

- **Sequence matters.** Finding 1 (proxy vs real system) and Finding 5 (inherited eval model) are both true and both manageable if explicitly scoped. The risk is not that the design is wrong — it is that the design's output will be misinterpreted as validating more than it actually validates. Adding the explicit scope framing I suggest costs nothing and prevents that misreading.

- **Finding 3 (precision omission) is the highest-leverage finding** for actual day-to-day use. A recall-only eval that can be gamed by flooding output is structurally dangerous during prompt iteration. This is the finding most likely to cause measurable harm if ignored.

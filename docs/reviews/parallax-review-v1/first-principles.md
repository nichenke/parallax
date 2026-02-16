# First Principles Challenger Review

## Problem Reframe

**Core problem from first principles:** The design process fails when a single perspective dominates and blind spots go unchallenged. The real problem is not "how do we coordinate review agents" but "how do we force exposure of unstated assumptions before they become design debt."

This differs subtly but critically from the design's framing. The design frames the problem as "multiple perspectives catch gaps" (true but incomplete) when the deeper problem is "single perspectives create invisible constraints." The solution isn't just additive (more reviewers = more coverage) but adversarial (reviewers that actively challenge each other's worldviews).

---

## Findings

### Finding 1: The Synthesizer Role Contradicts the Adversarial Premise
- **Severity:** Important
- **Phase:** design
- **Section:** Synthesis (lines 122-136)
- **Issue:** The Synthesizer is defined as "purely editorial — zero judgment on content or severity" but is tasked with deduplication, phase classification, and surfacing contradictions. This is judgment work disguised as editorial work. Deduplication requires deciding "are these the same issue or different manifestations?" Phase classification requires understanding what truly failed. These are interpretive acts.
- **Why it matters:** If the Synthesizer makes no judgments, it will produce mechanical consolidation that misses emergent insights (where two findings from different angles reveal a deeper problem). If it does make judgments, the "no judgment" constraint is dishonest and creates prompt confusion.
- **Suggestion:** Reframe the Synthesizer as an "adversarial consolidator" whose explicit job is to find patterns and tensions that individual reviewers can't see. Or split into two roles: (1) mechanical aggregator (truly no judgment), (2) meta-reviewer who analyzes the aggregate for emergent patterns. The current design wants both but won't admit it.

### Finding 2: "Discuss" is Underspecified and High-Risk
- **Severity:** Critical
- **Phase:** design
- **Section:** UX Flow, Step 5 (lines 220-226)
- **Issue:** "Discuss" is described as "full back-and-forth conversation about this finding before deciding" but provides no design for: Who is the user discussing with? The original reviewer? All reviewers? A new discussion agent? What prevents this from becoming an unbounded conversation that never resolves? What if the discussion reveals the finding is actually three separate findings?
- **Why it matters:** This is the most novel and potentially valuable interaction mode, but it's hand-waved. In a real session, "discuss" will either become a frustrating dead-end (no clear resolution mechanism) or a context explosion (user has to re-explain the same nuance to multiple reviewers). Without a design for how discussion converges to a decision, this will be the first feature users stop using.
- **Suggestion:** Specify the discussion protocol. Options: (1) Discussion with the original reviewer only, time-boxed to 3 turns, must end with revised severity or withdrawn finding. (2) Discussion invokes a "mediator" agent who has access to all reviewer contexts and helps triangulate. (3) Discussion creates a sub-review where all reviewers re-examine just this finding with the user's clarifications in context. Pick one and design it.

### Finding 3: Phase Classification Assumes Linear Causality
- **Severity:** Important
- **Phase:** calibrate
- **Section:** Finding Phase Classification (lines 138-146), Problem Statement lines 119-131
- **Issue:** The design assumes findings map cleanly to a single failing phase (survey gap, calibrate gap, design flaw, plan concern). Real design flaws are multi-causal: a missing requirement enabled a bad assumption which led to an infeasible design. Which phase "failed"? The classification forces a false choice.
- **Why it matters:** Single-phase classification will create escalation confusion ("fix requirements" but the design also needs rework) and mask systemic issues (if 5 findings all trace back to survey gaps, the signal is "stop and do real research," not "fix these 5 isolated gaps").
- **Suggestion:** Classify findings by primary and contributing phases. A finding can be "design flaw (primary) caused by calibrate gap (contributing)." This enables two actions: immediate (fix the design) and systemic (revisit requirements for this pattern). Also add aggregate analysis: if >30% of findings share a common root cause, escalate with "systemic issue detected."

### Finding 4: The Personas are Solving *Coverage*, Not *Adversarial Review*
- **Severity:** Critical
- **Phase:** calibrate
- **Section:** Reviewer Personas (lines 47-96)
- **Issue:** The 6 design-stage personas (Assumption Hunter, Edge Case Prober, etc.) are scoped by domain (what to look for) but not by stance (what to defend or attack). This produces comprehensive coverage but weak adversarial tension. Real adversarial review requires incompatible worldviews: "move fast and prove it works" vs "move carefully and prove it's safe." The personas can all be right simultaneously — they're additive, not adversarial.
- **Why it matters:** The hypothesis is "multiple perspectives catch gaps," but the personas are designed as non-overlapping inspectors. You'll catch more bugs but you won't challenge the design's core premise. The most valuable finding is "this whole approach is wrong," and none of these personas are incentivized to say that (except First Principles Challenger, who's outvoted 5-to-1).
- **Suggestion:** Redesign personas as adversarial pairs with opposing incentives. Examples: "Ship Fast" (minimize complexity, defer edge cases) vs "Ship Right" (demand completeness, block on unknowns). "User-Centric" (optimize for end-user experience) vs "Operator-Centric" (optimize for maintainability). Force them to argue. The best findings will come from resolving their contradictions, not from independent checklists.

### Finding 5: The Prototype Defers the Hardest Problem
- **Severity:** Important
- **Phase:** plan
- **Section:** Prototype Scope (lines 248-268)
- **Issue:** The prototype builds design-stage review but defers requirements and plan stages. The problem statement explicitly calls out requirements refinement as the "single biggest design quality lever" (line 99) and identifies spec drift (design-to-plan divergence) as a major pain point (lines 30-34). The prototype will validate persona mechanics but won't test the core hypothesis: does adversarial review at requirements-time prevent downstream design failures?
- **Why it matters:** Building design-stage review first is natural (familiar domain) but risks building the wrong thing. If requirements review is the highest-leverage phase, prototyping design review teaches you about subagent orchestration but nothing about whether the pipeline actually works. You'll have battle-tested personas for a phase that might not matter.
- **Suggestion:** Prototype requirements-stage review first, or in parallel. Use a real past project where bad requirements led to design failures (Second Brain is a candidate). Validate that adversarial review at requirements-time would have caught the issues. Then build design-stage review knowing it's solving the right problem. Alternatively: accept that you're prototyping orchestration mechanics (not value hypothesis) and defer validation to the eval framework.

### Finding 6: "Proceed" Verdict is Unactionable Without a Quality Bar
- **Severity:** Important
- **Phase:** design
- **Section:** Verdict Logic (lines 147-153)
- **Issue:** A "proceed" verdict means "only Important/Minor findings" but provides no guidance on how many Important findings are acceptable. Is a design with 20 Important findings better than one with 2? Does it matter if they're all in the same category (e.g., all edge cases deferred) vs spread across categories?
- **Why it matters:** Without a quality threshold, "proceed" becomes "no Critical findings" which is a very low bar. Real designs will accumulate Important findings that individually seem acceptable but collectively indicate the design is undercooked. The user has no framework to decide "this is good enough" vs "we need another iteration."
- **Suggestion:** Define a quality budget. Examples: (1) Hard cap (no more than N Important findings total). (2) Weighted score (Critical = -10, Important = -2, must be net positive after accepts). (3) Category limits (no more than 3 Important findings in any single persona's domain, signals blind spot). Make this configurable but provide a sensible default.

### Finding 7: Git Tracking Assumes Single-Branch Workflow
- **Severity:** Minor
- **Phase:** design
- **Section:** Output Artifacts (lines 32-45)
- **Issue:** "Iteration history tracked by git (each re-review is a new commit, diffs show what changed)" assumes all iterations happen on a single branch. Real workflows often involve design exploration in branches (Option A vs Option B) with review findings informing which to merge.
- **Why it matters:** If a user is comparing two design approaches and reviews both, the git history will show two interleaved commit sequences. Diffs will compare iterations within a branch (useful) but not branches against each other (also useful). The design assumes linear iteration when real design is often branching.
- **Suggestion:** Support explicit design comparison mode: review two design docs against the same requirements, produce a comparative summary ("Design A has stronger feasibility, Design B has better edge case handling"). Or document the limitation and defer to manual branching strategies.

### Finding 8: No Design for Reviewer Calibration Feedback Loop
- **Severity:** Important
- **Phase:** calibrate
- **Section:** Open Questions (lines 269-276), Problem Statement "Correction Compounding" (line 111)
- **Issue:** The design mentions "reject findings as feedback for reviewer tuning" and the problem statement describes correction compounding (false positives/negatives become calibration rules). But there's no design for how this feedback is captured, who analyzes it, or how prompts are updated. This is a core value proposition (reviewers improve over time) with no implementation plan.
- **Why it matters:** Without a calibration loop, rejected findings are lost signal. Over time, users will learn which reviewers produce noise and ignore them (defeating the multi-perspective benefit). The eval framework can measure quality, but if there's no mechanism to feed that back into prompts, the system won't improve.
- **Suggestion:** Design the calibration artifact. Minimal version: `docs/reviews/<topic>/calibration-notes.md` where the skill logs rejected findings with user's reason. After N reviews, a calibration skill analyzes patterns and suggests prompt updates. Or integrate with the eval framework: every review run is also an eval, findings are graded, and low-accuracy reviewers trigger prompt revision tasks.

---

## Blind Spot Check

As the First Principles Challenger, my blind spot is **over-questioning to the point of paralysis**. Some of my findings may be "this could be better" when "this is good enough for a prototype" is the right call given the YAGNI philosophy.

Specific risks I might be missing:
1. **The prototype is meant to learn, not to ship.** Deferring hard problems (requirements review, calibration loop) might be the right choice if the goal is to learn about persona mechanics first. I'm flagging this as a risk when it might be intentional.
2. **Simplicity has value.** My "adversarial pairs" suggestion (Finding 4) adds significant complexity. The current non-overlapping personas might be easier to prompt, easier to debug, and good enough to validate the hypothesis.
3. **The "discuss" mode might emerge from use.** I'm demanding a spec for discussion protocols when the right design might only be discoverable by trying it with real users. Over-specifying could constrain valuable exploration.

What I'm most confident about: **Finding 2 (Discuss is underspecified)** and **Finding 4 (Personas are coverage, not adversarial)** point to core design assumptions that should be challenged before implementation. If those are intentional tradeoffs, they should be explicitly documented. If they're oversights, fixing them now is cheaper than after the prototype is built.

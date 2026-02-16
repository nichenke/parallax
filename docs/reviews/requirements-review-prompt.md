# Requirements Review Subagent Prompt

**Task:** Review the requirements document for parallax:review and evaluate:

1. **Format & Style Quality**
2. **High-Level Outcomes / Jobs-to-Be-Done Clarity**
3. **Necessity Analysis: Do we need formal requirements?**

---

## Context

**Document to review:** `docs/requirements/parallax-review-requirements-v1.md`

**Background:**
- This is a requirements doc for a multi-agent adversarial design review skill
- Created after 3 design review iterations (v1, v2, v3) surfaced need for formal requirements
- Q1-Q8 open questions were just resolved and integrated into the doc
- Current status: Draft v1.1 (Open Questions Resolved)

**Key question from user:**
> "Do we have sufficient high-level outcomes (i.e., jobs to be done) that the rest of the detailed requirements have a sanity check on why we've added them?"

**Superpowers comparison:**
The superpowers plugin goes straight to design output without formal requirements docs. What's the design principle there, and can we learn from it?

---

## Review Focus Areas

### 1. Format & Style

**Evaluate:**
- Is the structure clear and navigable?
- Are requirements atomic and testable?
- Is traceability (source citations) helpful or cluttered?
- Are rationales compelling or boilerplate?
- Is the "Resolved Questions" section useful or should resolutions be inline?

**Look for:**
- Redundancy (same requirement stated multiple ways)
- Ambiguity (unclear success criteria)
- Over-specification (implementation details leaking into requirements)
- Under-specification (missing acceptance criteria)

---

### 2. High-Level Outcomes / Jobs-to-Be-Done

**The critical question:**
Does this requirements doc answer: **"What problem are we solving and why?"**

**Current state:**
- Problem statement exists in `docs/problem-statements/design-orchestrator.md`
- Requirements doc jumps straight to FR1-FR10, NFR1-NFR6
- No explicit "Jobs-to-Be-Done" or outcome-focused section

**What's missing (potentially):**
- User stories or scenarios ("As a designer, I want X so that Y")
- Success metrics ("Review catches 80% of design flaws before implementation")
- Value proposition ("Reduces design iteration time from days to hours")

**Evaluate:**
1. Can you trace each requirement back to a user need or outcome?
2. Are there requirements that feel unmotivated (no clear "why")?
3. Would adding a "Jobs-to-Be-Done" section at the top provide a sanity check?

**Example of what might be missing:**

```markdown
## Jobs-to-Be-Done

**Job 1: Catch design flaws before implementation**
- User: Engineering team designing new features
- Goal: Identify assumptions, edge cases, and contradictions before writing code
- Success: 80% of design flaws caught in review, not production
- Requirements that serve this: FR1-FR3, FR9, NFR4

**Job 2: Track design iteration progress**
- User: Designer iterating on design based on feedback
- Goal: Know which findings are resolved vs new vs persisting
- Success: Designer can answer "Did I fix the issues?" without manual cross-reference
- Requirements that serve this: FR5, FR10

**Job 3: Enable eval-driven quality improvement**
- User: Skill developer tuning reviewer prompts
- Goal: Measure prompt effectiveness, iterate based on data
- Success: Can correlate prompt changes with finding quality
- Requirements that serve this: NFR2, NFR5, NFR6
```

**Question for review:**
Without this framing, do the 53 functional requirements + 26 non-functional requirements feel anchored to real needs, or like feature creep?

---

### 3. Necessity Analysis: Do We Need Formal Requirements?

**The superpowers principle:**
Superpowers plugin goes straight to design/implementation without formal requirements docs. Skills are defined by their prompts and code. Why does this work?

**Hypothesis:**
- Skills are small enough that requirements fit in prompt context
- Iteration is cheap (change prompt, test, repeat)
- Users provide requirements inline ("I want X to do Y")
- Requirements are implicit in test cases

**For parallax:review:**
- Complex multi-agent orchestration (not a simple skill)
- Multiple decision points resolved (Q1-Q8)
- Eval framework needs stable requirements for testing
- 3 review iterations already showed requirements drift (findings like "JSONL decided but not documented")

**Questions to evaluate:**

1. **Could we eliminate this doc?**
   - Put high-level outcomes in CLAUDE.md
   - Put design decisions in design doc
   - Put Q1-Q8 resolutions in MEMORY.md
   - Just build and iterate

2. **What value does this doc provide?**
   - Single source of truth for "what are we building?"
   - Traceability (reviewers can cite FR5.1 instead of "the design says...")
   - Eval framework anchor (test against requirements, not just "did it work?")
   - Prevents scope creep (if it's not in requirements, it's out of scope)

3. **Is there a middle ground?**
   - High-level outcomes (Jobs-to-Be-Done) in CLAUDE.md
   - Detailed requirements in design doc
   - This doc becomes redundant?

4. **What would break if we deleted this doc?**
   - Finding phase classification (FR2.5-FR2.7) — would reviewers know how to classify?
   - JSONL schema (FR6) — would implementer know what fields are required?
   - Eval framework (NFR5, NFR6) — would tester know what to measure?

**Key insight to surface:**
If requirements are "stable enough to delete," they're documentation, not requirements. If they're changing frequently (Q1-Q8 resolutions), they're active design decisions that need a home.

---

## Output Format

**Produce 3 sections:**

### 1. Format & Style Findings
- List specific issues (redundancy, ambiguity, over/under-specification)
- Suggest improvements (restructuring, consolidation, clarification)
- Rate overall clarity: Clear | Needs Work | Confusing

### 2. Jobs-to-Be-Done Gap Analysis
- Are high-level outcomes explicit? (Yes/No + evidence)
- Can you trace requirements to user needs? (% traceable)
- Recommend: Add JTBD section? Inline outcomes? Leave as-is?
- Identify unmotivated requirements (if any)

### 3. Necessity Assessment
- Superpowers comparison: What can we learn?
- Value this doc provides (specific examples)
- Risks of eliminating this doc (what breaks?)
- Recommendation: Keep | Consolidate into CLAUDE.md/design doc | Restructure

---

## Success Criteria

Your review helps answer:
1. **Format:** Is this requirements doc well-structured and clear?
2. **Motivation:** Can we trace requirements back to user needs?
3. **Necessity:** Should we have formal requirements, or follow superpowers pattern?

Output should be concise, evidence-based, and actionable.

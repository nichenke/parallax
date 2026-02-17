# Experiment: What Made the Opus Research Prompt Work?

**Status:** Planned — not yet run
**Goal:** Determine whether output quality came from the prompt structure, the ambient context documents (CLAUDE.md, MEMORY.md), or conversation history — so we can write a reusable skill with the right focus.

---

## Background

On 2026-02-17, a short conversational prompt produced an exceptionally useful 8-section research report on Inspect AI eval patterns. The report:
- Correctly classified three tiers of Inspect AI agent complexity
- Definitively settled the "agent bridge vs. decompose" question with a comparison table
- Caught a second-order output format gap (markdown vs. JSONL) that we'd missed
- Produced copy-paste-ready code sketches for `evals/reviewer_eval.py`
- Laid out a phase-by-phase eval roadmap

**The original prompt was this short:**

> "run a deep opus background research to understand how inspect ai handles this sort of thing - including subagents, etc. What's the best practice for testing prompts/data sets when they are complex like this? Is this where the bridge options come into play?"

No file list. No structured output request. No binary yes/no framing. Just a directional question with a trailing hypothesis to probe.

**The hypothesis:** The prompt worked because the ambient context (CLAUDE.md + MEMORY.md + conversation history) did the heavy lifting — not the prompt itself. The context pre-loaded:
- The failure mode: `accuracy: 0.000`, 102 output tokens, model asking "What should I call this review folder?"
- The relevant files: `evals/severity_calibration.py`, `agents/assumption-hunter.md`, `evals/utils/output_parser.py`
- The Inspect AI API gotchas already encountered
- The strategic framing: build adversarial review, leverage Inspect AI infrastructure

If this hypothesis is correct, the skill to write is "how to maintain good context documents" not "how to write a good research prompt."

---

## The Benchmark Output

The report to compare against is at `docs/research/inspect-ai-eval-patterns.md`. Key quality markers:

1. **Tier classification** — Three tiers of Inspect AI agent complexity (solver chains, agents with tools, agent bridge), with clear criteria for when each applies
2. **Binary recommendation on agent bridge** — "No" with a comparison table, not "here are tradeoffs"
3. **Output format gap caught** — Reviewer agents output markdown; scorer expects JSONL. This cross-references `agents/assumption-hunter.md` output format with `evals/utils/output_parser.py` expectations
4. **Code sketches** — Working `evals/reviewer_eval.py` with per-reviewer `@task` functions, `load_reviewer_dataset()` with reviewer filtering
5. **Phase roadmap** — Phase 1 through Phase 3 with clear scope boundaries

A lower-quality output would: summarize Inspect AI documentation generically, present agent bridge as "option to consider," miss the output format gap, produce descriptive text instead of code.

---

## Relevant Repository Files

These files are referenced in the experiment. Read them before running variants.

```
evals/severity_calibration.py          — current eval task (uses orchestration skill as system prompt)
evals/utils/output_parser.py           — scorer expects JSONL output format
evals/utils/dataset_loader.py          — how ground truth is loaded
agents/assumption-hunter.md            — reviewer agent prompt (outputs structured markdown)
skills/requirements/SKILL.md          — orchestration skill (the thing that asks "What should I call this folder?")
datasets/inspect-ai-integration-requirements-light/critical_findings.jsonl  — ground truth (10 findings)
datasets/inspect-ai-integration-requirements-light/metadata.json
```

---

## The Mismatch We Were Debugging

The eval framework was running `make eval` and returning `accuracy: 0.000`. Two layers of mismatch:

1. **Layer 1 (known):** The `skills/requirements/SKILL.md` is an orchestration workflow. Its Step 1 asks the user "What should I call this review folder?" and Step 3 dispatches 5 parallel agents via the Task tool. In eval context there's no interactive input and no Task tool — the model produced 102 output tokens of interactive prompts and stopped.

2. **Layer 2 (caught by research, was unknown):** Even if we decompose to per-reviewer tasks, `evals/utils/output_parser.py` expects JSONL output. But `agents/assumption-hunter.md` instructs the model to "Write your findings as structured markdown." The scorer would parse zero findings from markdown output.

The research prompt was issued after we diagnosed Layer 1 but before we knew about Layer 2.

---

## Experiment Design

Run these four variants as parallel background agents (Opus model, background mode). Each writes its report to a separate output file. Compare against the benchmark.

**Shared baseline question for all variants:**

> "Research how Inspect AI handles complex multi-step evaluations. We are evaluating parallax reviewer agents — individual LLM agents that review design documents and output structured findings. Our current approach (using an orchestration skill as the eval system prompt) returns accuracy: 0.000. What is the right Inspect AI pattern for testing individual reviewer agents? Is the agent bridge / inspect_swe pattern appropriate here or overkill? Produce a concrete report with a recommendation and code sketches."

---

### Variant A — Full Context (Reproduction Baseline)

Run in the parallax repo with normal Claude Code context loading. This should reproduce the original result.

**Context available:**
- CLAUDE.md (project context, architecture, key decisions)
- MEMORY.md (session learnings, current state, API gotchas)
- Access to all repo files via Read/Grep/Glob tools

**Prompt:** Use the shared baseline question above.

**Output file:** `docs/research/experiment-variant-a-full-context.md`

**Hypothesis:** Should match benchmark quality closely. If it doesn't, the original result was a one-time artifact.

---

### Variant B — No MEMORY.md Learnings

Strip the Key Learnings sections from MEMORY.md before running. Specifically remove:
- "Inspect AI eval implementation (Session 20)" learnings
- "Eval framework debugging (Session 21)" learnings

**Context available:**
- CLAUDE.md (intact)
- MEMORY.md (session notes + current state, but no Key Learnings)
- Repo files

**Prompt:** Use the shared baseline question above.

**Output file:** `docs/research/experiment-variant-b-no-learnings.md`

**Hypothesis:** Report will be missing the output format gap catch (needed to cross-reference actual code files, which the learnings section pointed at). Code sketches may be more generic.

---

### Variant C — Minimal Context (No CLAUDE.md or MEMORY.md)

Run with only the prompt — no project context documents. Provide only what's in the prompt itself.

**Context available:**
- No CLAUDE.md
- No MEMORY.md
- No conversation history
- Prompt must be self-contained

**Self-contained prompt for this variant:**

> "You are researching Inspect AI, a Python evaluation framework for LLMs. We have a project that reviews design documents using multiple reviewer LLM agents. Each agent (e.g., 'assumption-hunter', 'scope-guardian') receives a design document and outputs structured findings. We are trying to evaluate these agents using Inspect AI. Our current approach: load the orchestration skill as a system prompt, call generate(), score output. Problem: accuracy is 0.000 because the skill asks interactive questions (it was designed for user interaction, not eval). Research: (1) What Inspect AI pattern is right for evaluating individual reviewer agents? (2) Is the 'agent bridge' / 'inspect_swe' pattern appropriate or overkill? (3) What patterns exist for handling the case where agents output markdown but scorers expect structured data? Produce a concrete report with recommendation and working code sketches for Python."

**Output file:** `docs/research/experiment-variant-c-minimal-context.md`

**Hypothesis:** Will produce a technically accurate but less targeted report. May miss the output format gap (no reference to actual scorer code). Will likely hedge more on agent bridge rather than give a definitive "no."

---

### Variant D — Structured Prompt, No Ambient Context

Same minimal context as Variant C, but with the prompt structured the way one might write it "correctly" — with file list, binary questions, explicit output format request.

**Self-contained structured prompt:**

> "Research how Inspect AI handles complex multi-step evaluations. Context: we are evaluating parallax reviewer agents — LLM agents that read design documents and output structured findings. Current problem: our eval uses an orchestration skill as the system prompt; accuracy is 0.000 because the skill asks interactive questions in Step 1.
>
> Relevant architecture:
> - Reviewer agents (assumption-hunter, scope-guardian, etc.) output structured markdown findings
> - Scorer in output_parser.py expects JSONL (one finding per line)
> - Current eval: system_message(skill) + generate() + score
> - Ground truth: 10 validated Critical findings with reviewer attribution
>
> Research questions:
> 1. Is decomposing to per-reviewer @task functions the right approach? (Yes/No + rationale)
> 2. Is the agent bridge / inspect_swe pattern appropriate for Phase 1? (Yes/No + rationale)
> 3. How do we handle the markdown-vs-JSONL output format mismatch?
> 4. What Inspect AI patterns exist for multi-reviewer aggregate scoring?
>
> Produce: decision table, code sketch for evals/reviewer_eval.py with per-reviewer tasks, phase roadmap."

**Output file:** `docs/research/experiment-variant-d-structured-prompt.md`

**Hypothesis:** Will produce a report similar in coverage to Variant A because the prompt itself provides the missing context. The output format mismatch will be caught because we stated it explicitly. Tests whether a good structured prompt can substitute for good ambient context.

---

## Evaluation Rubric

Score each variant 1-5 on each dimension. Compare to benchmark (target: 5/5 on each).

| Dimension | What to look for |
|-----------|-----------------|
| **Tier classification** | Does it name and distinguish solver chains / agents-with-tools / agent bridge? |
| **Agent bridge recommendation** | Definitive "no for Phase 1-2" with a comparison table? Or "here are tradeoffs"? |
| **Output format gap** | Does it catch the markdown-vs-JSONL mismatch without being told? |
| **Code sketches** | Working `evals/reviewer_eval.py` with per-reviewer tasks and reviewer filtering? |
| **Phase roadmap** | Phase 1 through 3 with scope boundaries? Or generic "here are steps"? |
| **Actionability** | Can you implement the next step directly from the report without further research? |

---

## How to Run

1. Open the repo in Claude Code: `cd /path/to/parallax`
2. For each variant, launch a background Opus agent with the Task tool:
   - `subagent_type: "general-purpose"` with `model: "opus"`
   - `run_in_background: true`
   - Use the variant's prompt
3. For Variant C and D: before launching, note that no CLAUDE.md or MEMORY.md context is in effect — run in a clean session or explicitly tell the agent to ignore project context
4. Wait for all four to complete
5. Compare outputs using the rubric above
6. Write findings to `docs/research/opus-prompt-context-experiment-findings.md`

---

## Expected Findings (Hypotheses Summary)

| Variant | Expected quality | Predicted gaps |
|---------|-----------------|----------------|
| A — Full context | Matches benchmark | None |
| B — No learnings | Good but misses output format gap | Layer 2 mismatch not caught |
| C — Minimal context, conversational | Adequate but hedged | Agent bridge hedged, output format gap missed, generic code |
| D — Structured prompt, no context | Matches benchmark on stated dimensions | Only catches what was stated explicitly; may miss unstated issues |

If B degrades and D matches, the finding is: **structured prompts can compensate for thin context, but rich context enables short prompts to catch unstated issues**.

If B matches and C degrades, the finding is: **MEMORY.md Key Learnings (not prompt structure) is doing the work**.

---

## Skill to Write After Experiment

The experiment results will determine which of these to write:

- **If context is doing the work:** "How to maintain research-ready MEMORY.md and CLAUDE.md" — key patterns for what to capture in session notes so future research prompts don't need to be elaborate
- **If structured prompts compensate:** "How to write an effective Opus research commission" — prompt structure, binary questions, file list, output format specification
- **If both contribute:** Write both, with explicit guidance on which to invest in

---

*Created: 2026-02-17. Run this experiment before writing the `commissioning-opus-research` skill.*

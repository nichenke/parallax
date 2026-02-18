# Feasibility Skeptic Review

## Complexity Assessment
**Overall complexity:** Medium (elevated to High in Phase 2)
**Riskiest components:** (1) must_find.jsonl curation protocol — labor-intensive, requires expert judgment, no automation; (2) reverse_judge_precision Haiku judge — depends on undocumented Haiku behavior on adversarial critique tasks; (3) Phase 2 scorer as described requires both scorers to be independently correct before either produces trustworthy signal
**Simplification opportunities:** The two-tier approach may be over-designed for the current sample size (N≈2 per reviewer). A single well-specified precision scorer might deliver 80% of Phase 2 value at 20% of the complexity.

## Findings

### Finding 1: must_find.jsonl curation is a high-skilled manual task with no tooling support
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Scoring Strategy (ADR-007) — Tier 2: must_find_recall, Curation rules
- **Issue:** Curating must_find.jsonl requires: (1) running a full review session to generate candidates, (2) human expert judgment to distinguish document-visible from context-dependent findings, (3) assigning per-finding min_recall thresholds (yet undefined for Phase 2), (4) the zero-shot validation test (if adopted from assumption-hunter's recommendation). This is 3–5 hours of expert work per dataset, per major document revision. The design presents curation as a straightforward step with no acknowledgment of the labor or skill required.
- **Why it matters:** If curation is too burdensome, it will not be done. must_find_recall with a stale or incomplete curated list is worse than no regression guard — it creates false confidence that regression is being caught when important findings are not in the list. The ground truth refresh cadence (FR-ARCH-4) already struggles with this; ADR-007 adds a second curated artifact that also needs refreshing.
- **Suggestion:** Automate first-pass curation: run the existing reviewer agents on the frozen document, collect all findings that score above a confidence threshold on the zero-shot judge test, and auto-populate must_find.jsonl candidates for human confirmation. Human expert reviews and confirms — they don't generate from scratch. This reduces curation to a confirmation step.

### Finding 2: Two-tier scorer adds implementation surface area that outpaces ground truth size
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Scoring Strategy (ADR-007) — Updated scorer wiring
- **Issue:** The design adds two new scorers (reverse_judge_precision, must_find_recall) and retires two (severity_calibration, llm_judge_match) while the underlying dataset has N≈2 findings per reviewer — a sample size too small for either metric to be statistically meaningful. Tier 1 precision at N=10 total findings is a noisy single-digit count. Tier 2 recall against a curated list of (likely) 3–5 must-find findings cannot distinguish 'good reviewer' from 'lucky reviewer.' The complexity of two scorers is not matched by the statistical power of the dataset.
- **Why it matters:** Building two scorers against insufficient ground truth produces scores that look precise but are statistically unreliable. The design acknowledges this for Phase 1 recall ('N=1 is binary') but does not address it for Phase 2 precision. Two scorers on N=10 findings means each scorer generates 10 data points — not enough to trust either metric independently.
- **Suggestion:** Before implementing two-tier scoring, specify the minimum ground truth size needed for each metric to be meaningful. A precision metric needs at least N=20 findings to distinguish 80% from 90% precision (10-finding difference). Set a gate: 'Two-tier ADR-007 scoring activates when ground truth reaches N≥20 per reviewer (N≥100 total).' Until then, run the prototype reverse_judge_precision scorer only, reported as a diagnostic indicator, not a quality signal.

### Finding 3: Haiku judge prompt engineering is underestimated as implementation work
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Scoring Strategy (ADR-007) — Tier 1: reverse_judge_precision
- **Issue:** The design treats the judge prompt as a documentation task: 'This explicit false positive list mirrors the code-review plugin's approach and must be encoded in the judge system prompt.' In practice, getting a Haiku judge to reliably distinguish genuine from not-genuine design findings requires iterative prompt development. The false positive categories as written are abstract ('style or completeness preference without a specific structural gap') — determining whether a specific finding meets this criterion is a semantic judgment that Haiku at T=0 will make inconsistently without extensive prompt engineering and calibration examples.
- **Why it matters:** Without worked examples (few-shot) in the judge prompt, abstract criteria produce inconsistent classifications. The design specifies T=0 determinism as a feature, but determinism of an incorrectly-prompted judge is worthless — it consistently produces the wrong answer. Prompt engineering for a binary classifier in the design/requirements domain is not a trivial task.
- **Suggestion:** Allocate explicit effort to judge prompt development: (1) Create a calibration set of 10 known genuine findings and 10 known false positives from the existing ground truth. (2) Run Haiku with the proposed judge prompt against this calibration set. (3) Measure accuracy against the calibration set before trusting the scorer on new findings. (4) Iterate prompt until calibration accuracy ≥90%.

### Finding 4: context_dependent_findings.jsonl is a permanent exclusion with no re-evaluation path
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Scoring Strategy (ADR-007) — Dataset schema additions
- **Issue:** context_dependent_findings.jsonl is described as a 'reviewer coverage improvement backlog' but the design provides no process for re-evaluating whether excluded findings should be reclassified. If the reviewer agents are updated to include more context (e.g., reading linked ADRs), a previously context-dependent finding might become document-visible. The schema has no version or review-date field to trigger re-evaluation.
- **Why it matters:** Over time, context_dependent_findings.jsonl accumulates excluded findings that may become evaluatable as the eval framework matures. A static exclusion file with no re-evaluation trigger means findings are excluded forever even when the condition that caused exclusion (no external context) no longer applies.
- **Suggestion:** Add a `review_after` field to context_dependent_findings.jsonl: the phase (Phase 2, Phase 3) after which this finding should be reconsidered for promotion to must_find.jsonl. Link to the issue that tracks the blocker (e.g., Issue #68 for multi-document eval design). This turns the exclusion file into an actionable backlog.

## Blind Spot Check
I focused on implementation complexity and hidden labor costs. I may have underweighted: (1) whether the two-tier approach is genuinely novel or whether existing eval frameworks (Braintrust, Promptfoo) already implement reverse-judge precision — if they do, the build-vs-leverage question applies to the scorers themselves; (2) the operational complexity of running N=3 runs per eval cycle (Phase 2.5) — this triples eval run time and cost, which may not be acceptable for a development workflow tool.

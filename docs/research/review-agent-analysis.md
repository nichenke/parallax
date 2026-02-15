# Review Agent Analysis: compound-engineering + adversarial-spec

**Research Date:** 2026-02-15
**Purpose:** Understand existing multi-agent review implementations to inform parallax:review design
**Sources:** EveryInc/compound-engineering-plugin, zscole/adversarial-spec

---

## compound-engineering: 15 Review Agents

### The Actual Agents

| # | Agent | What It Checks | Phase Relevance |
|---|-------|---------------|-----------------|
| 1 | architecture-strategist | SOLID, circular deps, component boundaries, API contracts, design patterns | Design + Implementation |
| 2 | security-sentinel | OWASP Top 10, auth/authz, input validation, secrets, dependency vulns | Design + Implementation |
| 3 | performance-oracle | Big O, N+1 queries, memory leaks, caching, bundle size, projects at 10x/100x/1000x scale | Design + Implementation |
| 4 | code-simplicity-reviewer | YAGNI violations, unnecessary abstractions, premature generalization, complexity scores | Implementation |
| 5 | pattern-recognition-specialist | Design patterns, anti-patterns, naming, duplication, architectural boundaries | Implementation |
| 6 | agent-native-reviewer | Action parity (UI actions have agent equivalents), context parity | Implementation (niche) |
| 7 | data-integrity-guardian | Migration safety, NULL handling, race conditions, transaction isolation, GDPR | Implementation |
| 8 | data-migration-expert | Production data mapping verification, swapped value detection, dual-write patterns | Implementation |
| 9 | schema-drift-detector | Cross-references schema.rb against PR migrations for unrelated changes | Implementation |
| 10 | deployment-verification-agent | Go/No-Go checklists with SQL queries, rollback procedures, monitoring plans | Implementation |
| 11 | dhh-rails-reviewer | Rails anti-patterns, JS framework contamination, convention violations | Implementation (Rails) |
| 12 | kieran-rails-reviewer | Rails quality, Turbo streams, namespacing, service extraction signals | Implementation (Rails) |
| 13 | kieran-python-reviewer | Type hints, PEP 8, pathlib, modern Python patterns | Implementation (Python) |
| 14 | kieran-typescript-reviewer | Type safety, strict null checks, discriminated unions, import org | Implementation (TS) |
| 15 | julik-frontend-races-reviewer | Race conditions, DOM lifecycle, event handler disposal, animation restart | Implementation (Frontend) |

Plus 1 research agent:
- **learnings-researcher** — searches docs/solutions/ for past issues related to current work (runs on every review)

### Key Observations

**All 15 agents are implementation-focused.** Not one reviews requirements, outcomes, or design decisions. The architecture-strategist comes closest but checks code-level patterns (SOLID, component boundaries), not "does this design achieve the stated goals?"

**Named after real people.** kieran-* (CTO), dhh-* (Rails creator's philosophy), julik-* (colleague with frontend expertise). They encoded individual reviewer expertise as agents. This is the Instruction Sharpener pattern applied organically.

**Born from pain, not methodology.** Schema-drift-detector, data-migration-expert, deployment-verification-agent were added after production incidents. No published methodology for why these 15 — they built what they needed for their stack (Rails + Hotwire).

**Stack-specific defaults:**
- Rails: kieran-rails + dhh-rails + code-simplicity + security + performance (5 agents)
- Python: kieran-python + code-simplicity + security + performance (4 agents)
- General: code-simplicity + security + architecture + performance (4 agents)
- Always-on: agent-native-reviewer + learnings-researcher (2 agents)
- Conditional: schema-drift + data-migration + deployment-verification (0-3 agents, if DB changes)

**Typical run: 7-10 parallel agents, not 12.**

### The Learning Loop

The most novel feature. `/compound` captures solutions to `docs/solutions/` with YAML frontmatter. Then `learnings-researcher` surfaces past solutions on every future review. This is correction-compounding for codebases — solve a problem once, never miss it again.

Five parallel subagents for capture: context analyzer, solution extractor, related docs finder, prevention strategist, category classifier. Then specialized reviewers validate the documentation based on problem type.

### Consolidation

Not algorithmic consensus — orchestrator-level synthesis. Main agent reads all subagent reports, deduplicates, categorizes (security/performance/architecture/quality), assigns severity (P1 blocks merge, P2 important, P3 nice-to-have), estimates effort.

**P1 findings block merge.** This is the "implementation errors as quality signals" pattern — certain findings should halt progress, not get patched around.

---

## adversarial-spec: Multi-LLM Debate

### Architecture

Claude is the control plane. Python CLI (`debate.py`) is stateless — runs one round of parallel model calls and exits. Claude orchestrates multi-round debate, synthesis, and decision-making via SKILL.md instructions.

**Models never talk to each other.** Parallel fan-out, Claude synthesizes. Not a true debate graph.

### Focus Areas (6)

| Focus | What It Checks |
|-------|---------------|
| security | Auth, input validation, SQLi/XSS/CSRF, secrets, API rate limiting, privilege escalation |
| scalability | Sharding, caching, queues, connection pooling, microservice boundaries, capacity planning |
| performance | Latency targets (p50/p95/p99), N+1, memory leaks, network round trips |
| ux | User journeys, error states, loading states, WCAG, mobile/desktop, onboarding |
| reliability | Failure modes, circuit breakers, retries, SLA/SLO, incident response, graceful degradation |
| cost | Infrastructure projections, utilization, auto-scaling, build vs buy, operational overhead |

### Personas (10)

| Persona | Perspective |
|---------|------------|
| security-engineer | 15yr AppSec, thinks like an attacker |
| oncall-engineer | Will be paged at 3am — observability, runbooks, debuggability |
| junior-developer | Flags ambiguity, tribal knowledge, decisions that should be in the spec |
| qa-engineer | Missing test scenarios, edge cases, boundary conditions, untestable requirements |
| site-reliability | Deployment, rollback, monitoring, alerting, capacity planning |
| product-manager | User value, success metrics, scope clarity, does it solve the stated problem? |
| data-engineer | Data models, data flow, ETL, analytics requirements, data quality |
| mobile-developer | API from mobile perspective — payload sizes, offline support, battery impact |
| accessibility-specialist | WCAG, screen readers, keyboard nav, color contrast, inclusive design |
| legal-compliance | GDPR, CCPA, terms of service, liability, audit, regulatory |

**Key limitation:** Focus and persona apply uniformly to ALL models per round. Cannot assign different personas to different models simultaneously. One persona + one focus per round.

### Skepticism of Early Consensus

The `--press` mechanism. If any model says `[AGREE]` in rounds 1-2, Claude re-invokes with a different prompt demanding the model:
1. List 3+ specific sections it reviewed
2. Explain WHY it agrees
3. Identify remaining concerns, however minor

**This is a prompt instruction to Claude, not automated logic.** The "within first 2 rounds" heuristic lives in SKILL.md prose.

### Interview Mode (8 Topics)

1. Problem & Context — what problem, what happens if unsolved, who feels it, prior attempts
2. Users & Stakeholders — user types, technical sophistication, privacy, devices
3. Functional Requirements — core journey step by step, decision points, error/edge cases
4. Technical Constraints — integrations, perf requirements, scale now + 2 years, regulatory
5. UI/UX Considerations — desired experience, critical flows, information density
6. Tradeoffs & Priorities — what gets cut first, speed vs quality vs cost, non-negotiables
7. Risks & Concerns — what keeps you up at night, failure modes, bad assumptions
8. Success Criteria — how to know it succeeded, metrics, minimum viable outcome

Guidelines: "Challenge assumptions," "look for contradictions," "ask about things the user hasn't mentioned but should have."

### Notable Design Patterns

- **preserve-intent prompt** — fights homogenization toward bland consensus. Removals require justification (like code review). Distinguishes errors from preferences. Important pattern for adversarial review.
- **Binary consensus** — every participant must `[AGREE]` or debate continues. No partial agreement, no scoring. Simple but effective.
- **Temperature 0.7** — relatively high for review tasks, encourages diverse critique.
- **No eval framework** — no measurement of review quality, false positive/negative rates.

---

## The Gap: What Neither Project Reviews

### Requirements / Outcomes Review (parallax:calibrate territory)

**Neither project does this.** adversarial-spec's interview mode is the closest — it gathers requirements but doesn't review them against outcomes. No one asks:
- Do these requirements actually achieve the stated goals?
- Are the success criteria measurable and sufficient?
- What outcome would tell us this design failed even if implemented correctly?
- Are there unstated assumptions that would invalidate the requirements?

### Design Review (parallax:review territory)

**adversarial-spec does spec review, not design review.** It debates whether a PRD/tech spec is complete and production-ready. It does not:
- Review architecture decisions against requirements
- Check for requirement coverage (does every must-have have a design element?)
- Identify design decisions that create unnecessary coupling
- Evaluate alternatives that weren't considered

**compound-engineering's architecture-strategist** reviews code-level patterns, not design documents.

### Implementation as Spec Signal (the self-error-detecting concept)

**compound-engineering partially does this** — P1 findings block merge. But the escalation path is "fix the code," not "question the spec."

What parallax should do differently: certain implementation findings (not style issues or bugs, but "this can't work because the design assumed X which isn't true") should trigger escalation back to design/requirements, not just a code fix. The implementation review should classify findings as:

| Type | Action |
|------|--------|
| **Bug** | Fix in implementation |
| **Style/quality** | Fix in implementation |
| **Design assumption violated** | Escalate to design review — spec quality problem |
| **Requirement missing** | Escalate to requirements — calibration problem |
| **Fundamental incompatibility** | Full cycle restart with updated constraints |

This classification is the novel contribution. No existing tool distinguishes "fix the code" from "the spec was wrong."

---

## Patterns to Adopt

1. **Named personas from real expertise** (compound-engineering) — encode specific reviewers' blind spots and strengths, not generic "be critical"
2. **Skepticism of early consensus** (adversarial-spec) — demand justification for agreement, not just agreement
3. **Preserve-intent prompt** (adversarial-spec) — fight homogenization, require justification for removals
4. **Learning loop** (compound-engineering) — capture findings for reuse, surface past solutions automatically
5. **Stack-specific defaults with overrides** (compound-engineering) — not one-size-fits-all review
6. **Finding severity that gates progress** (compound-engineering) — P1 blocks, not everything is advisory
7. **Interview mode structure** (adversarial-spec) — 8 topics for requirements gathering, "challenge assumptions"

## Patterns to Improve On

1. **Differentiated perspectives per round** — adversarial-spec applies one persona to all models. Parallax should assign different perspectives simultaneously.
2. **Finding classification** — neither tool distinguishes "fix implementation" from "spec was wrong." This is the self-error-detecting concept.
3. **Eval instrumentation** — neither tool measures review quality. Parallax:eval should track false positive/negative rates, finding value, and reviewer calibration.
4. **Cross-phase consistency** — compound-engineering reviews implementation. adversarial-spec reviews specs. Neither checks that the implementation matches the spec. parallax needs this.
5. **Outcome-focused requirements review** — neither tool reviews whether requirements achieve stated goals.

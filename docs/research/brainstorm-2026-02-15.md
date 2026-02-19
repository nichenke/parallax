# Parallax Brainstorm Session — 2026-02-15

**Context:** Initial brainstorming session that led to repo creation. Explored 7 investigation tracks across competing tools, testing approaches, agent architectures, and automation strategies.

---

## Topic 0: Competing Skills & Meta-Skill Landscape

**Finding:** The design orchestrator concept is genuinely novel. No tools automate brainstorm → design → adversarial review → plan → execute for software design.

**Key gaps identified:**
- Adversarial design review: completely unmet need (only Mitsubishi's proprietary manufacturing AI)
- Design-specific evals: nothing exists for "did this design satisfy requirements?"
- Self-improving skill frameworks: research-stage only (GPT-5 scores 17.9/100 on StuLife benchmark)

**Meta-skill analysis as a skill:** Periodic scanning for SOTA changes in the skill/agent space. Could be a cron job that files GitHub Issues for promising leads. No production framework for this exists — would be novel.

**Action:** See landscape-analysis.md for full competitive analysis.

---

## Topic 1: Black-Box Testing

**Approach:** Use real design sessions as test cases. Feed a project state to the orchestrator and validate its behavior against known-good outcomes.

**Test cases identified:**

| Case | From | What It Tests |
|------|------|---------------|
| Second Brain Design | openclaw | Full review cycle — 3 parallel reviews, 40+ findings, 4 revisions |
| Semantic Memory Search | openclaw | Iteration tracking — status says "post-review" but artifact missing |
| Phase 4 Plan | openclaw | Missing review detection — went straight from options to plan |
| claude-ai-customize | local repo | Phase detection — frozen at "plan complete, execution pending" |

**Validation criteria:**
1. Phase identification accuracy
2. Appropriate review spawning
3. Design-to-plan consistency checking
4. Review artifact completeness enforcement
5. Finding resolution tracking
6. Cost/time overhead vs manual

**Outcome data needed:**
- Session recordings with timestamps
- Finding counts and severity distributions per review
- Iteration counts before convergence
- Token usage per phase
- Human satisfaction scores

---

## Topic 2: Bill/Ryker Agent Architecture

**Question:** Can Bill (the OpenClaw agent) build and test this autonomously?

**Answer:** Partially. Needs significant capability additions and a separate agent is worth it for isolation.

**What Bill can do today:** File Issues, manage memory, Slack, cron, gh CLI in sandbox

**What a skill R&D agent (Ryker) would need:**
- Opus model access
- Claude Agent SDK for long-running sessions
- Eval infrastructure (Inspect AI or Batch API)
- Write access to this public repo (separate PAT)

**Security analysis:**

| Concern | Mitigation |
|---------|-----------|
| Public repo write = new attack surface | Separate PAT scoped to parallax only |
| Opus costs ~10x Haiku | Budget caps, Haiku for eval runs |
| Long sessions harder to audit | Checkpoint logging to Slack |
| New service on VM | Separate Docker network, separate agent config |

**Verdict:** Separate Ryker agent is worth it. Meaningful isolation, different risk profile, separate cost tracking.

---

## Topic 3: Public Repo Strategy

**Decision:** Build in `nichenke/parallax` (public).

**Rationale:**
- Useful beyond personal infra
- Helps at work (shared design review tooling)
- Community feedback opportunity
- Could become Claude Code plugin

---

## Topic 4: Agent Teams & Codex

**Concept:** Run multiple agents on same review task with different prompts/models. Compare quality and coverage.

**Hybrid strategy:**
- Claude for design phases (stronger reasoning, more thorough)
- Codex for execution phases (cheaper, native parallelism, 3x token-efficient)
- Cross-model adversarial review (Claude reviews Codex output and vice versa)

**Codex state (Feb 2026):** GPT-5.3-Codex, cloud-first, free tier, API at $1.25/1M input tokens. Philosophy: "Move fast, iterate" vs Claude's "Measure twice, cut once."

---

## Topic 5: Skill Testing / Eval Framework

**Foundation:** Inspect AI (UK AISI) — built for agent workflows, 100+ evals, supports Claude + Codex.

**Test types needed:**

| Type | What It Validates |
|------|------------------|
| Unit | Single skill behavior |
| Integration | Skill composition hand-offs |
| System | Full pipeline completion |
| Smoke | Basic sanity (skill loads) |
| Performance | Speed/token usage |
| Cost | Dollar efficiency per outcome |
| Ablation | Component contribution (what happens without review phase?) |
| Adversarial | Robustness to bad input |
| Regression | No degradation from changes |

**Novel skill-specific tests:**
- Plant intentional flaws, measure detection rate
- A/B test reviewer prompts for finding quality
- Compare N-reviewer vs (N+1)-reviewer diminishing returns

---

## Topic 6: Claude-Native Background Automation

**Architecture:** OpenClaw cron → Claude Agent SDK research agent → MCP tools → Slack checkpoints → GitHub Issues/PRs

**Key building blocks (all production-ready):**
- **Claude Agent SDK** (Jan 2026) — standalone agent as systemd service
- **OpenClaw cron** — scheduling triggers
- **MCP** — standardized tool access (industry standard, adopted by OpenAI/Google/Microsoft)
- **Batch API** — 50% cost discount for parallel eval runs
- **Multi-session pattern** — Anthropic guidance for tasks spanning context windows

**What doesn't exist yet:**
- Turnkey "background deep research" product — must be assembled from components
- Skill development CI/CD pipeline — must be built
- SOTA monitoring scanner — must be built

**Phased approach:**
1. PoC: One research question, Agent SDK agent, checkpoint to Slack
2. Eval loops: Skill spec → generate → test → iterate
3. SOTA scanner: Weekly cron, search, file Issues for leads

---

## Next Steps

All topics filed as GitHub Issues in nichenke/parallax. Each is a separate investigation session.

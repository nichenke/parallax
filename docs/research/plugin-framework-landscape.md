# Claude Code Plugin Framework Landscape

**Research Date:** 2026-02-15
**Purpose:** Evaluate alternatives to superpowers as a foundation for parallax
**Trigger:** User has used superpowers for ~1 month; coworker reported coding skills "complex and slower, not achieving better results"; need to validate foundation choice before building on it.

---

## Key Findings

### 1. No one has built what parallax aims to build.

The landscape analysis conclusion holds under deeper scrutiny. No design-focused orchestration framework with adversarial multi-perspective review exists.

### 2. Two projects deserve serious study.

**compound-engineering** (EveryInc) — closest philosophical match to parallax
**adversarial-spec** (zscole) — closest implementation match to parallax:review

### 3. No formal evaluations exist for any plugin.

Zero benchmarks, zero comparative studies. This is the gap parallax:eval would fill.

---

## Project Comparison

### superpowers (obra/superpowers) — Current Foundation

| Metric | Value |
|--------|-------|
| Stars | ~52k |
| Skills | 13 core |
| Focus | Structured software development — planning, TDD, subagent execution |

**Relevance to parallax:** Provides brainstorming, writing-plans, executing-plans, dispatching-parallel-agents. Composable architecture. Largest community. In official Anthropic plugin directory.

**Gaps:** No adversarial review. No multi-perspective critique. Skills are execution-oriented, not design-reasoning-oriented.

**The "complex and slower" feedback:** Superpowers' overhead (Socratic questioning, mandatory planning, TDD enforcement) adds genuine value on complex multi-step work but creates friction on simple tasks. This is by design — the discipline prevents expensive mistakes. Whether this helps or hurts depends on task complexity, not just user skill.

---

### compound-engineering (EveryInc/compound-engineering-plugin) — Best Alternative

| Metric | Value |
|--------|-------|
| Stars | ~8.9k |
| Release | v0.5.1 (Feb 12, 2026) |
| Components | 29 agents, 22 commands, 19 skills |
| License | MIT |

**What it does:** Four-stage cycle: `/plan` -> `/work` -> `/review` -> `/compound`. The philosophy: each unit of engineering work should make subsequent units easier. 80% planning+review, 20% execution.

**Why it matters for parallax:**
- `/review` uses **12 parallel subagents**, each checking from a different angle (security, performance, over-engineering, etc.). This is architecturally very close to parallax:review.
- `/compound` captures learnings as reusable prompts in the codebase — a learning loop. Directly relevant to parallax:eval's feedback loop and the correction-compounding concept.
- 80/20 planning-over-execution philosophy aligns with parallax's design-phase focus.

**Gaps:** Review agents are code-focused, not design/architecture-focused. Learning loop is prompt-level (text), not eval-level (measured and scored). No adversarial debate — subagents critique independently but don't challenge each other.

---

### adversarial-spec (zscole/adversarial-spec) — Most Directly Relevant

| Metric | Value |
|--------|-------|
| Stars | ~487 |
| Focus | Multi-LLM adversarial debate for spec refinement |

**What it does:** Sends specs to GPT, Gemini, Grok, and other models in parallel for critique. Claude synthesizes feedback and revises. Iterates until all models reach consensus.

**Why it matters for parallax:**
- **Validates the adversarial debate approach** for design artifacts — someone independently built exactly this.
- **Skepticism of early consensus** — models must justify agreement rather than rubber-stamp. This is a key pattern parallax:review should adopt.
- Focus modes (security, scalability, performance, UX, reliability, cost) map directly to parallax reviewer personas.
- Model personas (security engineer, on-call engineer, QA, compliance) are the reviewer persona concept.
- Session persistence with auto-checkpointing, cost tracking per round.

**Gaps:** Spec-focused only (PRD/tech spec), not full design pipeline. No eval framework. Small community (487 stars). Requires multi-provider API keys.

**Verdict:** Don't build on it. Study it intensely. It's the closest existing implementation to parallax's core differentiator.

---

### Other Notable Projects

| Project | Stars | Relevance |
|---------|-------|-----------|
| **oh-my-claudecode** (Yeachan-Heo) | 6.3k | Model routing patterns, 7 execution modes. Reference for parallax:orchestrate. |
| **claude-flow** (ruvnet) | 14.1k | MCP-based architecture, consensus mechanism. Credibility concerns with self-reported benchmarks. |
| **claude-code-skills** (levnikolaevich) | 89 | 28 parallel auditors — largest multi-perspective review implementation found. Architecture reference. |
| **everything-claude-code** (affaan-m) | 46.5k | Config aggregation. AgentShield red-team/blue-team pattern useful reference. |
| **anthropics/skills** (official) | 70k | Defines the skill spec format. No design/planning skills. |

---

## Updated Foundation Options

The original three-option framework should expand to four:

| Approach | Evaluation |
|----------|------------|
| **EXTEND superpowers** | Largest community, well-known, composable. Pipeline is execution-oriented. |
| **EXTEND compound-engineering** | Better philosophical fit (planning-heavy, multi-agent review, learning loop). Smaller community. |
| **Clean-room build** | Slower but cleanest. The novel parts must be original regardless. |
| **Bootstrap then evaluate** | Pragmatic: build v0.1 with either scaffolding, eval the foundation choice with your own framework. |

## Recommendation

The novel parts of parallax (adversarial review, calibration, design-specific eval) are the core differentiator and must be original work regardless of foundation choice. The scaffolding (subagent dispatch, plan state, pipeline management) is solved by multiple projects.

Pick whichever scaffolding you're most productive with today. Keep the dependency isolated enough to swap later. Study adversarial-spec's codebase before building parallax:review.

---

## Sources

- [obra/superpowers](https://github.com/obra/superpowers) — 52k stars
- [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) — 8.9k stars
- [zscole/adversarial-spec](https://github.com/zscole/adversarial-spec) — 487 stars
- [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) — 6.3k stars
- [ruvnet/claude-flow](https://github.com/ruvnet/claude-flow) — 14.1k stars
- [anthropics/skills](https://github.com/anthropics/skills) — 70k stars
- [levnikolaevich/claude-code-skills](https://github.com/levnikolaevich/claude-code-skills) — 89 stars

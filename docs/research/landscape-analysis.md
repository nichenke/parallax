# Design Orchestrator Landscape Analysis (February 2026)

**Research Date:** 2026-02-15
**Purpose:** Competitive landscape for multi-perspective design orchestration

---

## Executive Summary

1. **No design-focused orchestration exists** — existing tools are code-execution-centric
2. **Adversarial design review is largely unmet** — adversarial-spec (zscole) does spec-level debate, Mitsubishi announced manufacturing AI (Jan 2026), but nothing general-purpose for design/architecture review
3. **Strong building blocks available** — LangGraph, Inspect AI, Claude Code Swarms, compound-engineering (15 review agents, learning loop)
4. **Meta-skill self-improvement is research-stage** — GPT-5 scores 17.9/100 on self-evolving agent benchmarks
5. **Codex offers hybrid opportunity** — cheaper parallel execution, Claude better for design reasoning

---

## 1. Claude Code Ecosystem

**Existing orchestration:**
- **superpowers** (obra, 52k stars) — 13 skills: brainstorming, planning, execution, TDD, debugging. Execution-oriented. Largest community. Current working environment.
- **compound-engineering** (EveryInc, 8.9k stars) — 15 parallel review agents, `/compound` learning loop, 80/20 planning-over-execution. All agents are implementation-focused. Closest architectural match for multi-agent review.
- **adversarial-spec** (zscole, 487 stars) — Multi-LLM adversarial debate for spec refinement. Skepticism of early consensus, focus modes, model personas. Narrow (specs only, no eval) but validates the adversarial review hypothesis.
- **Claude-flow** (ruvnet/claude-flow, 14k stars) — agent swarm platform, MCP-based. Heavy infrastructure, credibility concerns with self-reported benchmarks.
- **oh-my-claudecode** (Yeachan-Heo, 6.3k stars) — 32 specialized agents, 7 execution modes, model routing. Execution-oriented.
- **Swarms mode** (native) — TeammateTool, task delegation

See `plugin-framework-landscape.md` and `review-agent-analysis.md` for detailed analysis.

**Gap:** No skills for brainstorm → design → review → plan pipeline. Execution-phase skills mature, design-phase orchestration uncharted. compound-engineering and adversarial-spec are the nearest neighbors but neither does design-phase orchestration with finding classification.

## 2. Agent Orchestration Frameworks

| Framework | Best For | Relevance |
|-----------|----------|-----------|
| **LangGraph** | Stateful graph workflows, conditional logic | **HIGH** — natural fit for design pipeline |
| **CrewAI** | Role-based teams | MEDIUM — roles map to phases but rigid |
| **AutoGen** | Multi-agent conversations | LOW-MEDIUM — good for brainstorming, too loose for pipeline |
| **MetaGPT** | Software company simulation | MEDIUM — overlaps in architecture phase |
| **ChatDev** | Waterfall SDLC | LOW-MEDIUM — phase-based but execution-heavy |
| **OpenHands** | Cloud coding agents | MEDIUM — execution backend potential |

**Industry:** 1,445% surge in multi-agent inquiries, 86% of $7.2B copilot spend on agents.

## 3. Adversarial Review Tools

**Code review (mature):** CodeRabbit, Qodo, Aikido — all code-focused, not design
**LLM red-teaming:** Mindgard, Garak, Promptfoo — security/robustness, not design critique
**Design review:** adversarial-spec does multi-LLM debate for PRD/tech specs (parallel fan-out, Claude synthesizes, skepticism of early consensus). Mitsubishi's proprietary manufacturing AI. Nothing general-purpose for design/architecture review beyond specs.

**This is the core opportunity.** General-purpose adversarial design review — with finding classification that routes back to the phase that failed — is an unmet need. adversarial-spec validates the debate approach but is narrow (specs only, no eval, no finding classification).

## 4. Eval Frameworks

| Framework | Relevance | Notes |
|-----------|-----------|-------|
| **Inspect AI** | **VERY HIGH** | Built for agent workflows, 100+ evals, supports Claude + Codex |
| **Braintrust** | HIGH | Integrated prompt engineering, LLM-as-judge, CI/CD |
| **Promptfoo** | MEDIUM | Open-source prompt testing, good for individual agent prompts |
| **LMSYS Arena** | LOW | Human-in-the-loop, too slow for automated pipeline |

**Gap:** No design-specific evals. Need custom dataset for "Does this design satisfy requirements?" and "Did the reviewer catch the planted flaw?"

## 5. OpenAI Codex (GPT-5.3-Codex)

- Cloud-first, native parallelism, 3x more token-efficient than Claude
- Free tier launched Feb 2026
- **Hybrid opportunity:** Claude for design phases (stronger reasoning), Codex for execution (cheaper, parallel)
- API: $1.25/1M input tokens

**Near-term action:** Set up a lightweight Codex workflow early — not a formal integration, but enough to run portability sanity checks. Goal: can a parallax skill run on Codex CLI and produce a reasonable result? Surfaces Claude-specific assumptions before they're baked in. Budget already allocated ($50-100/mo via work partnership).

**Multi-LLM review (later):** adversarial-spec's multi-model debate pattern (Claude + GPT + Gemini reviewing the same artifact) is worth testing during the eval phase to see if model diversity adds review quality beyond prompt diversity alone. Not a near-term priority — adopt the debate patterns first, test multi-model later.

## 6. Self-Improving Agents (Meta-Skills)

**Research-stage, not production-ready:**
- Metacognitive learning (OpenReview) — agents reflect on own learning process
- Meta-prompting — LLMs iteratively improve own prompts
- Evolver (aiXplain) — early meta-agent, platform-specific
- StuLife benchmark — GPT-5 scores only 17.9/100

**Recommendation:** Defer to Phase 3+. Focus on core pipeline first.

---

## Build vs Leverage

| Component | Decision | Rationale |
|-----------|----------|-----------|
| Orchestration engine | **START** with Claude Code native (skills, subagents, Task tool). Evaluate LangGraph when native orchestration hits limits. | Test native capabilities first; LangGraph solves problems (persistent state, headless runs, complex branching) we may not have yet. Revisit when pipeline needs to run outside a Claude Code session, state management gets hacky, or branching outgrows skill prompts. |
| Adversarial review | **BUILD** custom | Core differentiator, nothing exists |
| Design templates | **BUILD** | Design-specific, no off-the-shelf |
| Eval framework | **LEVERAGE** Inspect AI | Built for agent workflows |
| Brainstorming | **OPEN** — see below | Bootstrap problem: superpowers vs clean-room |
| Review orchestration | **BUILD** informed by compound-engineering + adversarial-spec | 15-agent parallel pattern and debate-to-consensus pattern are references; finding classification is novel |
| Document chain / RFC | **BUILD** | No off-the-shelf; pipeline artifacts consolidate into reviewable RFC |
| Execution | **LEVERAGE** existing skills / Codex | Mature ecosystem |
| Self-improvement | **DEFER** | Research-stage |

---

## Open: Superpowers as Foundation

**The bootstrap problem:** Parallax aims to orchestrate and evaluate design workflows. The superpowers plugin already has `brainstorming`, `writing-plans`, `executing-plans`, and `dispatching-parallel-agents` skills. Building on these is the fastest path to a working prototype — but it creates a circularity risk: evaluating superpowers-based orchestration using superpowers-built tooling.

**Four options:**

| Approach | Pros | Cons |
|----------|------|------|
| **EXTEND superpowers** | Fastest to prototype. Composable. Largest community (52k stars). Current working environment. | Circular evaluation. Hard to attribute value (parallax vs superpowers). Coupled to superpowers' design assumptions. Execution-oriented, not design-oriented. |
| **EXTEND compound-engineering** | Better philosophical fit (80/20 planning-over-execution). 15-agent parallel review architecture. Learning loop. | Smaller community (8.9k stars). Less familiar. All review agents are implementation-focused — would need new design-focused agents regardless. |
| **Clean-room build** | Unbiased evaluation. Full architectural control. Clear attribution. | Slower. Reinvents solved problems (subagent dispatch, plan state). May diverge unnecessarily. |
| **Bootstrap then evaluate** | Use superpowers or compound-engineering to build v0.1, then evaluate the foundation as one of the first test cases. Re-evaluate with data. | Requires discipline to actually re-evaluate. Sunk cost bias. But gives a working prototype to evaluate *with*. |

**Key sub-questions:**
1. Is there sufficient independent evaluation of superpowers skills today to make a risk-bet? (As of Feb 2026: no formal evals exist — superpowers skills are used but not benchmarked.)
2. If we bootstrap with superpowers, what's the minimum viable prototype needed before we can meaningfully evaluate the foundation choice?
3. Can we isolate the superpowers dependency enough that swapping it out later isn't a rewrite?

**Current lean:** No decision yet. This is one of the first things the eval framework (Track 5) should answer.

---

## Sources

Full source list with 60+ citations available in the original research document.

Key references:
- [obra/superpowers](https://github.com/obra/superpowers) — skills framework (52k stars)
- [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) — compound engineering (8.9k stars)
- [zscole/adversarial-spec](https://github.com/zscole/adversarial-spec) — multi-LLM spec debate (487 stars)
- [Inspect AI](https://inspect.aisi.org.uk/) — UK AISI eval framework
- [LangGraph](https://github.com/langchain-ai/langgraph) — stateful graph workflows
- [Mitsubishi Electric Multi-Agent AI](https://us.mitsubishielectric.com/en/pr/global/2026/0120/)
- [Adversarial Multi-Agent Evaluation of LLMs](https://openreview.net/forum?id=06ZvHHBR0i)
- [Awesome Self-Evolving Agents](https://github.com/EvoAgentX/Awesome-Self-Evolving-Agents)
- [Claude Code Multiple Agent Systems Guide](https://www.eesel.ai/blog/claude-code-multiple-agent-systems-complete-2026-guide)

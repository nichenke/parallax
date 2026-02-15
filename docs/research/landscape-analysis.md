# Design Orchestrator Landscape Analysis (February 2026)

**Research Date:** 2026-02-15
**Purpose:** Competitive landscape for multi-perspective design orchestration

---

## Executive Summary

1. **No design-focused orchestration exists** — existing tools are code-execution-centric
2. **Adversarial design review is an unmet need** — Mitsubishi announced adversarial debate AI (Jan 2026) but nothing general-purpose
3. **Strong building blocks available** — LangGraph, Inspect AI, Claude Code Swarms
4. **Meta-skill self-improvement is research-stage** — GPT-5 scores 17.9/100 on self-evolving agent benchmarks
5. **Codex offers hybrid opportunity** — cheaper parallel execution, Claude better for design reasoning

---

## 1. Claude Code Ecosystem

**Existing orchestration:**
- **Claude-flow** (ruvnet/claude-flow) — agent swarm platform, general-purpose
- **oh-my-claudecode** — 32 specialized agents, 40+ skills, pre-built teams
- **Swarms mode** (native) — TeammateTool, task delegation
- **Engineering-workflow-plugin** — git, testing, code review

**Gap:** No skills for brainstorm → design → review → plan pipeline. Execution-phase skills mature, design-phase orchestration uncharted.

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
**Design review:** **NOTHING EXISTS** except Mitsubishi's proprietary manufacturing AI

**This is the core opportunity.** Adversarial design/architecture review is a completely unmet need.

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
| Orchestration engine | **LEVERAGE** LangGraph / Claude Code Swarms | Mature primitives |
| Adversarial review | **BUILD** custom | Core differentiator, nothing exists |
| Design templates | **BUILD** | Design-specific, no off-the-shelf |
| Eval framework | **LEVERAGE** Inspect AI | Built for agent workflows |
| Brainstorming | **ADAPT** AutoGen patterns | Multi-agent discussion exists |
| Execution | **LEVERAGE** existing skills / Codex | Mature ecosystem |
| Self-improvement | **DEFER** | Research-stage |

---

## Sources

Full source list with 60+ citations available in the original research document.

Key references:
- [Inspect AI](https://inspect.aisi.org.uk/) — UK AISI eval framework
- [LangGraph](https://github.com/langchain-ai/langgraph) — stateful graph workflows
- [Mitsubishi Electric Multi-Agent AI](https://us.mitsubishielectric.com/en/pr/global/2026/0120/)
- [Adversarial Multi-Agent Evaluation of LLMs](https://openreview.net/forum?id=06ZvHHBR0i)
- [Awesome Self-Evolving Agents](https://github.com/EvoAgentX/Awesome-Self-Evolving-Agents)
- [Claude Code Multiple Agent Systems Guide](https://www.eesel.ai/blog/claude-code-multiple-agent-systems-complete-2026-guide)

# Research Report: GradientHQ/parallax (Name Collision Assessment)

**Date:** 2026-02-17
**Investigator:** Claude Opus 4.6
**Issue context:** Investigate whether GradientHQ's "Parallax" project creates a naming conflict for our parallax project

---

## Executive Summary

**GradientHQ/parallax is a distributed LLM inference engine** — it pools heterogeneous consumer hardware (GPUs, Apple Silicon) into a decentralized cluster for serving open-source LLMs. It has **zero functional overlap** with our project. The two projects share a name but operate in completely different domains: theirs is infrastructure-layer model serving, ours is application-layer design review orchestration. The name collision is real but the confusion risk is low given how different the audiences and use cases are.

---

## What It Is

GradientHQ/parallax is a fully decentralized inference engine developed by [Gradient Network](https://gradient.network) that enables users to build distributed AI clusters for serving large language models across heterogeneous hardware. It was open-sourced in November 2025 and has an accompanying [academic paper on arXiv](https://arxiv.org/abs/2509.26182) (submitted September 2025). The core problem it solves is running LLMs that are too large for a single consumer device by sharding the model across multiple machines connected over standard internet connections.

The system turns a collection of consumer-grade devices — laptops with Apple Silicon, desktops with NVIDIA GPUs, mixed configurations — into a single logical inference endpoint. It supports 40+ open models including DeepSeek R1, Qwen3, Llama 3.x, and Kimi K2. It is **not** an agent framework, orchestration tool, or evaluation system. It is purely an inference serving layer, analogous to vLLM or SGLang but for decentralized/heterogeneous environments.

## Architecture

The system has three main layers:

1. **Runtime Layer** — The core orchestration engine for LLM serving. Contains:
   - Executor (control loop)
   - Model Shard Holder
   - Request Manager
   - Scheduler (two-phase: allocation + request-time routing)
   - Paged KV Cache Manager (continuous batching on Mac)

2. **Communication Layer** — P2P networking via Lattica, built on Hivemind's DHT. No central coordinator.

3. **Worker Layer** — GPU Workers (modified SGLang) + Apple Workers (custom MLX with Metal kernels).

## Project Vitals

| Metric | Value |
|--------|-------|
| GitHub stars | ~810 |
| First release | October 2025 (v0.0.1) |
| ArXiv paper | [2509.26182](https://arxiv.org/abs/2509.26182) |
| Product Hunt | #1 Product of the Day (Oct 2025) |
| Active development | Yes, regular releases through Feb 2026 |

## Overlap Assessment

| Dimension | GradientHQ/parallax | Our parallax |
|-----------|---------------------|--------------|
| Layer | Infrastructure (model serving) | Application (design review orchestration) |
| Input | Model weights, inference requests | Design documents, requirements |
| Output | Token completions | Classified findings (Critical/Important/Minor) |
| Core tech | Pipeline parallelism, DHT, KV cache | Claude Code skills, Inspect AI evals |
| Multi-agent | No (single inference endpoint) | Yes (6 reviewer personas, adversarial) |
| Eval | No | Yes (Inspect AI integration) |

## Verdict

**Not interesting for our needs. No integration value.**

Zero functional overlap. No capabilities that augment our design review pipeline. The name "parallax" is used with a different metaphorical intent — they reference distributed compute nodes seeing the same model from different positions; we reference the optical principle of multiple observer perspectives revealing truth about a design.

### Recommendation

- **Name collision is low-severity** for current project stage (Claude Code plugin namespace, not standalone package).
- **If project grows** toward standalone CLI or PyPI package, rename becomes more material for SEO/discoverability.
- **No integration** — completely different layer of the stack.

---

## Sources

- [GradientHQ/parallax GitHub](https://github.com/GradientHQ/parallax)
- [ArXiv Paper](https://arxiv.org/abs/2509.26182)
- [Gradient Launches Parallax Press Release](https://www.globenewswire.com/news-release/2025/11/06/3182435/0/en/Gradient-Launches-Parallax-a-Sovereign-AI-Operating-System-for-an-Open-Source-Future.html)
- [Gradient Parallax Documentation](https://docs.gradient.network/the-open-intelligence-stack/parallax)

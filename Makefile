DESIGN_DOC ?= docs/plans/parallax-design-v4.md
MODEL       ?= anthropic/claude-sonnet-4-5
LOG_DIR     ?= logs/
VENV        := .venv-evals/bin/activate

## ── Setup ──────────────────────────────────────────────────────────────────

setup:
	python3 -m venv .venv-evals
	. $(VENV) && pip install -e ".[dev]"
	mkdir -p logs/ evals/baselines/

install:
	. $(VENV) && pip install -e ".[dev]" -q

## ── Ground truth (run after significant design changes) ────────────────────

review:
	@echo "Run: parallax:review $(DESIGN_DOC) in Claude Code"
	@echo "Then: make validate"

validate:
	. $(VENV) && python tools/validate_findings.py

## ── Eval loop ───────────────────────────────────────────────────────────────

eval:
	mkdir -p $(LOG_DIR)
	. $(VENV) && inspect eval evals/severity_calibration.py \
	    --model $(MODEL) \
	    --log-dir $(LOG_DIR) \
	    --tags "git=$(shell git rev-parse --short HEAD)"

reviewer-eval:
	mkdir -p $(LOG_DIR)
	. $(VENV) && inspect eval evals/reviewer_eval.py \
	    --model $(MODEL) \
	    --log-dir $(LOG_DIR) \
	    --tags "git=$(shell git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"

ablation:
	mkdir -p $(LOG_DIR)
	. $(VENV) && inspect eval evals/ablation_tests.py \
	    --model $(MODEL) \
	    --log-dir $(LOG_DIR)

baseline:
	mkdir -p evals/baselines/
	cp $$(ls -t $(LOG_DIR)*.json | head -1) evals/baselines/v3_critical_baseline.json
	@echo "Baseline stored."

regression:
	. $(VENV) && python tools/compare_to_baseline.py

view:
	. $(VENV) && inspect view

## ── Full cycle ──────────────────────────────────────────────────────────────

cycle: eval regression view

## ── Tests ───────────────────────────────────────────────────────────────────

test:
	. $(VENV) && pytest tests/ -v

## ── Help ────────────────────────────────────────────────────────────────────

help:
	@echo "Ground truth creation:"
	@echo "  make review      Run fresh parallax review on design doc"
	@echo "  make validate    Open validation UI in browser (localhost:5000)"
	@echo ""
	@echo "Eval loop:"
	@echo "  make eval        Run severity calibration eval"
	@echo "  make reviewer-eval Run per-reviewer eval tasks (5 tasks)"
	@echo "  make ablation    Run ablation tests"
	@echo "  make baseline    Store latest run as baseline"
	@echo "  make regression  Compare latest run to baseline"
	@echo "  make view        Open Inspect View UI"
	@echo "  make cycle       eval + regression + view"
	@echo ""
	@echo "Other:"
	@echo "  make test        Run unit tests"
	@echo "  make setup       Create venv and install dependencies"
	@echo "  make install     Reinstall dependencies into existing venv"

.PHONY: setup install review validate eval reviewer-eval ablation baseline regression view cycle test help

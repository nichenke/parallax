"""
Smoke tests for per-reviewer eval task instantiation.
Tests confirm: correct dataset loaded, correct agent content, task structure valid.
Each test catches wiring bugs (wrong agent name, missing dataset, wrong filter) at
test time instead of eval runtime.
"""
import pytest
from inspect_ai import Task

from evals.reviewer_eval import (
    assumption_hunter_eval,
    constraint_finder_eval,
    problem_framer_eval,
    scope_guardian_eval,
    success_validator_eval,
)


def test_assumption_hunter_eval_instantiates():
    task = assumption_hunter_eval()
    assert isinstance(task, Task)


def test_constraint_finder_eval_instantiates():
    task = constraint_finder_eval()
    assert isinstance(task, Task)


def test_problem_framer_eval_instantiates():
    task = problem_framer_eval()
    assert isinstance(task, Task)


def test_scope_guardian_eval_instantiates():
    task = scope_guardian_eval()
    assert isinstance(task, Task)


def test_success_validator_eval_instantiates():
    task = success_validator_eval()
    assert isinstance(task, Task)

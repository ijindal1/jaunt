---
name: uv-python
description: Use when working with the `uv` Python package manager to create/manage virtual environments, install or sync dependencies, compile requirements, and troubleshoot Python dependency issues. Trigger for requests mentioning `uv`, `uv pip`, `uv venv`, `uv run`, `pyproject.toml`, `uv.lock`, `requirements.in`, `requirements.txt`, dependency locking/syncing, or migrating from pip/venv workflows to uv.
---

# uv (Python package manager)

## Overview

Use `uv` as the primary interface for Python environments and dependency management. Prefer deterministic installs (lock/sync) and verify exact subcommands/flags with `uv --help` / `uv pip --help` when in doubt.

## Repo Triage (Do First)

1. Identify the dependency source of truth:
- `pyproject.toml` present: project metadata is likely in `pyproject.toml`.
- `requirements.in` / `requirements.txt` present: requirements-based workflow.

2. Identify reproducibility artifacts:
- Lockfile present (ex: `uv.lock` or a pinned `requirements.txt`): prefer syncing from it.
- No lockfile: compile/generate one before syncing for CI/repro.

3. Identify the Python version expectation:
- Look for `.python-version`, `pyproject.toml` Python constraints, `runtime.txt`, or CI config.
- When creating a venv, explicitly choose a Python if the project requires it.

## Core Workflows

### 1) Create/Repair a Virtual Environment

1. If there is already a project venv convention (commonly `.venv/`), keep it.
2. Prefer uv for creation:
- `uv venv` (optionally `--python X.Y` to match project constraints)
3. When troubleshooting, verify which interpreter and site-packages are active before changing deps.

### 2) Install/Synchronize Dependencies (Requirements-Based)

Use this when the repo is driven by `requirements*.txt` (or you need pip-compatible behavior).

1. If you have `requirements.in` (unpinned), compile to a pinned file:
- Prefer `uv pip compile requirements.in -o requirements.txt` (or a pinned output like `requirements.lock`).
2. Sync the environment to exactly the pinned requirements:
- Prefer `uv pip sync requirements.txt` for deterministic installs.
3. If the user wants a quick, non-deterministic install:
- Use `uv pip install -r requirements.txt` (but call out that it may drift over time).

### 3) Update Dependencies (Requirements-Based)

1. Edit inputs (`requirements.in`, constraints files, etc.).
2. Re-compile pinned requirements.
3. Re-sync the environment.
4. If tests fail after an update, bisect by reverting the last dependency change or pinning a problematic transitive dependency.

### 4) Run Tools/Commands Under uv

When a user wants “run tests/lint/build but ensure deps are correct”, prefer `uv`-managed execution (ex: `uv run ...` if available in the installed uv) or run commands after a `uv pip sync ...` to avoid ambient/global Python contamination.

## Troubleshooting Checklist

1. Confirm you are in the intended environment (venv active, correct Python version).
2. Inspect dependency state:
- Use `uv pip freeze` (or pip-equivalent) and compare with the pinned requirements/lock.
3. Prefer `sync` to “make it match” instead of incremental installs.
4. If resolution/build fails:
- Capture the exact error, platform, Python version, and the command invoked.
- Try upgrading build tooling only if needed (and keep changes minimal).

## Reference

For command patterns, see `references/uv.md`.

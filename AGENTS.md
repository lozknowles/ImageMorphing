# AGENTS.md

## Purpose

This repository contains a local Python image morphing prototype with a few helper and experimental scripts. Changes should prioritize preserving the manual image-morph workflow in `image_morpher.py` while keeping generated outputs out of version control.

## Working Rules

- Treat `image_morpher.py` as the main user-facing script.
- Treat `experiments/` as non-production code unless a script is explicitly promoted into the main package.
- Keep edits ASCII unless the file already requires something else.
- Do not commit generated output directories such as `morph_output/`.
- Do not commit `__pycache__` or virtual environment folders.
- Prefer small, targeted fixes over broad refactors unless explicitly requested.
- If adding dependencies, update `requirements.txt` and `README.md` together.
- If adding development tooling, update `requirements-dev.txt`, `pyproject.toml`, and CI config together.
- If changing the local developer workflow, keep `scripts/dev.ps1` and `README.md` in sync.
- If changing behavior, update `CHANGELOG.md` in the same edit.

## Repo Notes

- `perf.py` appears unrelated to the main morphing workflow and should not be treated as core functionality without confirmation.
- Several scripts in `experiments/` are one-off utilities or prototypes; document any promotion into the main supported workflow.
- Public publication should include a quick secret scan for obvious API keys or credentials before push.

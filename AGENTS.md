# AGENTS.md

## Purpose

This repository contains a local Python image morphing prototype with a few helper and experimental scripts. Changes should prioritize preserving the manual image-morph workflow in `image_morpher.py` while keeping generated outputs out of version control.

## Working Rules

- Treat `image_morpher.py` as the main user-facing script.
- Keep edits ASCII unless the file already requires something else.
- Do not commit generated output directories such as `morph_output/`.
- Do not commit `__pycache__` or virtual environment folders.
- Prefer small, targeted fixes over broad refactors unless explicitly requested.
- If adding dependencies, update `requirements.txt` and `README.md` together.
- If changing behavior, update `CHANGELOG.md` in the same edit.

## Repo Notes

- `perf.py` appears unrelated to the main morphing workflow and should not be treated as core functionality without confirmation.
- Several scripts in the repo are experiments or one-off utilities; document any changes that make one of them part of the main supported workflow.
- Public publication should include a quick secret scan for obvious API keys or credentials before push.


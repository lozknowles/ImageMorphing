# Changelog

All notable changes to this project will be documented in this file.

## 2026-05-22

### Added

- Added `README.md` with project overview, setup, usage, limitations, and security note.
- Added `requirements.txt` based on imported Python dependencies found in the repository.
- Added `requirements-dev.txt` for development and test tooling.
- Added `AGENTS.md` with contributor guidance for future automated or human edits.
- Added `.gitignore` to exclude generated outputs, cache files, and local environment folders from Git.
- Added `pyproject.toml` with package metadata and pytest configuration.
- Added an `imagemorphing/` package to separate config, image operations, pipeline orchestration, UI code, and selection state.
- Added lightweight tests for configuration validation and point-selection behavior.
- Added CLI parsing tests and extra config validation coverage.
- Added a GitHub Actions CI workflow for dependency install, compile checks, and tests.
- Added `ruff`-based lint and format checks for the maintained code paths.
- Added mocked pipeline smoke tests.
- Added `scripts/dev.ps1` as a local developer task runner.

### Changed

- Hardened `image_morpher.py` input handling for invalid frame counts and invalid click coordinates.
- Improved `image_morpher.py` export handling so missing `ffmpeg` no longer crashes MP4 export.
- Hardened `resize.py` against empty / fully out-of-bounds crop saves.
- Fixed the `perf.py` exception path to return `no_update` correctly.
- Replaced the old monolithic `image_morpher.py` and `resize.py` implementations with thin entry points that delegate to the package modules.
- Split runtime and development dependencies and tightened them with compatible version ranges.
- Moved prototype and side-experiment scripts into `experiments/` to separate them from the maintained app modules.

### Checked

- Reviewed the repository for obvious API keys, tokens, passwords, and private key markers.
- No obvious secrets were found in the project files that were scanned.

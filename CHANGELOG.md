# Changelog

All notable changes to this project will be documented in this file.

## 2026-05-22

### Added

- Added `README.md` with project overview, setup, usage, limitations, and security note.
- Added `requirements.txt` based on imported Python dependencies found in the repository.
- Added `AGENTS.md` with contributor guidance for future automated or human edits.
- Added `.gitignore` to exclude generated outputs, cache files, and local environment folders from Git.

### Changed

- Hardened `image_morpher.py` input handling for invalid frame counts and invalid click coordinates.
- Improved `image_morpher.py` export handling so missing `ffmpeg` no longer crashes MP4 export.
- Hardened `resize.py` against empty / fully out-of-bounds crop saves.
- Fixed the `perf.py` exception path to return `no_update` correctly.

### Checked

- Reviewed the repository for obvious API keys, tokens, passwords, and private key markers.
- No obvious secrets were found in the project files that were scanned.


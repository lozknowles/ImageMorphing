# ImageMorphing

`ImageMorphing` is a local Python project for aligning and morphing one image into another. The main workflow uses a small desktop UI where you manually mark matching points on two images, then generates transition frames plus GIF and optional MP4 output.

## Current Status

This repository started as a prototype and now has a cleaner package structure around the core workflow. It contains:

- a main interactive morphing tool
- a resize / overlay adjustment helper
- several experimental morphing variants
- sample source images
- generated media artifacts kept locally but excluded from Git

## Project Structure

- `image_morpher.py`: stable entry point for the primary interactive morphing workflow
- `resize.py`: stable entry point for the overlay adjustment helper
- `auto_morph.py`: supported automatic morphing entry point using ORB feature matching
- `imagemorphing/config.py`: application configuration dataclasses
- `imagemorphing/automatic.py`: automatic ORB-based morphing pipeline promoted from experiments
- `imagemorphing/image_ops.py`: image loading, resizing, alignment, and blending helpers
- `imagemorphing/pipeline.py`: orchestration for frame generation and export
- `imagemorphing/ui.py`: Matplotlib-based morphing UI
- `imagemorphing/overlay_ui.py`: Matplotlib-based overlay adjustment UI
- `imagemorphing/point_selection.py`: reusable point-pair state management
- `collage.py`: GIF collage generation helper
- `experiments/`: archived prototype and side-experiment scripts moved out of the supported app surface
- `tests/`: lightweight tests for core non-UI behavior

## Requirements

The project now includes both `requirements.txt` and `pyproject.toml`. The dependency list is still lightweight and inferred from repository imports plus test tooling:

- `opencv-python`
- `numpy`
- `matplotlib`
- `imageio`
- `Pillow`
- `psutil`
- `dash`
- `dash-cytoscape`
- `pytest`

Install runtime dependencies with:

```bash
python -m pip install -r requirements.txt
```

For development, including tests:

```bash
python -m pip install -r requirements-dev.txt
```

Or, if you want to work from the package metadata:

```bash
python -m pip install -e .[dev]
```

## How To Run

Run the main app from the project root:

```bash
python image_morpher.py --base_image before.jpg --surrogate_image after.jpg --output_folder morph_output
```

Automatic ORB-based workflow:

```bash
python auto_morph.py --base_image before.jpg --surrogate_image after.jpg --output_folder morph_output
```

You can also treat the core logic as importable modules from the `imagemorphing` package rather than only as top-level scripts.

## Quality Workflow

- `pyproject.toml` defines package metadata and pytest settings.
- `requirements.txt` contains runtime dependencies.
- `requirements-dev.txt` layers test tooling on top of runtime dependencies.
- `.github/workflows/ci.yml` runs install, compile, and test checks on GitHub Actions.
- `.github/workflows/release.yml` builds distributions and publishes a GitHub release on version tags or manual dispatch.
- Current automated tests focus on config validation, point selection rules, CLI parsing behavior, and pipeline orchestration via mocks.
- `scripts/dev.ps1` provides local developer tasks for install, lint, format, test, and combined checks.

Example local commands:

```powershell
./scripts/dev.ps1 install
./scripts/dev.ps1 check
./scripts/dev.ps1 run-morph --base_image before.jpg --surrogate_image after.jpg
./scripts/dev.ps1 run-auto --base_image before.jpg --surrogate_image after.jpg
```

Then:

1. Click corresponding points on the base and surrogate images alternately.
2. Use at least 3 point pairs.
3. Click `Process` to generate output frames and animations.
4. Use `Clear Points` if you want to restart point selection.

## Output

The main script can produce:

- aligned intermediate images
- morphed JPG frame sequences
- animated GIFs
- MP4 video output if `ffmpeg` is installed and available on `PATH`

Generated outputs are ignored by Git through `.gitignore`.

## Security Check

A basic repository scan was performed before publication for common secrets such as API keys, tokens, passwords, and private key markers. No obvious API keys or secret material were found in the project source or text files that were reviewed.

## Known Limitations

- The app relies on manual point selection and has no automated matching in the main workflow.
- The automatic ORB-based workflow is now supported, but it remains less controllable than the manual point-selection path.
- Test coverage is still light and currently focuses on non-UI logic.
- There is no packaged installer, CLI release flow, or reproducible environment file beyond `requirements.txt`.
- The `experiments/` folder is intentionally not treated as production-grade code.

## Repo Notes

- Generated media is intentionally excluded from version control.
- Sample source images remain in the repository.
- The core app has been refactored away from script-level globals into reusable package modules.
- Runtime and development dependencies are now split for cleaner maintenance.
- Prototype scripts have been moved into `experiments/` to keep the main surface area clearer.

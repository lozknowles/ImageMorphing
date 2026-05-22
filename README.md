# ImageMorphing

`ImageMorphing` is a local Python project for aligning and morphing one image into another. The main workflow uses a small desktop UI where you manually mark matching points on two images, then generates transition frames plus GIF and optional MP4 output.

## Current Status

This repository is best described as a prototype / experimental project rather than a packaged production app. It contains:

- a main interactive morphing tool
- a resize / overlay adjustment helper
- several experimental morphing variants
- sample source images
- generated media artifacts kept locally but excluded from Git

## Main Scripts

- `image_morpher.py`: primary interactive image morphing workflow
- `resize.py`: drag / scroll overlay adjustment and save helper
- `affine.py`, `affine2.py`, `affine3.py`: affine-transform experiments
- `morph.py`, `keypointmorph.py`: alternative morphing experiments
- `collage.py`: GIF collage generation helper
- `perf.py`: unrelated Dash-based system monitor experiment currently kept in the repo

## Requirements

The project does not ship with a lockfile or environment manager, so the dependencies below are inferred from repository imports:

- `opencv-python`
- `numpy`
- `matplotlib`
- `imageio`
- `Pillow`
- `psutil`
- `dash`
- `dash-cytoscape`

Install them with:

```bash
python -m pip install -r requirements.txt
```

## How To Run

Run the main app from the project root:

```bash
python image_morpher.py --base_image before.jpg --surrogate_image after.jpg --output_folder morph_output
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
- There are no automated tests in the repository.
- There is no packaged installer, CLI release flow, or reproducible environment file beyond `requirements.txt`.
- `perf.py` appears to be unrelated to the image morphing workflow and may be a side experiment.

## Repo Notes

- Generated media is intentionally excluded from version control.
- Sample source images remain in the repository.
- This repo was prepared for public publication by adding documentation, dependency listing, and basic guard-rail fixes in the Python scripts.


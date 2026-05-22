from __future__ import annotations

import argparse
from pathlib import Path

from .config import MorphConfig, ResizeConfig


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return parsed


def build_morph_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Image Morphing Script")
    parser.add_argument(
        "--base_image",
        type=Path,
        required=True,
        help="Path to the base image",
    )
    parser.add_argument(
        "--surrogate_image",
        type=Path,
        required=True,
        help="Path to the surrogate image",
    )
    parser.add_argument(
        "--num_frames",
        type=_positive_int,
        default=20,
        help="Number of frames for the morphing sequence",
    )
    parser.add_argument(
        "--output_folder",
        type=Path,
        default=Path("output"),
        help="Folder to save output files",
    )
    return parser


def build_resize_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Image Resizer and Cropper")
    parser.add_argument(
        "--base_image",
        type=Path,
        required=True,
        help="Path to the base image",
    )
    parser.add_argument(
        "--overlay_image",
        type=Path,
        required=True,
        help="Path to the overlay image",
    )
    parser.add_argument(
        "--output_folder",
        type=Path,
        default=Path("output"),
        help="Folder to save output files",
    )
    return parser


def run_morph_app() -> None:
    parser = build_morph_parser()
    args = parser.parse_args()
    from .ui import MorphApplication

    try:
        app = MorphApplication(
            MorphConfig(
                base_image=args.base_image,
                surrogate_image=args.surrogate_image,
                num_frames=args.num_frames,
                output_folder=args.output_folder,
            )
        )
    except ValueError as error:
        parser.error(str(error))
    app.run()


def run_resize_app() -> None:
    parser = build_resize_parser()
    args = parser.parse_args()
    from .overlay_ui import OverlayAdjuster

    try:
        app = OverlayAdjuster(
            ResizeConfig(
                base_image=args.base_image,
                overlay_image=args.overlay_image,
                output_folder=args.output_folder,
            )
        )
    except ValueError as error:
        parser.error(str(error))
    app.run()

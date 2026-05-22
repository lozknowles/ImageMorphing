from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

import numpy as np

from .config import MorphConfig
from .exporters import (
    ExportResult,
    ensure_output_folder,
    export_gif,
    export_mp4,
    save_aligned_image,
    save_frames,
)
from .image_ops import build_aligned_workspace, blend_frame, prepare_loaded_images


@dataclass(frozen=True)
class MorphRunResult:
    export_result: ExportResult


def run_morph(
    config: MorphConfig,
    base_points: Sequence[Tuple[float, float]],
    surrogate_points: Sequence[Tuple[float, float]],
) -> MorphRunResult:
    if len(base_points) != len(surrogate_points):
        raise ValueError("The number of points in both images must be the same.")
    if len(base_points) < 3:
        raise ValueError("At least three pairs of points are required for affine transformation.")

    loaded = prepare_loaded_images(config.base_image, config.surrogate_image)
    workspace = build_aligned_workspace(
        loaded.base_bgr,
        loaded.surrogate_bgr,
        np.float32(base_points),
        np.float32(surrogate_points),
    )

    ensure_output_folder(config.output_folder)
    frames = [
        blend_frame(workspace, frame_index / config.num_frames)
        for frame_index in range(config.num_frames + 1)
    ]
    frame_paths = save_frames(frames, config.output_folder, config.base_filename)
    aligned_image_path = save_aligned_image(
        workspace.aligned_cropped,
        config.output_folder,
        config.base_filename,
    )
    gif_path = export_gif(
        frame_paths,
        config.output_folder,
        config.base_filename,
        config.frame_duration_seconds,
    )
    mp4_path, mp4_message = export_mp4(
        config.output_folder,
        config.base_filename,
        config.ffmpeg_binary,
        config.frame_rate,
    )

    return MorphRunResult(
        export_result=ExportResult(
            frame_paths=frame_paths,
            aligned_image_path=aligned_image_path,
            gif_path=gif_path,
            mp4_path=mp4_path,
            mp4_message=mp4_message,
        )
    )

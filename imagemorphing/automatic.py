from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
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
from .image_ops import prepare_loaded_images


@dataclass(frozen=True)
class AutoMorphResult:
    export_result: ExportResult
    match_visualization_path: Path
    match_count: int


def run_auto_morph(
    config: MorphConfig,
    *,
    max_features: int = 5000,
    preview_matches: int = 50,
) -> AutoMorphResult:
    if max_features <= 0:
        raise ValueError("max_features must be greater than 0.")
    if preview_matches <= 0:
        raise ValueError("preview_matches must be greater than 0.")

    loaded = prepare_loaded_images(config.base_image, config.surrogate_image)

    base_gray = cv2.cvtColor(loaded.base_bgr, cv2.COLOR_BGR2GRAY)
    surrogate_gray = cv2.cvtColor(loaded.surrogate_bgr, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create(max_features)
    base_keypoints, base_descriptors = orb.detectAndCompute(base_gray, None)
    surrogate_keypoints, surrogate_descriptors = orb.detectAndCompute(
        surrogate_gray,
        None,
    )

    if base_descriptors is None or surrogate_descriptors is None:
        raise ValueError("Could not detect enough features for automatic morphing.")

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(base_descriptors, surrogate_descriptors)
    if len(matches) < 4:
        raise ValueError("Could not find enough feature matches for homography.")

    matches = sorted(matches, key=lambda match: match.distance)
    matched_base_points = np.float32([base_keypoints[match.queryIdx].pt for match in matches])
    matched_surrogate_points = np.float32(
        [surrogate_keypoints[match.trainIdx].pt for match in matches]
    )

    homography, _ = cv2.findHomography(
        matched_surrogate_points,
        matched_base_points,
        cv2.RANSAC,
        5.0,
    )
    if homography is None:
        raise ValueError("Could not compute homography from automatic feature matches.")

    ensure_output_folder(config.output_folder)

    preview_match_count = min(preview_matches, len(matches))
    match_visualization = cv2.drawMatches(
        loaded.base_bgr,
        base_keypoints,
        loaded.surrogate_bgr,
        surrogate_keypoints,
        matches[:preview_match_count],
        None,
        flags=2,
    )
    match_visualization_path = config.output_folder / f"matches_{config.base_filename}.jpg"
    cv2.imwrite(str(match_visualization_path), match_visualization)

    height, width = loaded.base_bgr.shape[:2]
    aligned_image = cv2.warpPerspective(
        loaded.surrogate_bgr,
        homography,
        (width, height),
    )

    frames = [
        cv2.addWeighted(
            loaded.base_bgr,
            1.0 - (frame_index / config.num_frames),
            aligned_image,
            frame_index / config.num_frames,
            0,
        )
        for frame_index in range(config.num_frames + 1)
    ]
    frame_paths = save_frames(frames, config.output_folder, config.base_filename)
    aligned_image_path = save_aligned_image(
        aligned_image,
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

    return AutoMorphResult(
        export_result=ExportResult(
            frame_paths=frame_paths,
            aligned_image_path=aligned_image_path,
            gif_path=gif_path,
            mp4_path=mp4_path,
            mp4_message=mp4_message,
        ),
        match_visualization_path=match_visualization_path,
        match_count=len(matches),
    )

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Iterable, List, Optional

import cv2
import imageio


@dataclass(frozen=True)
class ExportResult:
    frame_paths: List[Path]
    aligned_image_path: Path
    gif_path: Path
    mp4_path: Optional[Path]
    mp4_message: str


def ensure_output_folder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_frames(
    frames: Iterable,
    output_folder: Path,
    base_filename: str,
) -> List[Path]:
    saved_paths: List[Path] = []
    for index, frame in enumerate(frames):
        frame_path = output_folder / f"morphed_{base_filename}_{index:02d}.jpg"
        cv2.imwrite(str(frame_path), frame)
        saved_paths.append(frame_path)
    return saved_paths


def save_aligned_image(image, output_folder: Path, base_filename: str) -> Path:
    aligned_path = output_folder / f"aligned_image_{base_filename}.jpg"
    cv2.imwrite(str(aligned_path), image)
    return aligned_path


def export_gif(
    frame_paths: List[Path],
    output_folder: Path,
    base_filename: str,
    duration_seconds: float,
) -> Path:
    gif_path = output_folder / f"morph_{base_filename}.gif"
    with imageio.get_writer(gif_path, mode="I", duration=duration_seconds) as writer:
        for frame_path in frame_paths:
            writer.append_data(imageio.imread(frame_path))
    return gif_path


def export_mp4(
    output_folder: Path,
    base_filename: str,
    ffmpeg_binary: str,
    frame_rate: int,
) -> tuple[Optional[Path], str]:
    mp4_path = output_folder / f"morph_{base_filename}.mp4"
    try:
        subprocess.run(
            [
                ffmpeg_binary,
                "-y",
                "-framerate",
                str(frame_rate),
                "-i",
                str(output_folder / f"morphed_{base_filename}_%02d.jpg"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(mp4_path),
            ],
            check=True,
        )
        return mp4_path, f"MP4 video saved as {mp4_path}"
    except FileNotFoundError:
        return (
            None,
            "ffmpeg was not found. GIF output was created, but MP4 export was skipped.",
        )
    except subprocess.CalledProcessError:
        return (
            None,
            (
                "ffmpeg failed to create MP4 video. "
                "Please ensure ffmpeg is installed and in your PATH."
            ),
        )

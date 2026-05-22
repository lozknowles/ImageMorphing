from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MorphConfig:
    base_image: Path
    surrogate_image: Path
    output_folder: Path = Path("output")
    num_frames: int = 20
    frame_duration_seconds: float = 0.1
    frame_rate: int = 10
    ffmpeg_binary: str = "ffmpeg"

    def __post_init__(self) -> None:
        if self.num_frames <= 0:
            raise ValueError("num_frames must be greater than 0")
        if self.frame_duration_seconds <= 0:
            raise ValueError("frame_duration_seconds must be greater than 0")
        if self.frame_rate <= 0:
            raise ValueError("frame_rate must be greater than 0")

    @property
    def base_filename(self) -> str:
        return self.base_image.stem


@dataclass(frozen=True)
class ResizeConfig:
    base_image: Path
    overlay_image: Path
    output_folder: Path = Path("output")
    output_filename: str = "adjusted_overlay.png"

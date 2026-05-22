from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(frozen=True)
class LoadedImages:
    base_bgr: np.ndarray
    surrogate_bgr: np.ndarray
    base_rgb: np.ndarray
    surrogate_rgb: np.ndarray


@dataclass(frozen=True)
class AlignedWorkspace:
    base_cropped: np.ndarray
    aligned_cropped: np.ndarray
    mask_cropped_3ch: np.ndarray


def load_image_or_raise(path: Path) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"{path} not found or could not be opened.")
    return image


def resize_pair_to_smallest(
    base_image: np.ndarray,
    surrogate_image: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    base_height, base_width = base_image.shape[:2]
    surrogate_height, surrogate_width = surrogate_image.shape[:2]

    if (base_height, base_width) == (surrogate_height, surrogate_width):
        return base_image, surrogate_image

    width = min(base_width, surrogate_width)
    height = min(base_height, surrogate_height)
    return (
        cv2.resize(base_image, (width, height)),
        cv2.resize(surrogate_image, (width, height)),
    )


def prepare_loaded_images(base_path: Path, surrogate_path: Path) -> LoadedImages:
    base_bgr = load_image_or_raise(base_path)
    surrogate_bgr = load_image_or_raise(surrogate_path)
    base_bgr, surrogate_bgr = resize_pair_to_smallest(base_bgr, surrogate_bgr)

    return LoadedImages(
        base_bgr=base_bgr,
        surrogate_bgr=surrogate_bgr,
        base_rgb=cv2.cvtColor(base_bgr, cv2.COLOR_BGR2RGB),
        surrogate_rgb=cv2.cvtColor(surrogate_bgr, cv2.COLOR_BGR2RGB),
    )


def apply_sepia(input_image: np.ndarray, intensity: float) -> np.ndarray:
    intensity = float(np.clip(intensity, 0, 1))
    image_float = input_image.astype(float)
    sepia_filter = np.array(
        [
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189],
        ]
    )
    sepia_image = cv2.transform(image_float, sepia_filter)
    sepia_image = np.clip(sepia_image, 0, 255)
    output = cv2.addWeighted(image_float, 1 - intensity, sepia_image, intensity, 0)
    return np.clip(output, 0, 255).astype(np.uint8)


def build_aligned_workspace(
    base_image: np.ndarray,
    surrogate_image: np.ndarray,
    base_points: np.ndarray,
    surrogate_points: np.ndarray,
) -> AlignedWorkspace:
    affine_matrix, _ = cv2.estimateAffine2D(surrogate_points, base_points)
    if affine_matrix is None:
        raise ValueError("Could not compute affine transformation.")

    height, width = base_image.shape[:2]
    aligned_image = cv2.warpAffine(surrogate_image, affine_matrix, (width, height))

    aligned_gray = cv2.cvtColor(aligned_image, cv2.COLOR_BGR2GRAY)
    _, mask_bin = cv2.threshold(aligned_gray, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("No valid area found in the aligned image.")

    largest_contour = max(contours, key=cv2.contourArea)
    x, y, width, height = cv2.boundingRect(largest_contour)

    mask_cropped = mask_bin[y : y + height, x : x + width]
    mask_cropped_3ch = cv2.merge([mask_cropped, mask_cropped, mask_cropped])

    return AlignedWorkspace(
        base_cropped=base_image[y : y + height, x : x + width],
        aligned_cropped=aligned_image[y : y + height, x : x + width],
        mask_cropped_3ch=mask_cropped_3ch,
    )


def blend_frame(workspace: AlignedWorkspace, alpha: float) -> np.ndarray:
    beta = 1.0 - alpha
    morphed_foreground = cv2.addWeighted(
        workspace.base_cropped,
        beta,
        workspace.aligned_cropped,
        alpha,
        0,
    )
    adjusted_background = apply_sepia(workspace.base_cropped, alpha)
    return np.where(
        workspace.mask_cropped_3ch == 255,
        morphed_foreground,
        adjusted_background,
    )

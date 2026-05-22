from __future__ import annotations

from dataclasses import dataclass

import cv2
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button

from .config import ResizeConfig
from .image_ops import load_image_or_raise


@dataclass
class OverlayAdjuster:
    config: ResizeConfig

    def __post_init__(self) -> None:
        base_bgr = load_image_or_raise(self.config.base_image)
        overlay_bgr = load_image_or_raise(self.config.overlay_image)
        self.base_image = cv2.cvtColor(base_bgr, cv2.COLOR_BGR2RGB)
        self.overlay_image = cv2.cvtColor(overlay_bgr, cv2.COLOR_BGR2RGB)
        self.overlay_position = [0, 0]
        self.overlay_scale = 1.0
        self.is_dragging = False
        self.last_x = 0.0
        self.last_y = 0.0
        self.figure, self.axis = plt.subplots(figsize=(10, 8))

    def run(self) -> None:
        self._setup_plot()
        crop_axis = plt.axes([0.7, 0.05, 0.2, 0.075])
        Button(crop_axis, "Crop and Save").on_clicked(self.crop_and_save)
        plt.show()

    def _setup_plot(self) -> None:
        self.axis.imshow(self.base_image)
        self.axis.imshow(self.overlay_image, alpha=0.5)
        self.axis.set_title("Drag to move, Scroll to resize")
        self.figure.canvas.mpl_connect("button_press_event", self.on_press)
        self.figure.canvas.mpl_connect("button_release_event", self.on_release)
        self.figure.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.figure.canvas.mpl_connect("scroll_event", self.on_scroll)

    def _resized_overlay(self) -> np.ndarray:
        return cv2.resize(
            self.overlay_image,
            None,
            fx=self.overlay_scale,
            fy=self.overlay_scale,
        )

    def update_overlay(self) -> None:
        resized_overlay = self._resized_overlay()
        overlay_height, overlay_width = resized_overlay.shape[:2]
        offset_y, offset_x = self.overlay_position

        canvas = np.zeros(
            (
                max(self.base_image.shape[0], overlay_height),
                max(self.base_image.shape[1], overlay_width),
                3,
            ),
            dtype=np.uint8,
        )
        canvas[: self.base_image.shape[0], : self.base_image.shape[1]] = self.base_image

        y_start = max(0, offset_y)
        y_end = min(canvas.shape[0], offset_y + overlay_height)
        x_start = max(0, offset_x)
        x_end = min(canvas.shape[1], offset_x + overlay_width)

        overlay_y_start = max(0, -offset_y)
        overlay_x_start = max(0, -offset_x)

        canvas[y_start:y_end, x_start:x_end] = resized_overlay[
            overlay_y_start : overlay_y_start + (y_end - y_start),
            overlay_x_start : overlay_x_start + (x_end - x_start),
        ]

        self.axis.clear()
        self.axis.imshow(self.base_image)
        self.axis.imshow(canvas, alpha=0.5)
        self.axis.set_title("Drag to move, Scroll to resize")
        self.figure.canvas.draw_idle()

    def on_press(self, event) -> None:
        if event.inaxes != self.axis or event.xdata is None or event.ydata is None:
            return
        self.is_dragging = True
        self.last_x = event.xdata
        self.last_y = event.ydata

    def on_release(self, _event) -> None:
        self.is_dragging = False

    def on_motion(self, event) -> None:
        if (
            not self.is_dragging
            or event.inaxes != self.axis
            or event.xdata is None
            or event.ydata is None
        ):
            return
        self.overlay_position[0] += int(event.ydata - self.last_y)
        self.overlay_position[1] += int(event.xdata - self.last_x)
        self.last_x = event.xdata
        self.last_y = event.ydata
        self.update_overlay()

    def on_scroll(self, event) -> None:
        if event.inaxes != self.axis:
            return
        if event.button == "up":
            self.overlay_scale *= 1.1
        elif event.button == "down":
            self.overlay_scale /= 1.1
        self.update_overlay()

    def crop_and_save(self, _event) -> None:
        resized_overlay = self._resized_overlay()
        base_height, base_width = self.base_image.shape[:2]
        offset_y, offset_x = self.overlay_position

        y_start = max(0, -offset_y)
        y_end = min(resized_overlay.shape[0], base_height - offset_y)
        x_start = max(0, -offset_x)
        x_end = min(resized_overlay.shape[1], base_width - offset_x)

        if y_start >= y_end or x_start >= x_end:
            print("Error: Overlay is outside the base image. Move it back into view before saving.")
            return

        cropped = resized_overlay[y_start:y_end, x_start:x_end]
        pad_top = max(0, offset_y)
        pad_left = max(0, offset_x)
        pad_bottom = max(0, base_height - (pad_top + cropped.shape[0]))
        pad_right = max(0, base_width - (pad_left + cropped.shape[1]))

        cropped_padded = cv2.copyMakeBorder(
            cropped,
            pad_top,
            pad_bottom,
            pad_left,
            pad_right,
            cv2.BORDER_CONSTANT,
        )
        if cropped_padded.size == 0:
            print("Error: Adjusted overlay could not be saved because the crop area is empty.")
            return

        self.config.output_folder.mkdir(parents=True, exist_ok=True)
        output_path = self.config.output_folder / self.config.output_filename
        cv2.imwrite(
            str(output_path),
            cv2.cvtColor(cropped_padded, cv2.COLOR_RGB2BGR),
        )
        print(f"Adjusted overlay image saved as {output_path}")
        plt.close(self.figure)

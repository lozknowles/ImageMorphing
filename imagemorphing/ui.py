from __future__ import annotations

from dataclasses import dataclass

import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.widgets import Button

from .config import MorphConfig
from .image_ops import LoadedImages, prepare_loaded_images
from .pipeline import run_morph
from .point_selection import PointSelection


@dataclass
class MorphApplication:
    config: MorphConfig

    def __post_init__(self) -> None:
        self.loaded_images: LoadedImages = prepare_loaded_images(
            self.config.base_image,
            self.config.surrogate_image,
        )
        self.selection = PointSelection()
        self.figure = None
        self.base_axis: Axes | None = None
        self.surrogate_axis: Axes | None = None

    def run(self) -> None:
        self.figure, (self.base_axis, self.surrogate_axis) = plt.subplots(
            1,
            2,
            figsize=(10, 5),
        )
        plt.subplots_adjust(bottom=0.2)
        self._render_images()

        self.figure.canvas.mpl_connect("button_press_event", self._handle_click)

        process_axis = plt.axes([0.35, 0.05, 0.1, 0.075])
        clear_axis = plt.axes([0.5, 0.05, 0.1, 0.075])
        Button(process_axis, "Process").on_clicked(self._process_images)
        Button(clear_axis, "Clear Points").on_clicked(self._clear_points)

        plt.show()

    def _render_images(self) -> None:
        assert self.base_axis is not None and self.surrogate_axis is not None
        self.base_axis.clear()
        self.surrogate_axis.clear()
        self.base_axis.imshow(self.loaded_images.base_rgb)
        self.base_axis.set_title("Base Image")
        self.base_axis.axis("off")

        self.surrogate_axis.imshow(self.loaded_images.surrogate_rgb)
        self.surrogate_axis.set_title("Surrogate Image")
        self.surrogate_axis.axis("off")

    def _handle_click(self, event) -> None:
        if self.base_axis is None or self.surrogate_axis is None or self.figure is None:
            return
        if event.xdata is None or event.ydata is None:
            print("Click inside the image area.")
            return

        side = None
        axis = None
        if event.inaxes == self.base_axis:
            side = "base"
            axis = self.base_axis
        elif event.inaxes == self.surrogate_axis:
            side = "surrogate"
            axis = self.surrogate_axis
        else:
            print("Clicked outside of the images.")
            return

        try:
            point_number = self.selection.add_point(side, event.xdata, event.ydata)
        except ValueError as error:
            print(f"Error: {error}")
            return

        axis.plot(event.xdata, event.ydata, "ro")
        axis.text(
            event.xdata,
            event.ydata,
            f"{point_number}",
            color="yellow",
            fontsize=12,
        )
        self.figure.canvas.draw()
        print(f"Clicked on {side.title()} Image. Point number: {point_number}")

    def _process_images(self, _event) -> None:
        try:
            result = run_morph(
                self.config,
                self.selection.base_points,
                self.selection.surrogate_points,
            )
        except (ValueError, FileNotFoundError) as error:
            print(f"Error: {error}")
            return

        print("Affine transformation and morphing completed successfully!")
        print(f"Animated GIF saved as {result.export_result.gif_path}")
        print(result.export_result.mp4_message)

    def _clear_points(self, _event) -> None:
        if self.figure is None:
            return
        self.selection.reset()
        self._render_images()
        self.figure.canvas.draw()
        print("All points have been cleared.")

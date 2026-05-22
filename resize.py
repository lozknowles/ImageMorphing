#!/usr/bin/env python3
"""
Image Resizer and Cropper v2.0

This script overlays two input images and allows the user to select corresponding points
to resize the second image to match the dimensions of the base image.

Usage:
    python resize.py --base_image <path_to_base_image> --overlay_image <path_to_overlay_image> [options]

Required arguments:
    --base_image        Path to the base image file
    --overlay_image     Path to the overlay image file

Optional arguments:
    --output_folder     Folder to save output files (default: 'output')

After running the script:
1. A window will open showing the base image with the overlay image superimposed.
2. Click on corresponding points in both images (at least 3 pairs).
3. Click the "Resize" button to start the resizing process.
4. Use the "Clear Points" button to reset if you make a mistake.

Requirements:
- Python 3.x
- OpenCV (cv2)
- NumPy
- Matplotlib

Author: [Your Name]
Date: [Current Date]
Version: 2.0
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import argparse
import os

def parse_arguments():
    parser = argparse.ArgumentParser(description='Image Resizer and Cropper v2.0')
    parser.add_argument('--base_image', type=str, required=True, help='Filename of the base image')
    parser.add_argument('--overlay_image', type=str, required=True, help='Filename of the overlay image')
    parser.add_argument('--output_folder', type=str, default='output', help='Folder to save output files')
    return parser.parse_args()

class ImageAdjuster:
    def __init__(self, base_image, overlay_image):
        self.base_image = base_image
        self.overlay_image = overlay_image
        self.overlay_position = [0, 0]
        self.overlay_scale = 1.0
        self.is_dragging = False
        self.last_x = 0
        self.last_y = 0
        
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.setup_plot()

    def setup_plot(self):
        self.ax.imshow(self.base_image)
        self.overlay_plot = self.ax.imshow(self.overlay_image, alpha=0.5)
        self.ax.set_title('Drag to move, Scroll to resize')
        
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)

    def update_overlay(self):
        resized_overlay = cv2.resize(self.overlay_image, None, fx=self.overlay_scale, fy=self.overlay_scale)
        h, w = resized_overlay.shape[:2]
        y, x = self.overlay_position
        
        canvas = np.zeros((max(self.base_image.shape[0], h), max(self.base_image.shape[1], w), 3), dtype=np.uint8)
        canvas[:self.base_image.shape[0], :self.base_image.shape[1]] = self.base_image
        
        y_start = max(0, y)
        y_end = min(canvas.shape[0], y + h)
        x_start = max(0, x)
        x_end = min(canvas.shape[1], x + w)
        
        overlay_y_start = max(0, -y)
        overlay_x_start = max(0, -x)
        
        canvas[y_start:y_end, x_start:x_end] = resized_overlay[overlay_y_start:overlay_y_start+(y_end-y_start), 
                                                               overlay_x_start:overlay_x_start+(x_end-x_start)]
        
        self.ax.clear()
        self.ax.imshow(self.base_image)
        self.overlay_plot = self.ax.imshow(canvas, alpha=0.5)
        self.ax.set_title('Drag to move, Scroll to resize')
        self.fig.canvas.draw_idle()

    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        self.is_dragging = True
        self.last_x = event.xdata
        self.last_y = event.ydata

    def on_release(self, event):
        self.is_dragging = False

    def on_motion(self, event):
        if not self.is_dragging or event.inaxes != self.ax:
            return
        dx = event.xdata - self.last_x
        dy = event.ydata - self.last_y
        self.overlay_position[0] += int(dy)
        self.overlay_position[1] += int(dx)
        self.last_x = event.xdata
        self.last_y = event.ydata
        self.update_overlay()

    def on_scroll(self, event):
        if event.inaxes != self.ax:
            return
        if event.button == 'up':
            self.overlay_scale *= 1.1
        elif event.button == 'down':
            self.overlay_scale /= 1.1
        self.update_overlay()

    def crop_and_save(self, event):
        resized_overlay = cv2.resize(self.overlay_image, None, fx=self.overlay_scale, fy=self.overlay_scale)
        h, w = self.base_image.shape[:2]
        y, x = self.overlay_position
        
        y_start = max(0, -y)
        y_end = min(resized_overlay.shape[0], h - y)
        x_start = max(0, -x)
        x_end = min(resized_overlay.shape[1], w - x)
        
        if y_start >= y_end or x_start >= x_end:
            print("Error: Overlay is outside the base image. Move it back into view before saving.")
            return

        cropped = resized_overlay[y_start:y_end, x_start:x_end]
        
        output_h, output_w = h, w
        pad_top = max(0, y)
        pad_left = max(0, x)
        pad_bottom = max(0, output_h - (pad_top + cropped.shape[0]))
        pad_right = max(0, output_w - (pad_left + cropped.shape[1]))
        
        cropped_padded = cv2.copyMakeBorder(cropped, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT)

        if cropped_padded.size == 0:
            print("Error: Adjusted overlay could not be saved because the crop area is empty.")
            return

        os.makedirs(args.output_folder, exist_ok=True)
        output_filename = f"{args.output_folder}/adjusted_overlay.png"
        cv2.imwrite(output_filename, cv2.cvtColor(cropped_padded, cv2.COLOR_RGB2BGR))
        print(f"Adjusted overlay image saved as {output_filename}")
        plt.close(self.fig)

if __name__ == '__main__':
    args = parse_arguments()
    
    base_image = cv2.imread(args.base_image)
    overlay_image = cv2.imread(args.overlay_image)
    
    if base_image is None or overlay_image is None:
        print("Error: Images not found or could not be opened.")
        exit(1)
    
    base_image_rgb = cv2.cvtColor(base_image, cv2.COLOR_BGR2RGB)
    overlay_image_rgb = cv2.cvtColor(overlay_image, cv2.COLOR_BGR2RGB)
    
    adjuster = ImageAdjuster(base_image_rgb, overlay_image_rgb)
    
    ax_crop = plt.axes([0.7, 0.05, 0.2, 0.075])
    btn_crop = Button(ax_crop, 'Crop and Save')
    btn_crop.on_clicked(adjuster.crop_and_save)
    
    plt.show()

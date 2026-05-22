import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import matplotlib
import sys
import os
import argparse
import subprocess

# Ensure Matplotlib uses the TkAgg backend
matplotlib.use('TkAgg')

# Global variables to store points
points_base = []
points_surrogate = []
point_number = 1
last_clicked_axis = None  # Keep track of the last clicked axis

def parse_arguments():
    parser = argparse.ArgumentParser(description='Image Morphing Script')
    parser.add_argument('--base_image', type=str, required=True, help='Filename of the base image')
    parser.add_argument('--surrogate_image', type=str, required=True, help='Filename of the surrogate image')
    parser.add_argument('--num_frames', type=int, default=20, help='Number of frames for the morphing sequence')
    parser.add_argument('--output_folder', type=str, default='output', help='Folder to save output files')
    args = parser.parse_args()
    return args

def apply_sepia(input_image, intensity):
    # Ensure intensity is within [0, 1]
    intensity = np.clip(intensity, 0, 1)

    # Convert input_image to float
    img = input_image.astype(float)

    # Create the sepia filter matrix
    sepia_filter = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])

    # Apply the sepia filter
    sepia_img = cv2.transform(img, sepia_filter)

    # Clip values to [0, 255]
    sepia_img = np.clip(sepia_img, 0, 255)

    # Blend the original and sepia images
    output = cv2.addWeighted(img, 1 - intensity, sepia_img, intensity, 0)

    # Clip values to [0, 255] and convert to uint8
    output = np.clip(output, 0, 255).astype(np.uint8)

    return output

def onclick(event):
    global point_number, last_clicked_axis
    if event.inaxes == ax1:
        if last_clicked_axis == ax1:
            print("Please click on the other image next.")
            return
        x, y = event.xdata, event.ydata
        points_base.append([x, y])
        # Plot the point and number
        ax1.plot(x, y, 'ro')
        ax1.text(x, y, f'{point_number}', color='yellow', fontsize=12)
        fig.canvas.draw()
        last_clicked_axis = ax1
        print(f"Clicked on Base Image. Point number: {point_number}")
    elif event.inaxes == ax2:
        if last_clicked_axis == ax2:
            print("Please click on the other image next.")
            return
        x, y = event.xdata, event.ydata
        points_surrogate.append([x, y])
        # Plot the point and number
        ax2.plot(x, y, 'ro')
        ax2.text(x, y, f'{point_number}', color='yellow', fontsize=12)
        fig.canvas.draw()
        last_clicked_axis = ax2
        print(f"Clicked on Surrogate Image. Point number: {point_number}")
        point_number += 1  # Increment after a pair of clicks
    else:
        print("Clicked outside of the images.")

def process_images(event):
    if len(points_base) != len(points_surrogate):
        print("Error: The number of points in both images must be the same.")
        return
    if len(points_base) < 3:
        print("Error: At least three pairs of points are required for affine transformation.")
        return

    # Convert points to numpy arrays
    pts_base = np.float32(points_base)
    pts_surrogate = np.float32(points_surrogate)

    # Compute affine transformation
    affine_matrix, inliers = cv2.estimateAffine2D(pts_surrogate, pts_base)

    # Check if the affine transformation was successful
    if affine_matrix is None:
        print("Error: Could not compute affine transformation.")
        return

    # Warp surrogate image
    height, width = base_image.shape[:2]
    aligned_image = cv2.warpAffine(surrogate_image, affine_matrix, (width, height))

    # Create the mask for the warped image
    aligned_gray = cv2.cvtColor(aligned_image, cv2.COLOR_BGR2GRAY)
    _, mask_bin = cv2.threshold(aligned_gray, 1, 255, cv2.THRESH_BINARY)

    # Find contours in the binary mask
    contours, _ = cv2.findContours(mask_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the bounding rectangle around the largest contour
    if contours:
        # Assume the largest contour corresponds to the aligned image area
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
    else:
        print("Error: No valid area found in the aligned image.")
        return

    # Crop the mask, base image, and aligned image to the bounding box
    mask_cropped = mask_bin[y:y+h, x:x+w]
    mask_cropped_3ch = cv2.merge([mask_cropped, mask_cropped, mask_cropped])  # Convert to 3-channel

    base_image_cropped = base_image[y:y+h, x:x+w]
    aligned_image_cropped = aligned_image[y:y+h, x:x+w]

    # Ensure output folder exists
    os.makedirs(args.output_folder, exist_ok=True)

    # Get base image filename without extension for suffix
    base_filename = os.path.splitext(os.path.basename(args.base_image))[0]

    # Morph images with background blending and color adjustment
    for i in range(args.num_frames + 1):
        alpha = i / args.num_frames
        beta = 1.0 - alpha

        # Blend the aligned image and base image (both cropped)
        morphed_foreground = cv2.addWeighted(base_image_cropped, beta, aligned_image_cropped, alpha, 0)

        # Apply sepia filter to the base image (cropped) with intensity alpha
        adjusted_background = apply_sepia(base_image_cropped, alpha)

        # Combine the morphed foreground and adjusted background using the cropped mask
        morphed_image = np.where(mask_cropped_3ch == 255, morphed_foreground, adjusted_background)

        # Save the morphed image
        output_filename = f"{args.output_folder}/morphed_{base_filename}_{i:02d}.jpg"
        cv2.imwrite(output_filename, morphed_image)

    # Save the final aligned image (cropped)
    aligned_output_filename = f"{args.output_folder}/aligned_image_{base_filename}.jpg"
    cv2.imwrite(aligned_output_filename, aligned_image_cropped)

    print("Affine transformation and morphing completed successfully!")

    # Create animated GIF and MP4
    create_animations(base_filename)

def create_animations(base_filename):
    import imageio

    # Collect all morphed image filenames
    morphed_images = []
    for i in range(args.num_frames + 1):
        filename = f"{args.output_folder}/morphed_{base_filename}_{i:02d}.jpg"
        morphed_images.append(filename)

    # Create animated GIF
    gif_filename = f"{args.output_folder}/morph_{base_filename}.gif"
    with imageio.get_writer(gif_filename, mode='I', duration=0.1) as writer:
        for filename in morphed_images:
            image = imageio.imread(filename)
            writer.append_data(image)
    print(f"Animated GIF saved as {gif_filename}")

    # Create MP4 video using ffmpeg
    mp4_filename = f"{args.output_folder}/morph_{base_filename}.mp4"
    try:
        subprocess.run([
            'ffmpeg', '-y', '-framerate', '10', '-i',
            f"{args.output_folder}/morphed_{base_filename}_%02d.jpg",
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', mp4_filename
        ], check=True)
        print(f"MP4 video saved as {mp4_filename}")
    except subprocess.CalledProcessError:
        print("Error: ffmpeg failed to create MP4 video. Please ensure ffmpeg is installed and in your PATH.")

def clear_points(event):
    global points_base, points_surrogate, point_number, last_clicked_axis
    points_base = []
    points_surrogate = []
    point_number = 1
    last_clicked_axis = None
    ax1.clear()
    ax2.clear()
    ax1.imshow(base_image_rgb)
    ax1.set_title('Base Image')
    ax1.axis('off')
    ax2.imshow(surrogate_image_rgb)
    ax2.set_title('Surrogate Image')
    ax2.axis('off')
    fig.canvas.draw()
    print("All points have been cleared.")

if __name__ == '__main__':
    # Parse command-line arguments
    args = parse_arguments()

    # Load images
    base_image = cv2.imread(args.base_image)
    surrogate_image = cv2.imread(args.surrogate_image)

    # Check if images were loaded successfully
    if base_image is None:
        print(f"Error: {args.base_image} not found or could not be opened.")
        sys.exit(1)
    if surrogate_image is None:
        print(f"Error: {args.surrogate_image} not found or could not be opened.")
        sys.exit(1)

    # Resize images to the same size if necessary
    height1, width1 = base_image.shape[:2]
    height2, width2 = surrogate_image.shape[:2]

    if (height1, width1) != (height2, width2):
        width = min(width1, width2)
        height = min(height1, height2)
        base_image = cv2.resize(base_image, (width, height))
        surrogate_image = cv2.resize(surrogate_image, (width, height))

    # Convert images from BGR to RGB for matplotlib
    base_image_rgb = cv2.cvtColor(base_image, cv2.COLOR_BGR2RGB)
    surrogate_image_rgb = cv2.cvtColor(surrogate_image, cv2.COLOR_BGR2RGB)

    # Create matplotlib figure and axes
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    plt.subplots_adjust(bottom=0.2)  # Make room for buttons

    # Display the images
    ax1.imshow(base_image_rgb)
    ax1.set_title('Base Image')
    ax1.axis('off')

    ax2.imshow(surrogate_image_rgb)
    ax2.set_title('Surrogate Image')
    ax2.axis('off')

    # Connect the onclick event
    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    # Add a Process button
    ax_process = plt.axes([0.35, 0.05, 0.1, 0.075])
    btn_process = Button(ax_process, 'Process')

    # Add a Clear Points button
    ax_clear = plt.axes([0.5, 0.05, 0.1, 0.075])
    btn_clear = Button(ax_clear, 'Clear Points')

    btn_process.on_clicked(process_images)
    btn_clear.on_clicked(clear_points)

    plt.show()

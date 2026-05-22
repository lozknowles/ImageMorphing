import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import matplotlib

# Ensure Matplotlib uses the TkAgg backend
matplotlib.use('TkAgg')

# Global variables to store points
points_base = []
points_surrogate = []
point_number = 1
last_clicked_axis = None  # Keep track of the last clicked axis

# Load images
base_image = cv2.imread('1.jpg')
surrogate_image = cv2.imread('2.jpg')

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

# Function to handle mouse clicks
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

# Connect the onclick event
cid = fig.canvas.mpl_connect('button_press_event', onclick)

# Add a Process button
ax_process = plt.axes([0.45, 0.05, 0.1, 0.075])
btn_process = Button(ax_process, 'Process')

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

    # Save aligned image
    cv2.imwrite('aligned_image_affine.jpg', aligned_image)

    # Morph images
    num_frames = 20
    for i in range(num_frames + 1):
        alpha = i / num_frames
        beta = 1.0 - alpha
        morphed_image = cv2.addWeighted(base_image, beta, aligned_image, alpha, 0)
        cv2.imwrite(f'morphed_affine_{i:02d}.jpg', morphed_image)

    print("Affine transformation and morphing completed successfully!")


btn_process.on_clicked(process_images)

plt.show()


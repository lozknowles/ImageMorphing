import cv2
import numpy as np

# Load images
base_image = cv2.imread('hollands.jpeg')
surrogate_image = cv2.imread('surrogate_image.jpg')

# Convert to grayscale
base_gray = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
surrogate_gray = cv2.cvtColor(surrogate_image, cv2.COLOR_BGR2GRAY)

# Detect ORB keypoints and descriptors
orb = cv2.ORB_create(5000)
kp1, des1 = orb.detectAndCompute(base_gray, None)
kp2, des2 = orb.detectAndCompute(surrogate_gray, None)

# Match features
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(des1, des2)
matches = sorted(matches, key=lambda x: x.distance)
# Draw the first 50 matches
match_img = cv2.drawMatches(base_image, kp1, surrogate_image, kp2, matches[:50], None, flags=2)
cv2.imwrite('matches.jpg', match_img)

# Extract matched keypoints
points1 = np.float32([kp1[m.queryIdx].pt for m in matches])
points2 = np.float32([kp2[m.trainIdx].pt for m in matches])

# Compute homography
homography, mask = cv2.findHomography(points2, points1, cv2.RANSAC, 5.0)

# Warp surrogate image
height, width, channels = base_image.shape
aligned_image = cv2.warpPerspective(surrogate_image, homography, (width, height))

# Morph images
num_frames = 20
for i in range(num_frames + 1):
    alpha = i / num_frames
    beta = 1.0 - alpha
    morphed_image = cv2.addWeighted(base_image, beta, aligned_image, alpha, 0)
    cv2.imwrite(f'morphed_{i:02d}.jpg', morphed_image)

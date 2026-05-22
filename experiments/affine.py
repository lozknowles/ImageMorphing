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

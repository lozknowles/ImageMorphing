import os
import imageio
from PIL import Image, ImageDraw

# Constants for the final collage dimensions
COLLAGE_WIDTH = 1280
COLLAGE_HEIGHT = 720
GIF_DIR = '.'  # Directory where the script and GIFs are located
GIF_SIZE = 150  # Resized GIF dimensions (width and height)

def get_gif_files(directory):
    """Returns a list of GIF file paths from the specified directory."""
    return [f for f in os.listdir(directory) if f.endswith('.gif')]

def create_collage(gif_files, output_file='collage.gif'):
    """Creates a collage of animated GIFs and saves it."""
    # Calculate the number of rows and columns required
    gifs_per_row = COLLAGE_WIDTH // GIF_SIZE
    rows = (len(gif_files) + gifs_per_row - 1) // gifs_per_row

    # Create a blank image for the collage
    collage = Image.new('RGBA', (COLLAGE_WIDTH, COLLAGE_HEIGHT), (255, 255, 255, 255))
    all_gif_frames = []
    
    for gif_index, gif_file in enumerate(gif_files):
        gif_path = os.path.join(GIF_DIR, gif_file)
        gif_reader = imageio.get_reader(gif_path)
        gif_frames = [Image.fromarray(frame) for frame in gif_reader]

        # Resize the frames of the GIF to the specified GIF size
        resized_frames = [frame.resize((GIF_SIZE, GIF_SIZE), Image.Resampling.LANCZOS) for frame in gif_frames]

        # Calculate the position to paste the GIF
        x = (gif_index % gifs_per_row) * GIF_SIZE
        y = (gif_index // gifs_per_row) * GIF_SIZE

        # Paste each frame into the correct location on the collage
        for frame_index, frame in enumerate(resized_frames):
            if len(all_gif_frames) <= frame_index:
                # Create a new frame for the collage if needed
                all_gif_frames.append(collage.copy())
            all_gif_frames[frame_index].paste(frame, (x, y))

    # Save the collage as a looping GIF
    all_gif_frames[0].save(output_file, save_all=True, append_images=all_gif_frames[1:], loop=0, duration=100)

if __name__ == '__main__':
    gif_files = get_gif_files(GIF_DIR)
    if gif_files:
        create_collage(gif_files)
    else:
        print("No GIF files found in the directory.")

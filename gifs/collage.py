import os
from PIL import Image

# Constants
GIF_DIR = '.'  # Directory where the GIFs are located
OUTPUT_HTML = 'collage_hover_with_static.html'

def get_gif_files(directory):
    """Returns a list of GIF file paths from the specified directory."""
    return [f for f in os.listdir(directory) if f.endswith('.gif')]

def extract_first_frame(gif_file):
    """Extract the first frame of a GIF and save it as a PNG."""
    with Image.open(gif_file) as img:
        img.seek(0)  # Go to the first frame
        first_frame = img.convert('RGBA')  # Convert to proper format
        png_filename = gif_file.replace('.gif', '.png')
        first_frame.save(png_filename, 'PNG')
        return png_filename

def create_html(gif_files, output_file=OUTPUT_HTML):
    """Creates an HTML page displaying all GIFs that play on hover."""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GIF Collage</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            background-color: #f0f0f0;
        }
        .gif-container {
            margin: 5px;
        }
        img {
            display: block;
            max-width: 100%;
            height: auto;
        }
    </style>
</head>
<body>
'''

    # Loop through GIFs and add them to the HTML
    for gif in gif_files:
        static_image = extract_first_frame(gif)  # Generate static PNG from the first frame
        html_content += f'''
        <div class="gif-container">
            <img src="{static_image}" alt="{gif}" data-gif="{gif}" class="gif"/>
        </div>\n'''

    # Add JavaScript for hover effect
    html_content += '''
<script>
    document.querySelectorAll('.gif').forEach(img => {
        const gifSrc = img.getAttribute('data-gif');
        const staticSrc = img.getAttribute('src');
        img.addEventListener('mouseover', () => {
            img.setAttribute('src', gifSrc);  // Play the GIF on hover
        });
        img.addEventListener('mouseout', () => {
            img.setAttribute('src', staticSrc);  // Show static image when not hovered
        });
    });
</script>
</body>
</html>
'''

    # Write the HTML content to the output file
    with open(output_file, 'w') as f:
        f.write(html_content)

if __name__ == '__main__':
    gif_files = get_gif_files(GIF_DIR)
    if gif_files:
        create_html(gif_files)
        print(f"HTML file '{OUTPUT_HTML}' has been created with {len(gif_files)} GIFs.")
    else:
        print("No GIF files found in the directory.")

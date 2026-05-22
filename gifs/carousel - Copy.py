import os
from PIL import Image

# Constants
GIF_DIR = '.'  # Directory where the GIFs are located
OUTPUT_HTML = 'gif_carousel.html'

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
    """Creates an HTML page displaying GIFs in a carousel format."""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GIF Carousel</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f0f0f0;
            overflow: hidden;
        }
        .carousel {
            position: relative;
            width: 100vw;
            height: 80vh;
            display: flex;
            justify-content: center;
            align-items: center;
            perspective: 1000px;
        }
        .carousel-item {
            position: absolute;
            transition: all 0.5s ease;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .carousel-item img {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        .center {
            z-index: 5;
            width: 60vw;
            height: 60vh;
            opacity: 1;
        }
        .left, .right {
            z-index: 4;
            width: 30vw;
            height: 30vh;
            opacity: 0.8;
        }
        .left { transform: translateX(-80%) translateY(-5%) translateZ(-100px); }
        .right { transform: translateX(80%) translateY(-5%) translateZ(-100px); }
        .far-left, .far-right {
            z-index: 3;
            width: 20vw;
            height: 20vh;
            opacity: 0.6;
        }
        .far-left { transform: translateX(-140%) translateY(-10%) translateZ(-200px); }
        .far-right { transform: translateX(140%) translateY(-10%) translateZ(-200px); }
        .button {
            position: absolute;
            bottom: 20px;
            padding: 10px 20px;
            font-size: 18px;
            cursor: pointer;
            z-index: 10;
        }
        #prev { left: 20px; }
        #next { right: 20px; }
    </style>
</head>
<body>
    <div class="carousel">
'''

    # Add carousel items
    for i, gif in enumerate(gif_files):
        static_image = extract_first_frame(gif)
        html_content += f'''
        <div class="carousel-item" id="item-{i}">
            <img src="{static_image}" alt="{gif}" data-gif="{gif}" class="gif"/>
        </div>'''

    html_content += '''
    </div>
    <button class="button" id="prev">Previous</button>
    <button class="button" id="next">Next</button>

<script>
    const items = document.querySelectorAll('.carousel-item');
    const totalItems = items.length;
    let currentIndex = 0;

    function updateCarousel() {
        items.forEach((item, index) => {
            const offset = (index - currentIndex + totalItems) % totalItems;
            item.className = 'carousel-item';
            item.style.display = 'flex';
            if (offset === 0) {
                item.classList.add('center');
                playGif(item.querySelector('img'));
            } else if (offset === 1) {
                item.classList.add('right');
                stopGif(item.querySelector('img'));
            } else if (offset === totalItems - 1) {
                item.classList.add('left');
                stopGif(item.querySelector('img'));
            } else if (offset === 2) {
                item.classList.add('far-right');
                stopGif(item.querySelector('img'));
            } else if (offset === totalItems - 2) {
                item.classList.add('far-left');
                stopGif(item.querySelector('img'));
            } else {
                item.style.display = 'none';
            }
        });
    }

    function playGif(img) {
        img.src = img.getAttribute('data-gif');
    }

    function stopGif(img) {
        img.src = img.getAttribute('src').replace('.gif', '.png');
    }

    document.getElementById('next').addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % totalItems;
        updateCarousel();
    });

    document.getElementById('prev').addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + totalItems) % totalItems;
        updateCarousel();
    });

    updateCarousel();
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

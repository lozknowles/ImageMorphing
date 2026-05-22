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
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Collingham: Looking Back in Time</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
            min-height: 100vh;
            background-color: #f0f0f0;
            font-family: Arial, sans-serif;
        }
        .header {
            text-align: center;
            margin-bottom: 5px; /* Reduced from 10px to 5px */
        }
        .logo {
            max-width: 200px;
            margin-bottom: 10px;
            background-color: transparent; /* Ensure the background is transparent */
        }
        h1 {
            color: #333;
            margin: 0;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .carousel {
            position: relative;
            width: 100vw;
            height: 65vh;
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
            overflow: hidden;
        }
        .carousel-item img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
        }
        .center {
            z-index: 5;
            width: 50vw;
            height: 60vh;
        }
        .center img {
            object-fit: contain;
        }
        .left, .right {
            z-index: 4;
            width: 30vw;
            height: 40vh;
            opacity: 0.7;
        }
        .left { transform: translateX(-60%) translateY(0) translateZ(-100px); }
        .right { transform: translateX(60%) translateY(0) translateZ(-100px); }
        .far-left, .far-right {
            z-index: 3;
            width: 20vw;
            height: 30vh;
            opacity: 0.4;
        }
        .far-left { transform: translateX(-100%) translateY(0) translateZ(-200px); }
        .far-right { transform: translateX(100%) translateY(0) translateZ(-200px); }
        .button-container {
            position: absolute;
            bottom: 20px;
            left: 0;
            right: 0;
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        .button {
            width: 50px;
            height: 50px;
            cursor: pointer;
            z-index: 10;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            border: none;
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 25px;
        }
        #prev { background-image: url('prev_button.png'); }
        #start { background-image: url('play_button.png'); }
        #next { background-image: url('next_button.png'); }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
</head>
<body>
    <div class="header">
        <img src="logo.png" alt="Logo" class="logo">
        <h1>Collingham: Looking Back in Time</h1>
    </div>
    <div class="carousel">
'''

    # Add carousel items
    for i, gif in enumerate(gif_files):
        html_content += f'''
        <div class="carousel-item" id="item-{i}">
            <img src="{gif}" alt="GIF {i}" data-gif="{gif}" class="gif"/>
        </div>'''

    html_content += '''
    </div>
    <div class="button-container">
        <button class="button" id="prev"></button>
        <button class="button" id="start"></button>
        <button class="button" id="next"></button>
    </div>

<script>
    const items = document.querySelectorAll('.carousel-item');
    const totalItems = items.length;
    let currentIndex = 0;
    let isAutoRotating = false;
    let autoRotateTimeout;

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

    function rotateCarousel() {
        if (!isAutoRotating) return;

        currentIndex = (currentIndex + 1) % totalItems;
        updateCarousel();
        
        // Schedule next rotation after 5 seconds
        autoRotateTimeout = setTimeout(rotateCarousel, 5000);
    }

    function startAutoRotate() {
        if (!isAutoRotating) {
            isAutoRotating = true;
            document.getElementById('start').style.backgroundImage = "url('pause_button.png')";
            rotateCarousel();
        } else {
            isAutoRotating = false;
            document.getElementById('start').style.backgroundImage = "url('play_button.png')";
            clearTimeout(autoRotateTimeout);
        }
    }

    document.getElementById('next').addEventListener('click', () => {
        if (isAutoRotating) startAutoRotate();  // Stop auto-rotation
        currentIndex = (currentIndex + 1) % totalItems;
        updateCarousel();
    });

    document.getElementById('prev').addEventListener('click', () => {
        if (isAutoRotating) startAutoRotate();  // Stop auto-rotation
        currentIndex = (currentIndex - 1 + totalItems) % totalItems;
        updateCarousel();
    });

    document.getElementById('start').addEventListener('click', startAutoRotate);

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

from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import requests
from typing import List, Dict
from app.visualisations import vibe_calculator
import functools
import os

# Set up colors
BLACK = (50,60,73)	
ORANGE = "#ef8833"
SKYBLUE = (224, 237, 253)
BLUE = (102,185,239)
WHITE = (255, 255, 255)
GREEN = "#66dd68"

@functools.lru_cache
def get_font_from_url(font_url):
    response = requests.get(font_url)
    return response.content


def webfont(font_url):
    return io.BytesIO(get_font_from_url(font_url))

@functools.lru_cache
def load_all_fonts_from_web():
    emoji_font_url = 'https://github.com/google/fonts/blob/main/ofl/notoemoji/NotoEmoji%5Bwght%5D.ttf?raw=true'
    libre_url = 'https://github.com/google/fonts/blob/main/ofl/librebaskerville/LibreBaskerville-Bold.ttf?raw=true'
    roboto_black_url = 'https://github.com/openmaptiles/fonts/blob/master/roboto/Roboto-Black.ttf?raw=true'
    roboto_bold_url = 'https://github.com/openmaptiles/fonts/blob/master/roboto/Roboto-Bold.ttf?raw=true'

    font_dict = {
        'emoji_font': (emoji_font_url, 30),
        'font_highlights': (libre_url, 50),
        'font_numbers': (libre_url, 70),
        'font_numbers_medium': (libre_url, 40),
        'font_small': (roboto_bold_url, 40),
        'font_text': (roboto_bold_url, 30),
        'font_large': (roboto_black_url, 70),  
    }
    for key, (font_url, size) in font_dict.items():
        font_dict[key] = ImageFont.truetype(webfont(font_url), size)

    return font_dict


# Set up image size
width, height = 1080, 1920

def create_circle(draw, xy, radius, fill):
    draw.ellipse((xy[0]-radius, xy[1]-radius, xy[0]+radius, xy[1]+radius), fill=fill)

def add_rounded_corners(image, radius):
    # Create a mask with rounded corners
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, image.size[0], image.size[1]], radius=radius, fill=255)
    
    # Apply the mask to the image
    rounded_image = ImageOps.fit(image, image.size, centering=(0.5, 0.5))
    rounded_image.putalpha(mask)
    
    return rounded_image

def create_poster(username, movie_df, year, top3_movies):
    # Create a new image with a black background
    image = Image.new('RGB', (width, height), GREEN)
    draw = ImageDraw.Draw(image)

    # Draw purple background
    margin = 50
    draw.rectangle([margin, margin, width - margin, height - margin], fill=BLACK)
    draw.rectangle([margin, height//2, width - margin, height - margin], fill=WHITE)


    fonts = load_all_fonts_from_web()
    font_small = fonts['font_small']
    font_text = fonts['font_text']
    font_large = fonts['font_large']
    emoji_font = fonts['emoji_font']
    font_numbers = fonts['font_numbers']
    font_highlights = fonts['font_highlights']
    font_numbers_medium = fonts['font_numbers_medium']

    # Draw stats
    left_margin = 100
    top_margin = height // 2


    # Add title
    draw.text((width//2, 170), f"{year}", fill="#FFFFFF", font=font_numbers, anchor="mt")
    draw.text((width//2, 240), f"{username}'s Year in Film", fill=SKYBLUE, font=font_large, anchor="mt")

    stats = [
        ("Films Logged", str(movie_df.shape[0])),
        ("Films Reviewed", str(movie_df[~movie_df['description'].str.contains('Watched on')].shape[0])),
        ("New Releases", str(movie_df[movie_df['release_date'].dt.year == year].shape[0])),
        # ("TOP GENRE", movie_df['genres'].explode().value_counts().idxmax())
    ]

    poster_size = (250, 374)  # Increased size for better visibility
    for i, movie in enumerate(top3_movies):
        x_position = width // 2 + (i - 1) * (width // 4)
        y_position = 360

        # Add poster
        poster = Image.open(requests.get(movie['image'], stream=True).raw).resize(poster_size)
        rounded_poster = add_rounded_corners(poster, radius=30)
        image.paste(rounded_poster, (x_position - poster_size[0]//2, y_position), rounded_poster)
        
        # Add rating
        draw.text((x_position, y_position + poster_size[1] + 15), movie['caption'], fill="#FFFFFF", font=emoji_font, anchor="mt")
    

    #draw three circles distributed horizontally
    for i, (label, value) in enumerate(stats):
        circle_radius = 130
        circle_spacing = (circle_radius * 2) + 50
        circle_y = top_margin
        circle_x = (width//2) + (-1+i) * circle_spacing
        colors = [BLUE, GREEN, ORANGE]

        create_circle(draw, (circle_x, circle_y), circle_radius, colors[i])
        
        bbox_number = draw.textbbox((0, 0),value, font=font_numbers)
        text_width_number = bbox_number[2] - bbox_number[0]
        text_x_number = circle_x - (text_width_number // 2)

        bbox_label = draw.textbbox((0, 0), label, font=font_small)
        text_width_label = bbox_label[2] - bbox_label[0]
        text_x_label = circle_x - (text_width_label // 2)
    
        # Adjust the position of the text to be centered
        
        draw.text((text_x_number, circle_y-40),value, font=font_numbers, fill=WHITE)
        draw.text((text_x_label, circle_y+160), label, font=font_small, fill=BLACK)

        

    # Top Genres and number of films
    draw.text((left_margin, top_margin + 280), "Top Genres", font=font_small, fill=ORANGE)

    top3_genres = movie_df['genres'].explode().value_counts().head(3)
    genres = top3_genres.index
    
    num_films = top3_genres.values.astype(str)

    for i in range(3):
        draw.text((left_margin, top_margin + 350 + i*60), f"{genres[i]}", font=font_small, fill=BLACK)
        bbox_label = draw.textbbox((0, 0), num_films[i], font=font_small)
        text_width_label = bbox_label[2] - bbox_label[0]
        text_x_label = width - margin - 50 - text_width_label
        
        draw.text((text_x_label, top_margin + 350 + i*60), num_films[i], font=font_numbers_medium, fill=BLACK)

    # minutes_watched = f"{round(movie_df['runtime'].sum(), 1)}"
    minutes_watched = ("{:,}".format(movie_df['runtime'].sum()))

    # Minutes Listened
    draw.text((left_margin, top_margin + 590), "Minutes Watched", font=font_small, fill=ORANGE)
    draw.text((left_margin, top_margin + 660), minutes_watched, font=font_highlights, fill=BLACK)

    # Top Genre
    vibe = vibe_calculator(movie_df)
    draw.text(((width // 2), top_margin + 590), "Your Vibe", font=font_small, fill=ORANGE)
    draw.text((width // 2, top_margin + 660), vibe, font=font_highlights, fill=BLACK)

    # Add footer
    draw.text((width//2, height - 100), "https://tinyurl.com/letterboxdbi", fill=BLACK, font=font_text, anchor="mm")
    # add qr code to the footer
    base_dir = os.path.dirname(os.path.abspath(__file__))
    qr_code = Image.open(os.path.join(base_dir, '..', 'static/qr_code.png'))

    qr_code = qr_code.resize((100, 100))
    image.paste(qr_code, (width - 150, height - 150))


    # Save image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    # image.save('poster.png')
    img_byte_arr.seek(0)

    return img_byte_arr
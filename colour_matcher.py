from concurrent.futures import ThreadPoolExecutor
from logger_configuration import logger
from colorthief import ColorThief
from bs4 import BeautifulSoup
from io import BytesIO
from math import sqrt
import pandas as pd
import requests
import os
import re


# Colour dictionary and RGB values
# https://stackoverflow.com/questions/54242194/find-the-closest-color-to-a-color-from-given-list-of-colors
colour_dict = {
    'Red': 2000, 'Orange': 2001, 'Yellow': 2002, 'Green': 2003, 'Blue': 2004,
    'Purple': 2005, 'Pink': 2006, 'Black': 2007, 'White': 2008, 'Cream': 2009,
    'Beige': 2010, 'Grey': 2011, 'Brown': 2012, 'Gold': 2001
}

colour_rgb_dict = {
    'Red': (255, 0, 0), 'Orange': (255, 165, 0), 'Yellow': (255, 255, 0),
    'Green': (0, 255, 0), 'Blue': (0, 0, 255), 'Purple': (160, 32, 240),
    'Pink': (255, 192, 203), 'Black': (0, 0, 0), 'White': (255, 255, 255),
    'Cream': (255, 253, 208), 'Beige': (245, 245, 220), 'Grey': (190, 190, 190),
    'Brown': (160, 82, 45), 'Gold': (255, 165, 0)
}

colours_list = list(colour_rgb_dict.values())


# Function to fetch dominant color from an image
def fetch_dominant_color(img_path):
    try:
        if os.path.exists(img_path): 
            with open(img_path, 'rb') as f:
                img_bytes = BytesIO(f.read())
        else:  
            if not img_path.startswith(('http://', 'https://')):
                img_path = 'https://' + img_path.lstrip('/')
            response = requests.get(img_path)
            response.raise_for_status()
            img_bytes = BytesIO(response.content)

        img_bytes.seek(0)
        domColour = ColorThief(img_bytes).get_color(quality=1)
        return domColour

    except requests.exceptions.RequestException as e:
        logger.error(f"couldn't get img: {img_path}: {e}")
    except Exception as e:
        logger.error(f"couldn't get the dominant colour: {img_path}: {e}")
    return None


# Function to find closest color from the list
# Code created from here https://stackoverflow.com/questions/13811483/getting-dominant-color-of-an-image
def closest_colour(rgb, list_name):
    #logging
    logger.info(f"Finding closest color for RGB: {rgb}")
    if not (isinstance(rgb, tuple) and len(rgb) == 3):
        logger.error(f"Invalid RGB value: {rgb}")
        return None
    
    r, g, b = rgb
    colour_diffs = []
    for colour in list_name:
        cr, cg, cb = colour
        colour_diff = sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)
        colour_diffs.append((colour_diff, colour))
    closest = min(colour_diffs)[1]
    return closest

def rgb_distance(rgb1, rgb2):
    return sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

# Scraping function for LoveCrafts
def lovecrafts_colour_match_df(max_depth=10, colour_yarn=''):
    yarn_name, yarn_image, yarn_link = [], [], []

    for counter in range(1, max_depth + 1):
        url = f"https://www.lovecrafts.com/en-gb/l/yarns?filter-colorGroup={colour_yarn}"
        if counter > 1:
            url += f"&page={counter}"

        logger.info(f"Scraping LoveCrafts page {counter}: {url}")
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        yarnTitle = soup.find_all("div", class_="lc-product-card__title")
        yarnImage = soup.find_all("img", class_="lc-product-card__image")
        yarnLink = soup.find_all("a", class_="lc-product-card__link lc-link--pure")
        if not yarnTitle or not yarnImage:
            break

        for name, img, link in zip(yarnTitle, yarnImage, yarnLink):
            yarn_name.append(name.get_text().strip())
            yarn_image.append(img['src'])
            yarn_link.append(link['href'])

    with ThreadPoolExecutor(max_workers=10) as executor:
        rgb = list(executor.map(fetch_dominant_color, yarn_image))

    df = pd.DataFrame(zip(yarn_name, yarn_image, yarn_link, rgb),
                      columns=['name', 'img (.jpg)', 'link', 'rgb'])
    df = df[df['rgb'].apply(lambda x: isinstance(x, tuple) and len(x) == 3)]
    return df


# Scraping function for WoolWarehouse
def woolwarehouse_colour_match_df(max_depth=10, colour_yarn=''):
    yarn_name, yarn_image, yarn_link = [], [], []

    for counter in range(1, max_depth + 1):
        url = f"https://www.woolwarehouse.co.uk/yarn?colour_name={colour_yarn}"
        if counter > 1:
            url += f"&p={counter}"

        logger.info(f"Scraping WoolWarehouse page {counter}: {url}")
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        yarnTitle = soup.find_all("h2", class_="mobile-product-name")
        yarnImage = soup.select('a.product-image > img[src]')
        yarnLink = soup.find_all("a", class_="product-image")
        if not yarnTitle or not yarnImage:
            break

        for name, img, link in zip(yarnTitle, yarnImage, yarnLink):
            name_text = re.split(" - All| - Clearance", name.get_text())[0].strip()
            yarn_name.append(name_text)
            yarn_image.append(img['src'])
            yarn_link.append(link['href'])

    with ThreadPoolExecutor(max_workers=10) as executor:
        rgb = list(executor.map(fetch_dominant_color, yarn_image))

    df = pd.DataFrame(zip(yarn_name, yarn_image, yarn_link, rgb),
                      columns=['name', 'img (.jpg)', 'link', 'rgb'])  
    #validation for length rgb value
    df = df[df['rgb'].apply(lambda x: isinstance(x, tuple) and len(x) == 3)]
    return df


# Function to match the user's RGB to closest color
def colour_match(user_input_rgb):
    #validation
    if user_input_rgb is None:
        logger.error("Invalid RGB")
        return pd.DataFrame(columns=['name', 'img (.jpg)', 'link', 'rgb'])

    closest_rgb = closest_colour(user_input_rgb, colours_list)
    if closest_rgb is None:
        return pd.DataFrame(columns=['name', 'img (.jpg)', 'link', 'rgb'])

    colour_key = [key for key, val in colour_rgb_dict.items() if val == closest_rgb][0]
    logger.info(f"closest colour name: {colour_key}")

    lovecrafts_df = lovecrafts_colour_match_df(colour_yarn=colour_key)
    woolwarehouse_df = woolwarehouse_colour_match_df(colour_yarn=colour_dict[colour_key])
    colour_df = pd.concat([lovecrafts_df, woolwarehouse_df], ignore_index=True)

    if colour_df.empty:
        return pd.DataFrame(columns=['name', 'img (.jpg)', 'link', 'rgb'])

    # Compute distance and sort (but do not limit)
    colour_df['distance'] = colour_df['rgb'].apply(lambda x: rgb_distance(user_input_rgb, x))
    sorted_df = colour_df.sort_values('distance').copy()
    sorted_df.drop(columns='distance', inplace=True)
    
    return sorted_df
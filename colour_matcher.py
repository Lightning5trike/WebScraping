#oly using lovecrafts and woolwarehouse as they are the only websites with clear images that are scrapable
from colorthief import ColorThief
from bs4 import BeautifulSoup
from io import BytesIO
from math import sqrt
import pandas as pd
import requests
import re

input = '' #userinput(figure out)
colour_dict = {'Red':2000, 'Orange':2001, 'Yellow':2002, 'Green':2003, 'Blue':2004, 'Purple':2005, 'Pink':2006, 'Black':2007, 'White':2008, 'Cream':2009, 'Beige':2010, 'Grey':2011, 'Brown':2012, 'Gold':2001}
colour_rgb_dict = {'Red':(255,0,0), 'Orange':(255,165,0), 'Yellow':(255,255,0), 'Green':(0,255,0), 'Blue':(0,0,255), 'Purple':(160,32,240), 'Pink':(255,192,203), 'Black':(0,0,0), 'White':(255,255,255), 'Cream':(255,253,208), 'Beige':(245,245,220), 'Grey':(190,190,190), 'Brown':(160,82,45), 'Gold':(255,165,0)}
colours_list = [(255,0,0), (255,165,0), (255,255,0), (0,255,0), (0,0,255), (160,32,240), (255,192,203), (0,0,0), (255,255,255), (255,253,208), (245,245,220), (190,190,190), (160,82,45), (255,165,0)]

#https://stackoverflow.com/questions/54242194/find-the-closest-color-to-a-color-from-given-list-of-colors
def closest_colour(rgb, list_name):
    r, g, b = rgb
    colour_diffs = []
    for colour in list_name:
        cr, cg, cb = colour
        colour_diff = sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        colour_diffs.append((colour_diff, colour))
        closest = min(colour_diffs)[1]
    return closest

#finds the closes colour to one in the colours list
colour_key = [key for key, val in colour_rgb_dict.items() if val == closest_colour(input, colours_list)]
#matches the colour from the colours list to what would have to be input in the search bar for lc and ww
lovecrafts_colour = colour_key
woolwarehouse_colour = colour_dict[colour_key]

# Code created from here https://stackoverflow.com/questions/13811483/getting-dominant-color-of-an-image
def rgb_of_yarns(url):
    response = requests.get(url)
    image = BytesIO(response.content)
    colour_thief = ColorThief(image)
    dominant_colour = colour_thief.get_color(quality=1)
    return dominant_colour


def lovecrafts_colour_match_df(max_depth=100, colour_yarn=''):
    yarn_name = []
    yarn_image = []
    yarn_link = []
    rgb = []
    
    counter = 1
    while counter <= max_depth:
        if counter == 1:
            page_to_scrape = requests.get(f"https://www.lovecrafts.com/en-gb/l/yarns?filter-colorGroup={colour_yarn}")
        else:
            page_to_scrape = requests.get(f"https://www.lovecrafts.com/en-gb/l/yarns?filter-colorGroup={colour_yarn}&page={counter}") 
        counter += 1
  
        soup = BeautifulSoup(page_to_scrape.text, 'html.parser')
        yarnTitle = soup.find_all("div", attrs={"class": "lc-product-card__title"})
        yarnImage = soup.find_all("img", attrs={"class": "lc-product-card__image"})
        yarnLink = soup.find_all("a", attrs={"class": "lc-product-card__link lc-link--pure"})
        
        for name, img, link in zip(yarnTitle, yarnImage, yarnLink):
            yarn_name.append(name.get_text().strip())
            yarn_image.append(img['src'])
            yarn_link.append(link['href'])
            
        for i in yarn_image:
            rgb.append(rgb_of_yarns(i))

        lc_df = pd.DataFrame(list(zip(yarn_name, yarn_image, yarn_link, rgb)),
            columns=['name', 'img (.jpg)', 'link', 'rgb'])
    return lc_df



#df for colour matching including the name of the yarn the link and the 
def woolwarehouse_colour_match_df(max_depth=100, colour_yarn=''):
    yarn_name = []
    yarn_image = []
    yarn_link = []
    rgb = []
    
    counter = 1
    while counter <= max_depth:
        if counter == 1:
            page_to_scrape = requests.get(f"https://www.woolwarehouse.co.uk/yarn?colour_name={colour_yarn}")
        else:
            page_to_scrape = requests.get(f"https://www.woolwarehouse.co.uk/yarn?colour_name={colour_yarn}&p={counter}")       
        counter += 1
        
        soup = BeautifulSoup(page_to_scrape.text, 'html.parser')
        yarnTitle = soup.find_all("h2", attrs={"class": "mobile-product-name"})
        yarnImage = soup.select('a.product-image > img[src]')
        yarnLink = soup.find_all("a", attrs={"class": "product-image"})
        
        for name, img, link in zip(yarnTitle, yarnImage, yarnLink):
            name_text = name.get_text()
            name_text = re.split(" - All| - Clearance", name_text)
            name_text = name_text[0].strip()
            yarn_name.append(name_text)
            yarn_image.append(img['src'])
            yarn_link.append(link['href'])

        for i in yarn_image:
            rgb.append(rgb_of_yarns(i))
    
    ww_df = pd.DataFrame(list(zip(yarn_name, yarn_image, yarn_link, rgb)),
        columns=['name', 'img (.jpg)', 'link', 'rgb'])
    return ww_df



#when testing insert a colour for the colour yarns because empty otherwise
lovecrafts_df = lovecrafts_colour_match_df(max_depth=100, colour_yarn=lovecrafts_colour)
woolwarehouse_df = woolwarehouse_colour_match_df(max_depth=100, colour_yarn=woolwarehouse_colour)
colour_df = pd.concat([lovecrafts_df, woolwarehouse_df], ignore_index=True)

colours_from_websites = colour_df['rgb'].tolist()
closest_yarn = closest_colour(input, colours_from_websites)
closest_yarn_info = colour_df[colour_df['rgb'] == closest_yarn]
print(closest_yarn_info)
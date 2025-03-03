#oly using lovecrafts and woolwarehouse as they are the only websites with clear images that are scrapable

import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_lovecrafts_yarn_data(max_depth=100, colour_yarn=''):
    yarn_name = []
    yarn_image = []
    yarn_link = []
    
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

    lc_df = pd.DataFrame(list(zip(yarn_name, yarn_image, yarn_link)),
                      columns=['name', 'img (.jpg)', 'link'])
    
    return lc_df



import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def scrape_woolwarehouse_yarn_data(max_depth=100, colour_yarn=''):
    yarn_name = []
    yarn_image = []
    yarn_link = []
    
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
    
    ww_df = pd.DataFrame(list(zip(yarn_name, yarn_image, yarn_link)),
                      columns=['name', 'img (.jpg)', 'link'])
    
    return ww_df


# lovecrafts_df = scrape_lovecrafts_yarn_data(max_depth=50, colour_yarn='red')
# print(lovecrafts_df)

# woolwarehouse_df = scrape_woolwarehouse_yarn_data(max_depth=50, colour_yarn='2000')
# print(woolwarehouse_df)
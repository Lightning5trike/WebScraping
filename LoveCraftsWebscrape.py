from bs4 import BeautifulSoup
import requests
import pandas as pd 

page_to_scrape = requests.get("https://www.lovecrafts.com/en-gb/l/yarns")
soup = BeautifulSoup(page_to_scrape.text, "html.parser")
yarnInfo = soup.findAll("span", attrs={"class":"product-card__subtitle"})
yarnPrice = soup.findAll("small", attrs={"class":"product-price lc price lc-product-card_price"})


#fix pandas thing or find new way to write to an excel page
df = pd.DataFrame()

df['yarnInfo'] = yarnInfo 
df['yarnPrice'] = yarnPrice

df.to_excel('LoveCraftsScrape.xlsx', index = False) 
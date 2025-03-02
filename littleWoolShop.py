from bs4 import BeautifulSoup
import requests
import pandas as pd
import re

yarnName = []
fibres = []
thickness = []
weight = []
pricing = []
pricePerGram = []

counter = 1

while counter <= 28:
    if counter == 1:
        page_to_scrape = requests.get("https://www.lovecrafts.com/en-gb/l/yarns")
    elif counter > 1:
        page_to_scrape = requests.get("https://www.lovecrafts.com/en-gb/l/yarns?page=" + str(counter))
    counter += 1
    
    #get the info from website
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    yarnTitle = soup.find_all("div", attrs={"class": "lc-product-card__title"})
    yarnType = soup.find_all("div", attrs={"class": "lc-product-card__subtitle"})
    yarnPrice = soup.find_all("div", attrs={"class": "product-price lc-price lc-product-card__price"})
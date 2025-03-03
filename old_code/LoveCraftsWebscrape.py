from bs4 import BeautifulSoup
import requests
import pandas as pd 

yarnName = []
fibres = []
thickness = []
weight = []
pricing = []
strippedPricing = []
pricePerGram = []

counter = 1

#going through each of the pages on the website
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

    #going through the main list of info and splitting each part up
    for name, yarn, price in zip(yarnTitle, yarnType, yarnPrice):
        yarn_text = yarn.get_text().strip()
        splitter = yarn_text.split(", ")
        if len(splitter) == 3:
            fibres.append(splitter[0])
            thickness.append(splitter[2])
            yarnName.append(name.get_text().strip())

            weight_string = splitter[1]
            if "/"  in weight_string:
                after_slash = weight_string.split("/", 1)
                before_grams = after_slash[1].split("g")[0]
            else:
                before_grams = None
            weight.append(before_grams)

            # because theres 2 price options only show one
            price_text = price.get_text().strip()
            indexN = price_text.find("\n") 
            if indexN != -1: 
                priceStr = price_text[:indexN].strip()
            else:
                priceStr = price_text.strip()
            pricing.append(priceStr)


for old in pricing:
    priceStrip = ''.join(filter(str.isdigit, old))
    if priceStrip:
        newPrice = float(priceStrip) / 100
        strippedPricing.append(newPrice)

#math to make ppm
    for x, y in zip(weight, strippedPricing):
        if (x != None) and (y != None):
            ppg = round((float(y) / float(x)), 4)
        else:
            ppg = None
        pricePerGram.append(ppg)


df = pd.DataFrame(list(zip(
                yarnName, fibres, thickness, weight, pricing, pricePerGram
            )), columns=['name', 'fibres', 'thickness', 'weight(g)', 'price(£)', 'ppg'])


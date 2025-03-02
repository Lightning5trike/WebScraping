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

while counter <= 27:
    if counter == 1:
        page_to_scrape = requests.get("https://www.woolwarehouse.co.uk/yarn")
    else:
        page_to_scrape = requests.get(f"https://www.woolwarehouse.co.uk/yarn?p={counter}")
    counter += 1

    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    yarnTitle = soup.find_all("h2", attrs={"class": "mobile-product-name"})
    yarnType = soup.find_all("div", attrs={"class": "desc std"})
    yarnPrice = soup.find_all("div", attrs={"class": "gbp-price"})

    for name, yarn, price in zip(yarnTitle, yarnType, yarnPrice):
        
        price_text = price.get_text()
        price_text = re.sub('[^0-9,.]', '', price_text)
        pricing.append(price_text)
        
        name_text = name.get_text()
        name_text = re.split(" - All| - Clearance", name_text)
        name_text = name_text[0]
        name_text = name_text.strip()
        yarnName.append(name_text)
       
        yarn_text = yarn.get_text()
        yarn_text = re.split("g ", yarn_text, 2)
        weight_text = yarn_text[0]
        weight.append(weight_text)

        yarn_info = yarn_text[1]
        split_yarn_info = re.split("(\d+%)",yarn_info)
        yarn_thickness = split_yarn_info[0]
        thickness.append(yarn_thickness)

        fibre_combination = ''.join(split_yarn_info[1:])
        fibres.append(fibre_combination)


    for x, y in zip(weight, pricing):
        if x != '' and y!= '':
            ppg = round((float(y) / float(x)), 4)
        else:
            ppg = None
        pricePerGram.append(ppg)
        

df = pd.DataFrame(list(zip(
                yarnName, fibres, thickness, weight, pricing, pricePerGram
            )), columns=['name', 'fibres', 'thickness', 'weight(g)', 'price(£)', 'ppg'])
    
print(df)
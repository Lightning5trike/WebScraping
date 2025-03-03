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
pricing_old = []

counter = 1

while counter <= 15:
    if counter == 1:
        page_to_scrape = requests.get("https://littlewoolshop.com/collections/yarn-by-weight")
    elif counter > 1:
        page_to_scrape = requests.get("https://littlewoolshop.com/collections/yarn-by-weight?page=" + str(counter))
    counter += 1
   
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    yarnTitle = soup.find_all("a", attrs={"class": "card-link text-current js-prod-link"})
    yarnFibre = soup.find_all("p", string=re.compile(r"\d+%"))
    yarnPrice = soup.find_all("div", attrs={"class": "price__default"})

    for name, fibre, price in zip(yarnTitle, yarnFibre, yarnPrice):
        fibre_text = fibre.get_text().strip()
        fibres.append(fibre_text)
        
        name_text = name.get_text().strip()
        split_name_text = re.split("(\d+g)", name_text)
        
        if len(split_name_text) > 2:
            weight_split = split_name_text[1]
            weight_stripped = re.sub('g', '', weight_split)
            weight.append(weight_stripped)
        else:
            weight.append(None)

        price_clean = re.sub('From|£', '', price.text)
        stripped_price = price_clean.strip()
        pricing_old.append(stripped_price)

        for x in pricing_old:
            if "\n\n" in x:
                y = re.split("\n\n", x)
                pricing.append(y)
            else:
                pricing.append(x)
        
        thickness_options = ['Lace', '2 Ply', '3 Ply', '4 Ply', 'Double Knitting', 'DK', 'Aran', 'Chunky', 'Super Chunky']
        for j in reversed(thickness_options):
            if j in name_text:
                thickness.append(j)
                
                title = name_text.split(j, 1)[0]
                title = title.strip()
                yarnName.append(title)
        

    for x, y in zip(weight, pricing):
        if x != None and y!= None:
            ppg = round((float(y) / float(x)), 4)
        else:
            ppg = None
        pricePerGram.append(ppg)


df = pd.DataFrame(list(zip(
                yarnName, fibres, thickness,
                pricing, weight, pricing, pricePerGram
            )), columns=['name', 'fibres', 'thickness', 'pricing', 'weight(g)', 'price(£)', 'ppg'])
    



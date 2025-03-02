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

while counter <= 31:
    if counter == 1:
        page_to_scrape = requests.get("https://www.woolbox.co.uk/yarn/all-knitting-crochet-yarn-and-wool.html")
    else:
        page_to_scrape = requests.get(f"https://www.woolbox.co.uk/yarn/all-knitting-crochet-yarn-and-wool.html?p={counter}")
    counter += 1

    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    yarnTitle = soup.find_all("a", attrs={"class": "product-item-link hover:underline"})
    yarnFibre = soup.find_all("div", attrs={"class": "plp-usps text-sm text-abdarkgrey font-bold my-2"})
    yarnPrice = soup.find_all("span", attrs={"class": "price"})

    for name, fibre, price in zip(yarnTitle, yarnFibre, yarnPrice):
        price_text = price.get_text().strip()
        price_stripped = re.sub('£', '', price.text)
        pricing.append(price_stripped)

        name_text = name.get_text().strip()
        thickness_options = ['Lace', '2 Ply', '3 Ply', '4 Ply', '4Ply', 'Double Knitting', 'DK', 'Aran', 'Worsted' 'Chunky', 'Super Chunky']
        for j in reversed(thickness_options):
            if j in name_text:
                thickness.append(j)
        
        grams = re.split("(\d+)g|(\d+) grm", name_text)
        grams = list(filter(lambda x: x is not None, grams))
        combine=' '.join(map(str,grams))
        yarnName.append(combine) 
        grams_lst = []
        for k in grams:
            try:
                float(k)
                grams_lst.append(float(k))
            except ValueError:
                pass
        for n in grams_lst:
            weight.append(grams_lst[-1])

        fibre_text = fibre.get_text().strip()
        fibre_text = re.sub(r"[.(\n)(\r)]", '', fibre_text)
        fibre_split = re.split("(?<![A-Z\W])(?=[A-Z])|West", fibre_text)
        fibres.append(fibre_split[0])

    for x, y in zip(weight, pricing):
        if x != None and y!= None:
            ppg = round((float(y) / float(x)), 4)
        else:
            ppg = None
        pricePerGram.append(ppg)


df = pd.DataFrame(list(zip(
                yarnName, fibres, thickness, weight, pricing, pricePerGram
            )), columns=['name', 'fibres', 'thickness', 'weight(g)', 'price(£)', 'ppg'])

print(df)

         
    


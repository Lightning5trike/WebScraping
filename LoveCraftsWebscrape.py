from bs4 import BeautifulSoup
import requests
import pandas as pd 

yarnName = []
fibres = []
length = []
meterageOnly = []
weight = []
pricing = []
strippedPricing = []
pricePerMeter = []

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
    yarnTitle = soup.findAll("h2", attrs={"class":"product-card__title"})
    yarnType = soup.findAll("p", attrs={"class":"product-card__subtitle"})
    yarnPrice = soup.findAll("div", attrs={"class": "product-price lc-price lc-product-card__price"})

    #going through the main list of info and splitting each part up
    for name, yarn, price in zip(yarnTitle, yarnType, yarnPrice):
        yarn_text = yarn.get_text().strip()
        splitter = yarn_text.split(", ")
        if len(splitter) == 3:
            fibres.append(splitter[0])
            length.append(splitter[1])
            weight.append(splitter[2])
            yarnName.append(name.get_text().strip())

            # because theres 2 price options only show one
            price_text = price.get_text().strip()
            indexN = price_text.find("\n") 
            if indexN != -1: 
                priceStr = price_text[:indexN].strip()
            else:
                priceStr = price_text.strip()
            pricing.append(priceStr)


#get the length and price in float form for the math
for meters in length:
    metersStripped = meters.strip()
    try:
        indexM = metersStripped.index("m")
        newLength = float(metersStripped[:indexM])
    except ValueError:
        newLength = 1
    meterageOnly.append(newLength)

# Strip and convert pricing to float
for old in pricing:
    priceStrip = ''.join(filter(str.isdigit, old))
    if priceStrip:
        newPrice = float(priceStrip) / 100
        strippedPricing.append(newPrice)
    else:
        strippedPricing.append(1) 

# math to make ppm
for x, y in zip(meterageOnly, strippedPricing):
    if y is not None:
        ppm = round((y/x), 4)
        pricePerMeter.append(ppm)
    else:
        pricePerMeter.append(1)


df = pd.DataFrame(list(zip(yarnName, fibres, length, weight, pricing, meterageOnly, strippedPricing, pricePerMeter)), columns=['name', 'fibres', 'length', 'weight', 'pricing', 'meters', 'price(kinda)', 'ppm'])

with pd.ExcelWriter('LoveCraftsWebscrape.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='main')
    workbook = writer.book
    format1 = workbook.add_format({'num_format': '0.0000'})

    sheets = {
        'weight': ['DK', 'Aran', 'Chunky', 'Worsted'],
        'fibres': ['100% Acrylic', '100% Cotton', '100% Wool']
    }

    for category, values in sheets.items():
        for value in values:
            filtered_df = df[df[category] == value]
            filtered_df.to_excel(writer, sheet_name=f'{value} Yarns')
            worksheet = writer.sheets[f'{value} Yarns']
            worksheet.set_column('I:I', None, format1)
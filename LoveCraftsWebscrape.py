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

while counter <= 28:
    if counter == 1:
        page_to_scrape = requests.get("https://www.lovecrafts.com/en-gb/l/yarns")
    elif counter > 1:
        page_to_scrape = requests.get("https://www.lovecrafts.com/en-gb/l/yarns?page=" + str(counter))
    counter += 1
    
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    yarnTitle = soup.findAll("h2", attrs={"class":"product-card__title"})
    yarnType = soup.findAll("p", attrs={"class":"product-card__subtitle"})
    yarnPrice = soup.findAll("span", attrs={"class":"lc-price__regular"})

    for name, yarn, price in zip(yarnTitle, yarnType, yarnPrice):
        yarn_text = yarn.get_text().strip()
        splitter = yarn_text.split(", ")
        if len(splitter) == 3:
            fibres.append(splitter[0])
            length.append(splitter[1])
            weight.append(splitter[2])
            yarnName.append(name.get_text().strip())

            price_text = price.get_text().strip()
            indexN = price_text.find("\n") 
            if indexN != -1: 
                priceStr = price_text[:indexN].strip()
            else:
                priceStr = price_text.strip()
            pricing.append(priceStr)
        

for meters in length:
    metersStripped = meters.strip()
    try:
        indexM = metersStripped.index("m")
        newLength = float(metersStripped[:indexM])
    except ValueError:
        newLength = 1
    meterageOnly.append(newLength)

for old in pricing:
    priceStrip = ''.join(filter(str.isdigit, old))
    if priceStrip:
        newPrice = float(priceStrip) / 100
        strippedPricing.append(newPrice)
        

for x, y in zip(meterageOnly, strippedPricing):
    ppm = round((y/x), 4)
    pricePerMeter.append(ppm)


df = pd.DataFrame(list(zip(yarnName, fibres, length, weight, pricing, meterageOnly, strippedPricing, pricePerMeter)), columns = ['name', 'fibre', 'length','weight', 'pricing', 'meters', 'price(kinda)', 'ppm'])

writer = pd.ExcelWriter('LoveCraftsWebscrape.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='main')

workbook = writer.book
worksheet = writer.sheets['main']

format1 = workbook.add_format({'num_format': '0.0000'})
worksheet.set_column('I:I', None, format1)

writer.close()
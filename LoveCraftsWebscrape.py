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

for old in pricing:
    priceStrip = ''.join(filter(str.isdigit, old))
    if priceStrip:
        newPrice = float(priceStrip) / 100
        strippedPricing.append(newPrice)

#math to make ppm
for x, y in zip(meterageOnly, strippedPricing):
    ppm = round((y/x), 4)
    pricePerMeter.append(ppm)



#writing to excel sheet
with pd.ExcelWriter('LoveCraftsWebscrape.xlsx', engine='xlsxwriter') as writer:
    df1 = pd.DataFrame(list(zip(yarnName, fibres, length, weight, pricing, meterageOnly, strippedPricing, pricePerMeter)), columns=['name', 'fibre', 'length', 'weight', 'pricing', 'meters', 'price(kinda)', 'ppm'])
    df1.to_excel(writer, sheet_name='main')

    #filtering each sheet by weight of yarn
    dfDK = df1[df1['weight'] == 'DK']
    dfDK.to_excel(writer, sheet_name='DK Yarns')
    dfAran = df1[df1['weight'] == 'Aran']
    dfAran.to_excel(writer, sheet_name='Aran Yarns')
    dfChunky = df1[df1['weight'] == 'Chunky']
    dfChunky.to_excel(writer, sheet_name='Chunky Yarns')

    #formatting
    workbook = writer.book
    format1 = workbook.add_format({'num_format': '0.0000'})
    
    worksheet1 = writer.sheets['main']
    worksheet1.set_column('I:I', None, format1)
    worksheet2 = writer.sheets['DK Yarns']
    worksheet2.set_column('I:I', None, format1)
    worksheet3 = writer.sheets['Aran Yarns']
    worksheet3.set_column('I:I', None, format1)
    worksheet4 = writer.sheets['Chunky Yarns']
    worksheet4.set_column('I:I', None, format1)



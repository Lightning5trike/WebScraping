#Trial page using a very filtered version of the yarn page
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

page_to_scrape = requests.get("https://www.lovecrafts.com/en-gb/l/yarns?filter-yarnWeight.en-GB=Aran&filter-fibers.en-GB=Wool")
soup = BeautifulSoup(page_to_scrape.text, "html.parser")
#the inspect google thing
yarnCards = soup.findAll("div", attrs={"class":"product-card__wrapper"})
for card in yarnCards:
    yarnTitle = card.find("h2", attrs={"class":"product-card__title"}).get_text().strip()
    yarnType = card.find("p", attrs={"class":"product-card__subtitle"}).get_text().strip()
    yarnPrice = card.find("span", attrs={"class": "lc-price__regular"})
    if not yarnPrice:
        yarnPrice = card.find("del", attrs={"class": "lc-price__old"})

#goes through each yarn on the page and strips it of the unnecessary info
#splits it into 3 seperate piece of information
    splitter = yarnType.split(", ")
    if len(splitter) == 3:
        #adds each piece of info into the correct list
        fibres.append(splitter[0])
        length.append(splitter[1])
        weight.append(splitter[2])

#goes through the length and then splits at the m so i can get the meters
for meters in length:
    metersStripped = meters.strip()
    try:
        indexM = metersStripped.index("m")
        newLength = float(metersStripped[:indexM])
    except ValueError:
        #was an error value when put as none when doing the math
        newLength = 1
    meterageOnly.append(newLength)

#
for old in pricing:
    priceStrip = ''.join(filter(str.isdigit, old))
    if priceStrip:
        newPrice = float(priceStrip) / 100
        strippedPricing.append(newPrice)
    
# do the maths for seperate columns to figure out pound per meter
for x, y in zip(meterageOnly, strippedPricing):
    ppm = float(y)/float(x)
    ppm_rounded = round(ppm, 4)
    pricePerMeter.append(ppm_rounded)


df = pd.DataFrame(list(zip(yarnName, fibres, length, weight, pricing, meterageOnly, strippedPricing, pricePerMeter)), columns = ['name', 'fibre', 'length','weight', 'pricing', 'meters', 'price(kinda)', 'ppm'])

# print(df)

# writer = pd.ExcelWriter('LoveCraftTrial.xlsx', engine='xlsxwriter')
# df.to_excel(writer, sheet_name='welcome')

workbook = writer.book
worksheet = writer.sheets['welcome']

format1 = workbook.add_format({'num_format': '0.0000'})
worksheet.set_column('I:I', None, format1)

# writer.close()





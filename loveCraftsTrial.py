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

page_to_scrape = requests.get("https://www.lovecrafts.com/en-gb/l/yarns?filter-yarnWeight.en-GB=Aran&filter-fibers.en-GB=Wool")
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
        pricing.append(price.get_text().strip())


for meters in length:
    metersStripped = meters.strip()
    indexM = metersStripped.index("m")
    newLength = float(metersStripped[:indexM])
    meterageOnly.append(newLength)

for old in pricing:
    priceStrip = old.strip()
    newPrice = float(priceStrip[1:])
    strippedPricing.append(newPrice)
    
# do the maths for seperate columns to figure out pound per meter


df = pd.DataFrame(list(zip(yarnName, fibres, length, weight, pricing, meterageOnly, strippedPricing)), columns = ['name', 'fibre', 'length','weight', 'pricing', 'meters', 'price(kinda)'])

writer = pd.ExcelWriter('LoveCraftTrial.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='welcome')

workbook = writer.book
worksheer = writer.sheets['welcome']

writer.close()





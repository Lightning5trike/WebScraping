from bs4 import BeautifulSoup
import requests
import pandas as pd 

fibres = []
length = []
weight = []
pricing = []


#add in the yarn info so i candifferentiate the types of yarn
page_to_scrape = requests.get("https://www.lovecrafts.com/en-gb/l/yarns?filter-yarnWeight.en-GB=Aran&filter-fibers.en-GB=Wool")
soup = BeautifulSoup(page_to_scrape.text, "html.parser")
yarnType = soup.findAll("p", attrs={"class":"product-card__subtitle"})
yarnPrice = soup.findAll("span", attrs={"class":"lc-price__regular"})

for yarn, price in zip(yarnType, yarnPrice):
    yarn_text = yarn.get_text().strip()
    splitter = yarn_text.split(", ")
    if len(splitter) == 3:
        fibres.append(splitter[0])
        length.append(splitter[1])
        weight.append(splitter[2])
        pricing.append(price.get_text())


#do the maths for seperate columns to figure out pound per meter

df = pd.DataFrame(list(zip(fibres, length, weight, pricing)), columns = ['fibre', 'length', 'weight', 'pricing'])

print(df)

writer = pd.ExcelWriter('LoveCraftsScrape.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='welcome')

workbook = writer.book
worksheer = writer.sheets['welcome']

writer.close()

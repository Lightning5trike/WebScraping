from bs4 import BeautifulSoup
import requests
import pandas as pd 


yarnInfo = []
pricing = []

page_to_scrape = requests.get("https://www.lovecrafts.com/en-gb/l/yarns")
soup = BeautifulSoup(page_to_scrape.text, "html.parser")
yarnType = soup.findAll("p", attrs={"class":"product-card__subtitle"})
yarnPrice = soup.findAll("span", attrs={"class":"lc-price__regular"})

for yarn in yarnType:
    yarnInfo.append(yarn)
for price in yarnPrice:
    pricing.append(price)

df = pd.DataFrame(list(zip(yarnInfo, pricing)), columns = ['yarn info', 'pricing'])

writer = pd.ExcelWriter('LoveCraftsScrape.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='welcome')

workbook = writer.book
worksheer = writer.sheets['welcome']

writer.close()

#sort the data in the Info sectoion into defferent colums and technically into different lists
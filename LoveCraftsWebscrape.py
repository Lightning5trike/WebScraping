from bs4 import BeautifulSoup
import requests
import pandas as pd 
# import xlsxwriter

yarnInfo = []
# pricing = []

page_to_scrape = requests.get("https://www.lovecrafts.com/en-gb/l/yarns")
soup = BeautifulSoup(page_to_scrape.text, "html.parser")
yarnType = soup.findAll("span", attrs={"class":"product-card__subtitle"})
yarnPrice = soup.findAll("small", attrs={"class":"product-price lc price lc-product-card_price"})

# for yarn in yarnType:
#     yarnInfo.append(yarn)
# for price in yarnPrice:
#     pricing.append(price)

for type, price in zip (yarnType, yarnPrice):
    yarnInfo.append([type], [price])

df = pd.DataFrame(yarnInfo)

df['Info'] = yarnInfo[0::2] 
df['Price'] = yarnInfo[1::2] 

# df['yarnType'] = yarnInfo[]
# df['yarnPrice'] = pricing[]

writer = pd.ExcelWriter('LoveCraftsScrape.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='welcome', index=False)
writer._save()

# can now write to file
# current issue: not writing the correct information to the file
# i think something is wrong with the listing
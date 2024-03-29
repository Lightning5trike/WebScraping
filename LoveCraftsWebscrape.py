from bs4 import BeautifulSoup
import requests
import pandas as pd 

yarnName = []
fibres = []
length = []
weight = []
pricing = []

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
            pricing.append(price.get_text().strip())


    df = pd.DataFrame(list(zip(yarnName, fibres, length, weight, pricing)), columns = ['name', 'fibre', 'length', 'weight', 'pricing'])

    # print(df)

    writer = pd.ExcelWriter('LoveCraftsScrape.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='welcome')

    workbook = writer.book
    worksheer = writer.sheets['welcome']

    writer.close()
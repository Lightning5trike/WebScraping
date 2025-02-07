# from bs4 import BeautifulSoup
# import requests
# import pandas as pd 

# yarnName = []
# fibres = []
# length = []
# meterageOnly = []
# weight = []
# pricing = []
# strippedPricing = []
# pricePerMeter = []

# counter = 1

# #going through each of the pages on the website
# while counter <= 28:
#     if counter == 1:
#         page_to_scrape = requests.get("https://www.lovecrafts.com/en-gb/l/yarns")
#     elif counter > 1:
#         page_to_scrape = requests.get("https://www.lovecrafts.com/en-gb/l/yarns?page=" + str(counter))
#     counter += 1
    
#     #get the info from website
#     soup = BeautifulSoup(page_to_scrape.text, "html.parser")
#     yarnTitle = soup.findAll("h2", attrs={"class":"product-card__title"})
#     yarnType = soup.findAll("p", attrs={"class":"product-card__subtitle"})
#     yarnPrice = soup.findAll("div", attrs={"class": "product-price lc-price lc-product-card__price"})

#     #going through the main list of info and splitting each part up
#     for name, yarn, price in zip(yarnTitle, yarnType, yarnPrice):
#         yarn_text = yarn.get_text().strip()
#         splitter = yarn_text.split(", ")
#         if len(splitter) == 3:
#             fibres.append(splitter[0])
#             length.append(splitter[1])
#             weight.append(splitter[2])
#             yarnName.append(name.get_text().strip())

#             # because theres 2 price options only show one
#             price_text = price.get_text().strip()
#             indexN = price_text.find("\n") 
#             if indexN != -1: 
#                 priceStr = price_text[:indexN].strip()
#             else:
#                 priceStr = price_text.strip()
#             pricing.append(priceStr)


# #get the length and price in float form for the math
# for meters in length:
#     metersStripped = meters.strip()
#     try:
#         indexM = metersStripped.index("m")
#         newLength = float(metersStripped[:indexM])
#     except ValueError:
#         newLength = 1
#     meterageOnly.append(newLength)

# # Strip and convert pricing to float
# for old in pricing:
#     priceStrip = ''.join(filter(str.isdigit, old))
#     if priceStrip:
#         newPrice = float(priceStrip) / 100
#         strippedPricing.append(newPrice)
#     else:
#         strippedPricing.append(1) 

# # math to make ppm
# for x, y in zip(meterageOnly, strippedPricing):
#     if y is not None:
#         ppm = round((y/x), 4)
#         pricePerMeter.append(ppm)
#     else:
#         pricePerMeter.append(1)


# df = pd.DataFrame(list(zip(yarnName, fibres, length, weight, pricing, meterageOnly, strippedPricing, pricePerMeter)), columns=['name', 'fibres', 'length', 'weight', 'pricing', 'meters', 'price(kinda)', 'ppm'])

# with pd.ExcelWriter('LoveCraftsWebscrape.xlsx', engine='xlsxwriter') as writer:
#     df.to_excel(writer, sheet_name='main')
#     workbook = writer.book
#     format1 = workbook.add_format({'num_format': '0.0000'})

#     sheets = {
#         'weight': ['DK', 'Aran', 'Chunky', 'Worsted'],
#         'fibres': ['100% Acrylic', '100% Cotton', '100% Wool']
#     }

#     for category, values in sheets.items():
#         for value in values:
#             filtered_df = df[df[category] == value]
#             filtered_df.to_excel(writer, sheet_name=f'{value} Yarns')
#             worksheet = writer.sheets[f'{value} Yarns']
#             worksheet.set_column('I:I', None, format1)



from bs4 import BeautifulSoup
import requests
import pandas as pd

class YarnScraper:
    def __init__(self, base_url="https://www.lovecrafts.com/en-gb/l/yarns", pages=28):
        self.base_url = base_url
        self.pages = pages
        self.yarn_name = []
        self.fibres = []
        self.length = []
        self.meterage_only = []
        self.weight = []
        self.pricing = []
        self.stripped_pricing = []
        self.price_per_meter = []
    
    def scrape_pages(self):
        for counter in range(1, self.pages + 1):
            url = self.base_url if counter == 1 else f"{self.base_url}?page={counter}"
            page_to_scrape = requests.get(url)
            soup = BeautifulSoup(page_to_scrape.text, "html.parser")
            
            yarn_titles = soup.findAll("h2", class_="product-card__title")
            yarn_types = soup.findAll("p", class_="product-card__subtitle")
            yarn_prices = soup.findAll("div", class_="product-price lc-price lc-product-card__price")
            
            for name, yarn, price in zip(yarn_titles, yarn_types, yarn_prices):
                yarn_text = yarn.get_text().strip()
                splitter = yarn_text.split(", ")
                if len(splitter) == 3:
                    self.fibres.append(splitter[0])
                    self.length.append(splitter[1])
                    self.weight.append(splitter[2])
                    self.yarn_name.append(name.get_text().strip())
                    
                    price_text = price.get_text().strip()
                    index_n = price_text.find("\n") 
                    self.pricing.append(price_text[:index_n].strip() if index_n != -1 else price_text.strip())
    
    def process_data(self):
        for meters in self.length:
            meters_stripped = meters.strip()
            try:
                index_m = meters_stripped.index("m")
                new_length = float(meters_stripped[:index_m])
            except ValueError:
                new_length = 1
            self.meterage_only.append(new_length)
        
        for old in self.pricing:
            price_strip = ''.join(filter(str.isdigit, old))
            new_price = float(price_strip) / 100 if price_strip else 1
            self.stripped_pricing.append(new_price)
        
        for meters, price in zip(self.meterage_only, self.stripped_pricing):
            ppm = round((price / meters), 4) if meters else 1
            self.price_per_meter.append(ppm)
    
    def to_dataframe(self):
        return pd.DataFrame(
            list(zip(self.yarn_name, self.fibres, self.length, self.weight, self.pricing, self.meterage_only, self.stripped_pricing, self.price_per_meter)),
            columns=['name', 'fibres', 'length', 'weight', 'pricing', 'meters', 'price(kinda)', 'ppm']
        )
    
    def run(self):
        self.scrape_pages()
        self.process_data()
        return self.to_dataframe()
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

#SuperClass that does the scraping and gets all the info for the columns
class YarnScraper:
    def __init__(self, base_url, pages, source):
        self.base_url = base_url
        self.pages = pages
        self.source = source
        self.yarnName = []
        self.fibres = []
        self.thickness = []
        self.weight = []
        self.pricing = []
        self.pricePerGram = []

    def get_page(self, counter):
        url = self.base_url if counter == 1 else self.base_url + f"?page={counter}"
        return requests.get(url).text

    def scrape(self):
        for counter in range(1, self.pages + 1):
            soup = BeautifulSoup(self.get_page(counter), "html.parser")
            self.extract_data(soup)

        self.calculate_ppg()
        return self.to_dataframe()

    def extract_data(self, soup):
        pass  # implemented by subclasses

    #calculate price per gram
    def calculate_ppg(self):
        for x, y in zip(self.weight, self.pricing):
            try:
                ppg = round(float(y) / float(x), 4) if x and y else None
            except ValueError:
                ppg = None
            self.pricePerGram.append(ppg)

    def to_dataframe(self):
        return pd.DataFrame({
            'name': self.yarnName,
            'fibres': self.fibres,
            'thickness': self.thickness,
            'weight(g)': self.weight,
            'price(£)': self.pricing,
            'ppg': self.pricePerGram,
            'source': self.source
        })

class LittleWoolShopScraper(YarnScraper):
    def __init__(self):
        super().__init__("https://littlewoolshop.com/collections/yarn-by-weight", 15, "Little Wool Shop")
    
    def extract_data(self, soup):
        yarnTitle = soup.find_all("a", class_="card-link text-current js-prod-link")
        yarnFibre = soup.find_all("p", string=re.compile(r"\d+%"))
        yarnPrice = soup.find_all("div", class_="price__default")

        for name, fibre, price in zip(yarnTitle, yarnFibre, yarnPrice):
            self.fibres.append(fibre.get_text().strip())
            name_text = name.get_text().strip()
            self.yarnName.append(name_text)
            
            weight_match = re.search(r"(\d+)g", name_text)
            self.weight.append(weight_match.group(1) if weight_match else None)
            
            price_clean = re.sub(r'From|£', '', price.text).strip()
            self.pricing.append(price_clean)

            thickness_options = ['Lace', '2 Ply', '3 Ply', '4 Ply', 'Double Knitting', 'DK', 'Aran', 'Chunky', 'Super Chunky']
            for j in reversed(thickness_options):
                if j in name_text:
                    self.thickness.append(j)
                    break
            else:
                self.thickness.append(None)

class LoveCraftsScraper(YarnScraper):
    def __init__(self):
        super().__init__("https://www.lovecrafts.com/en-gb/l/yarns", 28, "LoveCrafts")
    
    def extract_data(self, soup):
        yarnTitle = soup.find_all("div", class_="lc-product-card__title")
        yarnType = soup.find_all("div", class_="lc-product-card__subtitle")
        yarnPrice = soup.find_all("div", class_="product-price lc-price lc-product-card__price")

        for name, yarn, price in zip(yarnTitle, yarnType, yarnPrice):
            details = yarn.get_text().strip().split(", ")
            self.fibres.append(details[0] if len(details) > 0 else None)
            self.thickness.append(details[2] if len(details) > 2 else None)
            self.yarnName.append(name.get_text().strip())
            
            weight_match = re.search(r"(\d+)g", details[1]) if len(details) > 1 else None
            self.weight.append(weight_match.group(1) if weight_match else None)
            
            price_text = price.get_text().strip().split("\n")[0]
            self.pricing.append(re.sub(r'[^0-9.]', '', price_text))

class WoolBoxScraper(YarnScraper):
    def __init__(self):
        super().__init__("https://www.woolbox.co.uk/yarn/all-knitting-crochet-yarn-and-wool.html", 31, "Wool Box")
    
    def fetch_page(self, counter):
        url = self.base_url if counter == 1 else f"{self.base_url}?p={counter}"
        return requests.get(url).text

    def extract_data(self, soup):
        yarnTitle = soup.find_all("a", class_="product-item-link hover:underline")
        yarnFibre = soup.find_all("div", class_="plp-usps text-sm text-abdarkgrey font-bold my-2")
        yarnPrice = soup.find_all("span", class_="price")

        for name, fibre, price in zip(yarnTitle, yarnFibre, yarnPrice):
            self.pricing.append(re.sub('£', '', price.text.strip()))
            
            name_text = name.get_text().strip()
            self.yarnName.append(name_text)
            
            weight_match = re.search(r"(\d+)g", name_text)
            self.weight.append(weight_match.group(1) if weight_match else None)
            
            fibre_text = fibre.get_text().strip()
            self.fibres.append(fibre_text.split(" ")[0])

            thickness_options = ['Lace', '2 Ply', '3 Ply', '4 Ply', 'Double Knitting', 'DK', 'Aran', 'Chunky', 'Super Chunky']
            for j in reversed(thickness_options):
                if j in name_text:
                    self.thickness.append(j)
                    break
            else:
                self.thickness.append(None)

class WoolWarehouseScraper(YarnScraper):
    def __init__(self):
        super().__init__("https://www.woolwarehouse.co.uk/yarn", 27, "Wool Warehouse")

    def extract_data(self, soup):
        yarnTitle = soup.find_all("h2", class_="mobile-product-name")
        yarnType = soup.find_all("div", class_="desc std")
        yarnPrice = soup.find_all("div", class_="gbp-price")

        for name, yarn, price in zip(yarnTitle, yarnType, yarnPrice):
            self.pricing.append(re.sub('[^0-9,.]', '', price.get_text().strip()))
            self.yarnName.append(name.get_text().strip().split(" - ")[0])
            
            details = yarn.get_text().strip().split("g ")
            self.weight.append(details[0] if len(details) > 0 else None)
            
            split_details = re.split("(\d+%)", details[1]) if len(details) > 1 else []
            self.thickness.append(split_details[0] if split_details else None)
            self.fibres.append(" ".join(split_details[1:]))

# Runs all scrapers
dfs = [scraper().scrape() for scraper in [LittleWoolShopScraper, LoveCraftsScraper, WoolBoxScraper, WoolWarehouseScraper]]
final_df = pd.concat(dfs, ignore_index=True)
# print(final_df)

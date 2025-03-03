from fastapi import FastAPI
from webscraper_classes import *
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/yarns")
async def get_yarns():
    dfs = [scraper().scrape() for scraper in [LittleWoolShopScraper, LoveCraftsScraper, WoolBoxScraper, WoolWarehouseScraper]]
    final_df = pd.concat(dfs, ignore_index=True)
    if final_df.empty:
        return {"error": "No data scraped"}
    return final_df.to_dict(orient="records")


from fastapi import FastAPI
from LoveCraftsWebscrape import LovecraftsScraper

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/yarns")
async def get_yarns():
    scraper = LovecraftsScraper()
    df = scraper.run()
    if df.empty:
        return {"error": "No data scraped"}
    return df.to_dict(orient="records")


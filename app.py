from flask import Flask, render_template, url_for, request, session, redirect
from webscraper_classes import *
from colour_matcher import *
from werkzeug.utils import secure_filename
import pandas as pd
import os

from logger_configuration import logger

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Scrape once at startup
dfs = [scraper().scrape() for scraper in [LittleWoolShopScraper, LoveCraftsScraper, WoolBoxScraper, WoolWarehouseScraper]]
final_df = pd.concat(dfs, ignore_index=True)

# Upload folder config
upload_folder = os.path.join('images', 'uploads')
app.config['UPLOAD'] = upload_folder


@app.route('/pricecomparison', methods=['GET', 'POST'])
def pricecomparison_tohtml():
    if final_df.empty:
        logger.warning("No data scraped from any site.")
        return "error No data scraped"
    logger.info("Serving price comparison page.")
    return render_template('pricecomparison.html',
                           column_names=final_df.columns.values,
                           row_data=list(final_df.values.tolist()),
                           zip=zip)


#https://geekpython.in/render-images-from-flask
@app.route('/colourmatch', methods=['GET', 'POST'])
def colourMatch_tohtml():
    if request.method == 'POST':
        file = request.files['img']
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD'], filename)
        file.save(save_path)
        logger.info(f"Image uploaded: {filename}")

        user_rgb = fetch_dominant_color(save_path)
        logger.info(f"Extracted RGB: {user_rgb}")

        closest_yarn_info = colour_match(user_rgb)
        top_rows = closest_yarn_info.head(5)

        session['img'] = filename
        session['top_rows'] = top_rows.to_dict(orient='records')

        return redirect(url_for('colourMatch_tohtml'))

    img = session.get('img')
    top_rows = session.get('top_rows')
    return render_template('colourmatch.html', img=img, top_rows=top_rows)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
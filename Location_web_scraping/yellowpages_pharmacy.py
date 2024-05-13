import pandas as pd
from scraper import scrape_pharmacies
from data_handler import save_to_csv

yellow_pages_url = "https://www.yellowpages.com.au/nsw/chemist-pharmacy-stores-18597-category-{}{}"
alphabets = 'abcdefghijklmnopqrstuvwxyz'
pharmacy_data_all = []

for alphabet in alphabets:
    page = 1
    while True:
        url = yellow_pages_url.format(alphabet, page)
        pharmacy_data = scrape_pharmacies(url)
        if not pharmacy_data:
            break
        pharmacy_data_all.extend(pharmacy_data)
        page += 1

yellow_pages_pharmacy_df = pd.DataFrame(pharmacy_data_all)
save_to_csv(yellow_pages_pharmacy_df, "data/raw/yellow_pages_pharmacy_df.csv")
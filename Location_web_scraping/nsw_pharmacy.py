from scraper import scrape_nsw_pharmacy
from data_handler import save_to_csv

nsw_pharmacy_url = "https://www.health.nsw.gov.au/pharmaceutical/Pages/pharmacy-trial-locations.aspx"
nsw_pharmacy_df, scraping_date = scrape_nsw_pharmacy(nsw_pharmacy_url)

save_to_csv(nsw_pharmacy_df, "data/raw/nsw_pharmacy_df.csv")
print(scraping_date)

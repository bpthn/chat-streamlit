from bs4 import BeautifulSoup
import requests
from checks import check_status
import pandas as pd

def scrape_pharmacies(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    
    if not check_status(response, url):
        return []
    
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        pharmacy_divs = soup.find_all('div', class_='flow-layout inside-gap inside-gap-small vertical')
        
        pharmacy_data = []
        
        for div in pharmacy_divs:
            pharmacy_tags = div.find_all('a', href=True)
            for tag in pharmacy_tags:
                pharmacy_name = tag.get_text(strip=True)
                pharmacy_url = "https://www.yellowpages.com.au" + tag['href']
                response_pharmacy = requests.get(pharmacy_url, headers=headers)
                
                if not check_status(response_pharmacy, pharmacy_url):
                    continue
                
                try:
                    soup_pharmacy = BeautifulSoup(response_pharmacy.text, 'html.parser')
                    address_divs = soup_pharmacy.find_all('div', class_='listing-address mappable-address mappable-address-with-poi')
                    
                    if address_divs:
                        address_info = address_divs[0]
                        address = address_info['data-address-line']
                        latitude = address_info['data-geo-latitude']
                        longitude = address_info['data-geo-longitude']
                    else:
                        address = "Address not found"
                        latitude = "Latitude not found"
                        longitude = "Longitude not found"
                    
                    phone_links = soup_pharmacy.find_all('a', class_='click-to-call contact contact-preferred contact-phone')
                    
                    if phone_links:
                        phone_number = phone_links[0]['href'].split(':')[1]
                    else:
                        phone_number = "Phone number not found"
                    
                    suburb_postal_code = tag.find_next(class_='de-emphasis').get_text(strip=True)
                    suburb, postal_code = suburb_postal_code.rsplit(maxsplit=1)
                    postal_code = ''.join(filter(str.isdigit, postal_code))
                    
                    pharmacy_data.append({'pharmacy_name': pharmacy_name, 'address': address, 'suburb': suburb, 'postal_code': postal_code, 'latitude': latitude, 'longitude': longitude, 'tel': phone_number, 'link_url': pharmacy_url})
                except Exception as e:
                    print(f"Error scraping pharmacy details: {e}")
                    continue
        
        return pharmacy_data
    
    except Exception as e:
        print(f"Error scraping pharmacies page: {e}")
        return []
    
def scrape_nsw_pharmacy(url):
    response = requests.get(url)
    if not check_status(response, url):
        print("Failed to retrieve the webpage:", url)
        return None, None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    if not table:
        print("No table found on the webpage:", url)
        return None, None
    
    headers = [header.text.strip() for header in table.find_all('th')]
    if not headers:
        print("No table headers found on the webpage:", url)
        return None, None
    
    rows = []
    for row in table.find_all('tr')[1:]:
        row_data = [data.text.strip() for data in row.find_all('td')]
        if len(row_data) == len(headers):
            rows.append(row_data)
        else:
            print("Incomplete row data detected on the webpage:", url)
    
    if not rows:
        print("No valid row data found on the webpage:", url)
        return None, None
    
    nsw_trial_df = pd.DataFrame(rows, columns=headers)
    nsw_trial_df = nsw_trial_df.sort_values(by='Suburb', ignore_index=True)
    
    scraping_date_element = soup.find('div', class_='lastupdated')
    scraping_date = scraping_date_element.text.replace('Current as at: ', '').strip() if scraping_date_element else "Unknown"
    
    return nsw_trial_df, scraping_date
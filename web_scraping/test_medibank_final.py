from selenium import webdriver
from selenium.webdriver import ActionChains , DesiredCapabilities
from selenium.webdriver.chrome.service import Service 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import bs4
import pandas as pd
import re

options = Options()
options.add_argument("--headless")
options.add_experimental_option("detach",True) #fix  Automatically & Immediately After Test Without Calling Quit or Close
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.medibank.com.au/overseas-health-insurance/oshc/comprehensive-oshc/")

        
        
data = driver.page_source
soup = bs4.BeautifulSoup(data, 'html.parser')

services = soup.find_all('span', {'class': 'service-name'})
details = soup.find_all('div', {'id': lambda x: x and x.startswith('hospitalinclusion')})

service_names = []
service_details = []

for service in services:
    # Extract text content from <span> and <div> elements and strip any leading/trailing whitespace
    service_name = service.text.strip()
    # print(service)
    # print(service_name)
    service_names.append(service_name)
    

for detail in details:
    detail.find('div', {'class': 'd-md-none m-t-2'}).decompose()
    p_tags = detail.find_all('p')
    # print(p_tags)
    service_detail = ' '.join([p.get_text(separator=' ', strip=True) for p in p_tags])
    service_details.append(service_detail)
    # print(service_detail)


service_data = pd.DataFrame({
    'services':service_names,
    'details':service_details
    })

service_data.to_csv('medibank.csv')
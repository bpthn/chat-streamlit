import requests
from bs4 import BeautifulSoup
import csv

def scrape_faq(url):
    # Define headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Send a GET request to the URL with headers
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all FAQ sections
        faq_sections = soup.find_all('div', class_='css-p5vfr4')
        
        # Prepare list to hold question-answer pairs
        faq_data = []
        
        # Iterate over each FAQ section and extract the question and answer
        for faq_section in faq_sections:
            question_element = faq_section.find('h3', class_='MuiTypography-root MuiTypography-subheadingLg rds-component css-7pwa1y')
            question = question_element.text.strip() if question_element else "Question not found"
            
            answer_element = faq_section.find('div', class_='MuiCollapse-wrapperInner MuiCollapse-vertical css-8atqhb')
            answer = answer_element.text.strip() if answer_element else "Answer not found"
            
            faq_data.append([question, answer])
        
        # Save the data to a CSV file
        csv_filename = "faq_data_bupa.csv"
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Question", "Answer"])  # Write header row
            writer.writerows(faq_data)  # Write data rows
        
        print("Data saved to", csv_filename)
    else:
        print("Failed to retrieve the webpage.")

# URL of the page containing the FAQs
url = "https://www.bupa.com.au/health-insurance/oshc/faqs"

# Call the function to scrape FAQs from the URL and save them to a CSV file
scrape_faq(url)

import requests
from bs4 import BeautifulSoup
import csv

def scrape_faq(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all FAQ sections
        faq_sections = soup.find_all('div', class_='accordion-panel')
        
        # Prepare list to hold question-answer pairs
        faq_data = []
        
        # Iterate over each FAQ section and extract the question and answer
        for faq_section in faq_sections:
            question_element = faq_section.find_previous_sibling('div', class_='accordion-header').find('a', class_='collapse-toggle')
            question = question_element.text.strip() if question_element else "Question not found"
            answer = faq_section.find('div', class_='collapse-inner').text.strip()
            faq_data.append([question, answer])
        
        # Save the data to a CSV file
        csv_filename = "faq_data.csv"
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Question", "Answer"])  # Write header row
            writer.writerows(faq_data)  # Write data rows
        
        print("Data saved to", csv_filename)
    else:
        print("Failed to retrieve the webpage.")

# URL of the page containing the FAQs
url = "https://www.medibank.com.au/overseas-health-insurance/oshc/faqs/"

# Call the function to scrape FAQs from the URL and save them to a CSV file
scrape_faq(url)



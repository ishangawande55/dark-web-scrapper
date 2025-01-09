from bs4 import BeautifulSoup
import requests
from src.tor_controller import set_tor_proxy
import logging
from src.utils import save_to_csv


# Set up logging
logging.basicConfig(filename='logs/scraper.log', level=logging.INFO)

def scrape_website(url):
    session = set_tor_proxy()
    try:
        response = session.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        logging.info(f"Successfully fetched {url}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def extract_links(soup):
    links = soup.find_all('a', href=True)
    extracted_links = [link['href'] for link in links]
    return extracted_links

def scrape_website_and_save(url):
    soup = scrape_website(url)
    if soup:
        links = extract_links(soup)
        for link in links:
            save_to_csv([link])  # Store each link in CSV
        print(f"Data saved to CSV for {url}")
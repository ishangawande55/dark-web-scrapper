import tkinter as tk
from tkinter import scrolledtext
import requests
from stem import Signal
from stem.control import Controller
import time
import logging
import threading

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up the Tor proxy session
def set_tor_proxy():
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    return session

# Request to a .onion site with retries and backoff
def fetch_onion_data(url, session, retries=3):
    for attempt in range(retries):
        try:
            logging.info(f"Attempt {attempt + 1} to fetch data from {url}...")
            
            # Send request to the .onion site
            response = session.get(url, timeout=20)
            
            # Check the status code
            if response.status_code == 200:
                logging.info(f"Successfully fetched data from {url}.")
                try:
                    # Try parsing the response as JSON
                    data = response.json()
                    return data
                except ValueError:
                    # If response isn't JSON, log raw content
                    logging.error(f"Error: Response is not valid JSON. Raw response: {response.text}")
                    return response.text  # Return raw response
            else:
                logging.error(f"Error: Received status code {response.status_code}")
                time.sleep(2 * (attempt + 1))  # Exponential backoff before retrying
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred: {e}")
            time.sleep(2 * (attempt + 1))  # Exponential backoff before retrying

    logging.error(f"Failed to fetch data from {url} after {retries} attempts.")
    return None

# Change Tor IP by sending a signal to Tor
def change_tor_ip():
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            logging.info("IP address changed.")
    except Exception as e:
        logging.error(f"Error changing IP: {e}")

# GUI logic to interact with the scraper
class DarkWebScraperGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Dark Web Scraper")
        self.geometry("600x400")
        
        # Label to show status messages
        self.status_label = tk.Label(self, text="Enter the .onion URL and start scraping.", anchor="w")
        self.status_label.pack(pady=10, padx=10)
        
        # Entry for .onion URL
        self.url_entry = tk.Entry(self, width=50)
        self.url_entry.pack(pady=10)
        self.url_entry.insert(0, "http://jgwe5cjqdbyvudjqskaajbfibfewew4pndx52dye7ug3mt3jimmktkid.onion/")
        
        # Scraped Data Display (ScrolledText widget)
        self.text_area = scrolledtext.ScrolledText(self, width=70, height=15)
        self.text_area.pack(pady=10, padx=10)
        
        # Scrape Button
        self.scrape_button = tk.Button(self, text="Scrape Data", command=self.scrape_data)
        self.scrape_button.pack(pady=5)
        
        # Change IP Button
        self.change_ip_button = tk.Button(self, text="Change IP", command=self.change_ip)
        self.change_ip_button.pack(pady=5)
    
    def scrape_data(self):
        url = self.url_entry.get().strip()
        if url:
            # Set up the Tor proxy session
            session = set_tor_proxy()
            self.status_label.config(text="Scraping data, please wait...")
            
            # Start the scraping task in a new thread
            threading.Thread(target=self._scrape_data, args=(url, session)).start()
        else:
            self.status_label.config(text="Please enter a valid .onion URL.")
    
    def _scrape_data(self, url, session):
        # Try to fetch data from the .onion site
        data = fetch_onion_data(url, session)
        
        # Update GUI in the main thread
        if data:
            self.text_area.delete(1.0, tk.END)  # Clear any previous content
            self.text_area.insert(tk.END, data)  # Display the raw response
            self.status_label.config(text="Data scraped successfully.")
        else:
            self.status_label.config(text="Failed to scrape data.")
    
    def change_ip(self):
        self.status_label.config(text="Changing IP address, please wait...")
        change_tor_ip()
        self.status_label.config(text="IP address changed.")

# Run the GUI application
if __name__ == "__main__":
    app = DarkWebScraperGUI()
    app.mainloop()
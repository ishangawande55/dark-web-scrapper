import csv
import logging

# Save data to CSV
def save_to_csv(data, file_name='data/scraped_data.csv'):
    try:
        with open(file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
    except Exception as e:
        logging.error(f"Failed to save data to {file_name}: {e}")
#!/usr/bin/env python3

import csv
import time
import pathlib
import datetime
import requests
import multiprocessing

from colorama import init
from termcolor import colored

# Interval to collect data every 30 minutes
SLEEP_SECS = 60 * 30

def main():
    # Initialize colorama for colored terminal output
    init()

    print(colored(f"Starting the monitoring loop. Collecting data every {SLEEP_SECS} seconds.", "blue"))
    
    # Load URLs from the specified file
    urls = load_urls("urls.txt")
    print(colored(f"Loaded {len(urls)} URLs from urls.txt.", "blue"))

    # Check if the CSV file already exists to determine if the header is needed
    needs_header = not pathlib.Path("data.csv").is_file()
    
    # Open the CSV file for appending
    with open("data.csv", "a", newline='') as fh:
        print(colored(f"Opened data.csv for appending.", "blue"))
        # Create a CSV DictWriter object with the specified fieldnames
        data_writer = csv.DictWriter(fh, fieldnames=["run", "time", "url", "error"])

        # Write the header if needed
        if needs_header:
            print(colored(f"Writing header to data.csv.", "blue"))
            data_writer.writeheader()

        # Enter the main monitoring loop
        while True:
            # Ensure CSV file is up to date by flushing it after each run
            print(colored(f"Flushing data to data.csv.", "blue"))
            fh.flush()

            # Record the start time of the run
            started = datetime.datetime.now()

            # Create a pool of 50 processes to check the URLs concurrently
            with multiprocessing.Pool(50) as pool:
                print(colored(f"{started} checking {len(urls)} URLs", "yellow"))
                # Map the check function to the list of URLs and process results
                for result in pool.map(check, urls):
                    if result:
                        result["run"] = started.isoformat()
                        data_writer.writerow(result)

            # Calculate the elapsed time for the run
            elapsed = datetime.datetime.now() - started
            print(colored(f"Completed run starting at {started}. Total time elapsed: {elapsed.total_seconds()} seconds.", "blue"))
            
            # Sleep for the remaining interval if the run completed faster than SLEEP_SECS
            if elapsed.total_seconds() < SLEEP_SECS:
                t = SLEEP_SECS - elapsed.total_seconds()
                print(colored(f"Sleeping for {t} seconds before the next run.", "yellow"))
                time.sleep(t)

def load_urls(file_path):
    """Load URLs from the given file path and return them as a list."""
    with open(file_path) as f:
        return f.read().splitlines()

def check(url):
    """Check the given URL and return a dictionary with error details if any."""
    try:
        # Attempt to get the URL with a timeout of 30 seconds
        resp = requests.get(url, timeout=30)
        print(colored(f"Successfully checked URL: {url}", "green"))
        return None
    except Exception as e:
        # Catch any exceptions and return error details
        print(colored(f"Caught exception for URL: {url}, error: {str(e)}", "red"))
        return {
            "time": datetime.datetime.now().isoformat(),
            "url": url,
            "error": str(e)
        }

if __name__ == "__main__":
    main()

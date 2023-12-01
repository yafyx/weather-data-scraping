# Weather Data Scraper

## Overview

The Weather Data Scraper is a Python script designed to extract historical weather data from the timeanddate.com website for a specific location. The script utilizes web scraping techniques to gather information from the historical weather tables and organizes the data into a CSV file for further analysis.

## Features

- Extracts historical weather data, including temperature, wind speed, humidity, barometric pressure, and visibility.
- Saves the collected data in a CSV file for easy analysis

## Usage

To use the Weather Data Scraper, follow these steps:

1. Install the required Python packages by running the following command:

   ```bash
   pip install requests beautifulsoup4
   ```

2. Copy and paste the provided script into a Python file (e.g., `weather_scraper.py`).

3. Replace the value of the `country`, `city`, `month` and `year` variables with the desired values.

   ```python
   country = "Your Country"
   city = "Your City"
   month = "November"
   year = "2023"
   ```

4. Run the script:

   ```bash
   python weather_scraper.py
   ```

   The script will generate a CSV file named `weather_data.csv` in the same directory as the script.

## Disclaimer

This script is for learning and fun only. Make sure you follow the rules of any website you use this script on. The script might need tweaks if the timeanddate.com website changes.

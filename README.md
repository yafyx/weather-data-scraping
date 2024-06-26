# Time and Date Weather Scraping

Extract historical weather data from the timeanddate.com website for a specific location. The script uses web scraping techniques to collect information from historical weather tables and organizes the data into a CSV file for further analysis.

## Features

- Extracts historical weather data, including temperature, wind speed, humidity, barometric pressure, and visibility.
- Saves the collected data in a CSV file for easy analysis.

## Usage

To use the Weather Data Scraper, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/yafyx/weather-data-scraping.git
   ```

1. Install the required Python packages by running the following command:

   ```bash
   pip install -r requirements.txt
   ```

1. Replace the value of the `country`, `city`, `month` and `year` variables with the desired values.

   ```python
   country = # Your Country
   city = # Your City
   month = # Your Month (in number format)
   year = # Your Year (in number format)
   ```

1. Run the script:

   The script will save the scraped data into a CSV file named `<country>_<city>_weather_dataset.csv` in the same directory.

## Contributing

Feel free to submit issues or pull requests. Contributions are welcome!

## Disclaimer

This script is for learning and fun only. Make sure you follow the rules of any website you use this script on. The script might need tweaks if the timeanddate.com website changes.

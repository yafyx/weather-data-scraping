import csv
import os
import re

import requests
from bs4 import BeautifulSoup

TABLE_ID = "wt-his"
SELECT_ID = "wt-his-select"
BASE_URL = "https://www.timeanddate.com/weather/{}/{}/historic?month={:02d}&year={}"
HEADERS = {"User-Agent": "Mozilla/5.0"}
TEMP_UNIT = "°C"
WIND_UNIT = " km/h"
HUMIDITY_UNIT = "%"
BAROMETER_UNIT = " mbar"
VISIBILITY_UNIT = "km"


def remove_non_breaking_spaces(data: list) -> list:
    """Remove non-breaking spaces from a list of strings."""
    return [re.sub("\xa0", "", item).strip() for item in data if item]


def get_soup(url: str) -> BeautifulSoup:
    """Fetch and parse HTML content from the given URL."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None


def extract_table_data(table) -> list:
    """Extract weather data from the HTML table."""
    table_data = [
        [[i.text for i in c.find_all("th")], *[i.text for i in c.find_all("td")]]
        for c in table.find_all("tr")
    ]
    return table_data


def get_weather_data(country: str, city: str, month: int, year: int) -> dict:
    """Scrape weather data from the specified location and date."""
    url = BASE_URL.format(country.lower(), city.lower(), month, year)
    page_soup = get_soup(url)
    if not page_soup:
        return {}

    table = page_soup.find("table", {"id": TABLE_ID})
    select = page_soup.find("select", {"id": SELECT_ID})
    if not table or not select:
        print("Required HTML elements not found.")
        return {}

    options = select.find_all("option")
    data = {}
    for option in options:
        option_value = option["value"]
        option_text = option.text.strip()
        select["value"] = option_value
        table_data = extract_table_data(table)
        if len(table_data) < 2:
            continue
        headers = remove_non_breaking_spaces(table_data[1])
        headers.insert(4, "Direction")
        data[option_text] = [
            dict(zip(headers, remove_non_breaking_spaces([a, *i])))
            for [[a], *i] in table_data[2:]
        ]

    return data


def clean_data(data: dict) -> list:
    """Clean and format the weather data."""
    csv_data = []
    for _, option_data in data.items():
        for row in option_data:
            csv_row = {}
            for key, value in row.items():
                value = re.sub(r"\s+", " ", value.strip()).split(":")[0]
                if key == "Temp":
                    value = value.replace(TEMP_UNIT, "")
                elif key == "Wind":
                    value = value.replace(WIND_UNIT, "").replace("No wind", "")
                elif key == "Humidity":
                    value = value.replace(HUMIDITY_UNIT, "")
                elif key == "Barometer":
                    value = value.replace(BAROMETER_UNIT, "")
                elif key == "Visibility":
                    value = value.replace(VISIBILITY_UNIT, "")
                csv_row[key] = value
            csv_data.append(csv_row)
    return csv_data


def save_to_csv(data: list, file_path: str):
    """Save the weather data to a CSV file."""
    if not data:
        print("No data to save.")
        return

    try:
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"Data saved successfully to {file_path}")
    except IOError as e:
        print(f"Failed to save data: {e}")


def main():
    country = "indonesia"
    city = "jakarta"
    month = 11
    year = 2023

    weather_data = get_weather_data(country, city, month, year)
    if not weather_data:
        print("Failed to retrieve weather data.")
        return

    csv_data = clean_data(weather_data)
    csv_file_path = os.path.join(
        os.path.dirname(__file__), f"{country}_{city}_weather_dataset.csv"
    )
    save_to_csv(csv_data, csv_file_path)


if __name__ == "__main__":
    main()

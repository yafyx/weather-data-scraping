import csv
import os
import re

import requests
from bs4 import BeautifulSoup as soup

TABLE_ID = "wt-his"
SELECT_ID = "wt-his-select"
BASE_URL = "https://www.timeanddate.com/weather/{}/{}/historic?month={:02d}&year={}"


def remove_non_breaking_spaces(data: list) -> list:
    return list(filter(None, [re.sub("\xa0", "", item) for item in data]))


def get_soup(url: str) -> soup:
    response = requests.get(url)
    response.raise_for_status()
    return soup(response.text, "html.parser")


def get_weather_data(country: str, city: str, month: int, year: int) -> dict:
    url = BASE_URL.format(country.lower(), city.lower(), month, year)
    page_soup = get_soup(url)
    table = page_soup.find("table", {"id": TABLE_ID})
    select = page_soup.find("select", {"id": SELECT_ID})
    options = select.find_all("option")

    data = {}
    for option in options:
        option_value = option["value"]
        option_text = option.text.strip()
        select["value"] = option_value
        table_data = [
            [[i.text for i in c.find_all("th")], *[i.text for i in c.find_all("td")]]
            for c in table.find_all("tr")
        ]
        [h1], [h2], *option_data, _ = table_data
        h2 = remove_non_breaking_spaces(h2)
        h2.insert(4, "Direction")
        data[option_text] = [
            dict(zip(h2, remove_non_breaking_spaces([a, *i])))
            for [[a], *i] in option_data
        ]

    return data


def clean_data(data: dict) -> list:
    csv_data = []
    for _, option_data in data.items():
        for row in option_data:
            csv_row = {}
            for key, value in row.items():
                value = re.sub(r"\s+", " ", value.strip())
                value = value.split(":")[0]
                if key == "Temp":
                    value = value.replace("°C", "")
                elif key == "Wind":
                    value = value.replace(" km/h", "")
                    if value == "No wind":
                        value = ""
                elif key == "Humidity":
                    value = value.replace("%", "")
                elif key == "Barometer":
                    value = value.replace(" mbar", "")
                elif key == "Visibility":
                    value = value.replace("km", "")
                csv_row[key] = value
            csv_data.append(csv_row)
    return csv_data


def save_to_csv(data: list, file_path: str):
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


country = "indonesia"
city = "jakarta"
month = 11
year = 2023

weather_data = get_weather_data(country, city, month, year)
csv_data = clean_data(weather_data)
csv_file_path = os.path.join(os.path.dirname(__file__), "test.csv")
save_to_csv(csv_data, csv_file_path)

print("Data saved successfully to", csv_file_path)

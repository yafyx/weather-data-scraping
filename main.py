import csv
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup as soup

TABLE_ID = "wt-his"
BASE_URL = (
    "https://www.timeanddate.com/weather/{}/{}/historic?month={:02d}&year={}&hd={}"
)
HEADERS = {"User-Agent": "Mozilla/5.0"}
TEMP_UNIT = "°C"
WIND_UNIT = " km/h"
HUMIDITY_UNIT = "%"
BAROMETER_UNIT = " mbar"
VISIBILITY_UNIT = "km"


def remove_non_breaking_spaces(data: list) -> list:
    return list(filter(None, [re.sub("\xa0", "", item) for item in data]))


def get_soup(url: str) -> soup:
    with requests.Session() as session:
        response = session.get(url, headers=HEADERS)
        response.raise_for_status()
        return soup(response.text, "html.parser")


def get_weather_data(country: str, city: str, month: int, year: int) -> dict:
    data = {}
    for day in range(1, 32):
        try:
            date = datetime(year, month, day)
        except ValueError:
            break

        date_str = date.strftime("%Y%m%d")
        url = BASE_URL.format(country.lower(), city.lower(), month, year, date_str)

        try:
            page_soup = get_soup(url)
        except requests.HTTPError as e:
            print(f"Failed to get data for {date_str}: {e}")
            continue

        table = page_soup.find("table", {"id": TABLE_ID})
        if not table:
            print(f"No data available for {date_str}")
            continue

        table_data = [
            [[i.text for i in c.find_all("th")], *[i for i in c.find_all("td")]]
            for c in table.find_all("tr")
        ]
        if not table_data:
            continue

        [h1], [h2], *option_data, _ = table_data
        h2 = remove_non_breaking_spaces(h2)
        h2.insert(4, "Direction")
        data[date_str] = [
            dict(
                zip(h2, remove_non_breaking_spaces([a, *[get_td_text(td) for td in i]]))
            )
            for [[a], *i] in option_data
        ]

    return data


def get_td_text(td):
    span = td.find("span")
    if span and "title" in span.attrs:
        return span["title"]
    else:
        return td.text.strip()


def clean_data(data: dict) -> list:
    csv_data = []
    for date, option_data in data.items():
        day = date[-2:]
        for row in option_data:
            csv_row = {"Day": day}
            for key, value in row.items():
                value = re.sub(r"\s+", " ", value.strip())
                value = value.split(":")[0]
                if key == "Temp":
                    value = value.replace(TEMP_UNIT, "")
                elif key == "Wind":
                    value = value.replace(WIND_UNIT, "")
                    if value == "No wind":
                        value = ""
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
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print("Data saved successfully to", file_path)
    except IOError as e:
        print(f"Failed to save data: {e}")


def main():
    country = "indonesia"
    city = "jakarta"
    month = 11
    year = 2023

    weather_data = get_weather_data(country, city, month, year)
    csv_data = clean_data(weather_data)
    csv_file_path = os.path.join(
        os.path.dirname(__file__), f"{country}_{city}_weather_dataset.csv"
    )
    save_to_csv(csv_data, csv_file_path)


if __name__ == "__main__":
    main()

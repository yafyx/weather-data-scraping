import contextlib
import csv
import os
import re
import sys
import typing

import requests
from bs4 import BeautifulSoup as soup


def _remove(d: list) -> list:
    return list(filter(None, [re.sub("\xa0", "", b) for b in d]))


@contextlib.contextmanager
def get_weather_data(url: str, by_url=True) -> typing.Generator[dict, None, None]:
    d = soup(requests.get(url).text if by_url else url, "html.parser")
    _table = d.find("table", {"id": "wt-his"})
    _select = d.find("select", {"id": "wt-his-select"})
    _options = _select.find_all("option")

    data = {}
    for option in _options:
        option_value = option["value"]
        option_text = option.text.strip()
        _select["value"] = option_value
        _data = [
            [[i.text for i in c.find_all("th")], *[i.text for i in c.find_all("td")]]
            for c in _table.find_all("tr")
        ]
        [h1], [h2], *option_data, _ = _data
        _h2 = _remove(h2)
        _h2.insert(4, "Direction")
        data[option_text] = [
            dict(zip(_h2, _remove([a, *i]))) for [[a], *i] in option_data
        ]

    yield data


sys.stdout.reconfigure(encoding="utf-8")

with get_weather_data(
    "https://www.timeanddate.com/weather/indonesia/jakarta/historic?month=07&year=2023"
) as weather:
    # print(weather)
    csv_data = []
    for option_text, option_data in weather.items():
        for data in option_data:
            csv_row = []
            for key, value in data.items():
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
                csv_row.append(value)
            csv_data.append(csv_row)

    csv_file_path = os.path.join(os.path.dirname(__file__), "weather_data.csv")
    with open(csv_file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(list(data.keys()))
        writer.writerows(csv_data)

    print("Data saved successfully to", csv_file_path)

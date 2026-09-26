import os
import json
import folium
import requests
from geopy import distance
from dotenv import load_dotenv
from flask import Flask, render_template


def get_coordinates(apikey, address):
    url = "https://geocode-maps.yandex.ru/1.x"
    params = {
        "geocode": address,
        "apikey": apikey,
        "format": "json"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    geo_objects = response.json()['response']['GeoObjectCollection']['featureMember']

    if not geo_objects:
        return None

    location = geo_objects[0]['GeoObject']['Point']['pos']
    longitude, latitude = location.split(" ")
    return latitude, longitude


def json_reading(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def get_distance(user_cords, data):
    stations = []
    for station_info in data:
        place = station_info["latitude"], station_info["longitude"]
        formated_data = {
            "title": station_info["name"],
            "distance": distance.distance(user_cords, place).km,
            "latitude": station_info["latitude"],
            "longitude": station_info["longitude"]
        }
        stations.append(formated_data)
    return stations


def get_map(data, user_cords):
    m = folium.Map(
        location=user_cords,
        zoom_start=12,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012"
    )

    for marker in data:
        folium.Marker(
            location=[marker["latitude"], marker["longitude"]],
            tooltip="Click me!",
            popup=marker["title"],
            icon=folium.Icon(color="green"),
        ).add_to(m)
    os.makedirs("templates", exist_ok=True)
    m.save("templates/index.html")


def station_map():
    return render_template("index.html")


def main():
    load_dotenv()
    data = json_reading("charging_stations_by.json")
    apikey = os.getenv("API_KEY")
    address = input("Где вы находитесь?: ")
    user_cords = get_coordinates(apikey, address)
    sorted_list = sorted(get_distance(user_cords, data), key=lambda x: x["distance"])[:15]
    get_map(sorted_list, user_cords)
    app = Flask(__name__)
    app.add_url_rule('/', 'station_map', station_map)
    app.run('0.0.0.0')


if __name__ == "__main__":
    main()
"""Weather Service for O2C AI Monitor"""
import requests
from datetime import datetime


class WeatherService:
    """Fetches weather data from OpenWeatherMap (current) and Open-Meteo (historical)"""

    OWM_URL = "https://api.openweathermap.org/data/2.5/weather"
    METEO_HIST_URL = "https://archive-api.open-meteo.com/v1/archive"
    
    WEATHER_CODES = {
        0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
        45: "fog", 48: "icy fog",
        51: "light drizzle", 53: "moderate drizzle", 55: "heavy drizzle",
        61: "light rain", 63: "moderate rain", 65: "heavy rain",
        71: "light snow", 73: "moderate snow", 75: "heavy snow",
        80: "light showers", 81: "moderate showers", 82: "heavy showers",
        95: "thunderstorm", 96: "thunderstorm with hail",
    }
    
    WEATHER_MAIN = {
        **{k: "Clear" for k in [0, 1]},
        **{k: "Clouds" for k in [2, 3]},
        **{k: "Fog" for k in [45, 48]},
        **{k: "Drizzle" for k in [51, 53, 55]},
        **{k: "Rain" for k in [61, 63, 65, 80, 81, 82]},
        **{k: "Snow" for k in [71, 73, 75]},
        **{k: "Thunderstorm" for k in [95, 96]},
    }

    def __init__(self, api_key: str, cities: dict):
        self.api_key = api_key
        self.cities = cities

    def fetch_current(self) -> list:
        """Fetch live weather for all cities via OpenWeatherMap"""
        print("🌤️  Fetching current weather (OpenWeatherMap)...")
        results = []
        for city, coords in self.cities.items():
            print(f"   📍 {city:<15}", end=" ")
            rec = self._owm_one(city, coords)
            if rec:
                results.append(rec)
        return results

    def fetch_historical(self, date: str) -> list:
        """Fetch historical weather via Open-Meteo (free, no key)"""
        print(f"📅 Fetching historical weather for {date} (Open-Meteo)...")
        results = []
        for city, coords in self.cities.items():
            print(f"   📍 {city:<15}", end=" ")
            rec = self._meteo_one(city, coords, date)
            if rec:
                results.append(rec)
        return results

    def _owm_one(self, city: str, coords: dict) -> dict:
        """Fetch one city from OpenWeatherMap"""
        try:
            r = requests.get(self.OWM_URL, params={
                "lat": coords["lat"],
                "lon": coords["lon"],
                "appid": self.api_key,
                "units": "metric"
            }, timeout=10)
            r.raise_for_status()
            data = r.json()
            
            rec = {
                "city_name": city,
                "state": coords.get("state"),
                "recorded_at": datetime.now().isoformat(),
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "temp_min": data["main"]["temp_min"],
                "temp_max": data["main"]["temp_max"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "visibility_km": data.get("visibility", 10000) / 1000,
                "cloudiness": data["clouds"]["all"],
                "weather_main": data["weather"][0]["main"],
                "weather_description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"].get("deg", 0),
                "rain_1h": data.get("rain", {}).get("1h", 0),
                "snow_1h": data.get("snow", {}).get("1h", 0),
                "data_source": "OpenWeatherMap"
            }
            print(f"✅ {rec['temperature']}°C  {rec['weather_description']}")
            return rec
        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            return None

    def _meteo_one(self, city: str, coords: dict, date: str) -> dict:
        """Fetch one city from Open-Meteo historical"""
        try:
            r = requests.get(self.METEO_HIST_URL, params={
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "start_date": date,
                "end_date": date,
                "hourly": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
                "timezone": "auto"
            }, timeout=10)
            r.raise_for_status()
            data = r.json()["hourly"]
            
            # Take noon values (index 12)
            idx = 12 if len(data["time"]) > 12 else 0
            rec = {
                "city_name": city,
                "state": coords.get("state"),
                "recorded_at": data["time"][idx],
                "temperature": data["temperature_2m"][idx],
                "feels_like": data["temperature_2m"][idx],
                "temp_min": min(data["temperature_2m"]),
                "temp_max": max(data["temperature_2m"]),
                "humidity": data["relative_humidity_2m"][idx],
                "pressure": 1013,
                "visibility_km": 10,
                "cloudiness": 0,
                "weather_main": self.WEATHER_MAIN.get(data["weather_code"][idx], "Clear"),
                "weather_description": self.WEATHER_CODES.get(data["weather_code"][idx], "clear"),
                "wind_speed": data["wind_speed_10m"][idx],
                "wind_direction": 0,
                "rain_1h": data["precipitation"][idx],
                "snow_1h": 0,
                "data_source": "Open-Meteo"
            }
            print(f"✅ {rec['temperature']}°C  {rec['weather_description']}")
            return rec
        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            return None
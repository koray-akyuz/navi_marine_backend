import httpx
import os

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

async def get_weather_data(lat: float, lon: float):
    print(f"DEBUG: Weather request for Lat: {lat}, Lon: {lon}")
    if not OPENWEATHER_API_KEY:
        print("DEBUG ERROR: OPENWEATHER_API_KEY is not set!")
        return None

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=tr"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        print(f"DEBUG: OpenWeatherMap Response Status: {response.status_code}")
        if response.status_code != 200:
            print(f"DEBUG ERROR: OpenWeatherMap API details: {response.text}")
            return None
        
        data = response.json()
        return {
            "temp": data["main"]["temp"],
            "pressure": data["main"]["pressure"], # Balık aktivitesi için kritik
            "wind_speed": data["wind"]["speed"],
            "wind_deg": data["wind"]["deg"],      # Rüzgar yönü (derece)
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"]
        }

def get_wind_name(deg: int):
        # Türk balıkçı terminolojisi
        if 337.5 <= deg <= 360 or 0 <= deg <= 22.5: return "Yıldız (K)"
        if 22.5 < deg < 67.5: return "Poyraz (KD)"
        if 67.5 <= deg <= 112.5: return "Gündoğusu (D)"
        if 112.5 < deg < 157.5: return "Keşişleme (GD)"
        if 157.5 <= deg <= 202.5: return "Kıble (G)"
        if 202.5 < deg < 247.5: return "Lodos (GB)"
        if 247.5 <= deg <= 292.5: return "Günbatısı (B)"
        if 292.5 < deg < 337.5: return "Karayel (KB)"
        return "Değişken"

async def get_marine_weather(lat: float, lon: float):
    # Marine API: Dalga ve deniz verileri için
    # Forecast API: Rüzgar ve hava durumu için
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m", "is_day", "precipitation", "wind_speed_10m", "wind_direction_10m", "pressure_msl"],
        "wind_speed_unit": "ms", # m/s (denizciler knots da sever, 'kn' yapılabilir)
        "timezone": "auto"
    }


    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            return None
        
        data = response.json()["current"]
        wind_name = get_wind_name(data["wind_direction_10m"])
        return {
            "temp": data["temperature_2m"],
            "wind_speed": data["wind_speed_10m"],
            "wind_deg": data["wind_direction_10m"],
            "pressure": data["pressure_msl"],
            "is_day": data["is_day"],
            "wind_name" : wind_name
        }

async def get_wind_grid(min_lat, max_lat, min_lon, max_lon, steps=5):
    # Izgarayı oluştur (float olarak sakla, API'ye string gönder)
    lat_step = (max_lat - min_lat) / steps
    lon_step = (max_lon - min_lon) / steps
    
    lats = []
    lons = []
    for i in range(steps + 1):
        for j in range(steps + 1):
            lats.append(min_lat + i * lat_step)
            lons.append(min_lon + j * lon_step)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": ",".join(str(lat) for lat in lats),
        "longitude": ",".join(str(lon) for lon in lons),
        "current": "wind_speed_10m,wind_direction_10m",  # liste değil string
        "wind_speed_unit": "kn",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        # API bazen tek dict, bazen liste döner — normalize et
        if isinstance(data, dict):
            data = [data]
        
        grid_data = []
        for idx, item in enumerate(data):
            if idx >= len(lats):
                break
            current = item.get("current", {})
            grid_data.append({
                "lat": lats[idx],
                "lon": lons[idx],
                "speed": current.get("wind_speed_10m", 0),
                "deg": current.get("wind_direction_10m", 0)
            })
        return grid_data
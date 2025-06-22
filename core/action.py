import math
import requests
from datetime import datetime, timedelta, timezone

class Point:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    meters = R * c 
    km = meters / 1000.0

    return round(km, 3)

def get_candidate_places(epicenter, radius_km):
    radius_m = radius_km * 1000

    query = f"""
    [out:json];
    (
      node["leisure"="park"](around:{radius_m},{epicenter.lat},{epicenter.lon});
      node["amenity"="school"](around:{radius_m},{epicenter.lat},{epicenter.lon});
      node["leisure"="stadium"](around:{radius_m},{epicenter.lat},{epicenter.lon});
      node["amenity"="hospital"](around:{radius_m},{epicenter.lat},{epicenter.lon});
      node["amenity"="fire_station"](around:{radius_m},{epicenter.lat},{epicenter.lon});
    );
    out body;
    """

    url = "https://overpass-api.de/api/interpreter"
    response = requests.post(url, data={"data": query})
    response.raise_for_status()
    data = response.json()

    candidates = []
    for element in data.get("elements", []):
        lat = element.get("lat")
        lon = element.get("lon")
        name = element.get("tags", {}).get("name", "Unknown Place")
        if lat is not None and lon is not None:
            candidates.append({
                "lat": lat,
                "lon": lon,
                "name": name
            })

    return candidates

def fetch_earthquake_data(lat, lon, radius_km=100, min_magnitude=2.5, hours=24):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)
    
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "latitude": lat,
        "longitude": lon,
        "maxradiuskm": radius_km,
        "minmagnitude": min_magnitude,
        "starttime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "endtime": end_time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    earthquakes = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [])
        if len(coords) >= 2:
            earthquake_info = {
                "longitude": coords[0],
                "latitude": coords[1],
                "magnitude": props.get("mag"),
                "time": datetime.utcfromtimestamp(props.get("time") / 1000).isoformat() if props.get("time") else None,
                "place": props.get("place")
            }
            earthquakes.append(earthquake_info)
    
    return earthquakes

def get_user_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        loc = data.get("loc")
        if loc:
            lat_str, lon_str = loc.split(",")
            return float(lat_str), float(lon_str)
    except Exception as e:
        print("Could not get location automatically:", e)
    
    lat = float(input("Enter your latitude: "))
    lon = float(input("Enter your longitude: "))
    return lat, lon

def find_safe_places(epicenter, magnitude, user_location):
    sigma = magnitude * 5
    zones = {
        "red": sigma,
        "yellow": 2 * sigma,
        "green": 3 * sigma
    }

    candidates = get_candidate_places(epicenter, zones["green"] * 3)

    safe_places = []
    
    for place in candidates:
        dist_to_epicenter = haversine(epicenter.lat, epicenter.lon, place['lat'], place['lon'])
        dist_to_user = haversine(user_location.lat, user_location.lon, place['lat'], place['lon'])
        safety_score = 1 - math.exp(- (dist_to_epicenter**2) / (2 * sigma**2))

        if dist_to_epicenter <= zones["red"]:
            zone_color = "red"
        elif dist_to_epicenter <= zones["yellow"]:
            zone_color = "yellow"
        elif dist_to_epicenter <= zones["green"]:
            zone_color = "green"
        else:
            continue

        safe_places.append({
            "place": place,
            "dist_to_user": dist_to_user,
            "safety_score": safety_score,
            "zone": zone_color
        })

    safe_places_sorted = sorted(
        safe_places,
        key=lambda x: (x["zone"] != "green", x["zone"] != "yellow", x["dist_to_user"])
    )
    return safe_places_sorted

def run_quake_safety():
    lat, lon = get_user_location()
    user_location = Point(lat, lon)

    earthquakes = fetch_earthquake_data(lat, lon, radius_km=100, min_magnitude=3, hours=24)
    if not earthquakes:
        return {
            "status": "no_quakes",
            "message": "No recent earthquakes detected nearby."
        }

    epicenter_eq = max(earthquakes, key=lambda e: e['magnitude'])
    epicenter = Point(epicenter_eq['latitude'], epicenter_eq['longitude'])
    magnitude = epicenter_eq['magnitude']

    safe_places = find_safe_places(epicenter, magnitude, user_location)

    return {
        "status": "ok",
        "user_location": {"lat": lat, "lon": lon},
        "epicenter": {"lat": epicenter.lat, "lon": epicenter.lon, "place": epicenter_eq['place']},
        "magnitude": magnitude,
        "safe_places": safe_places[:5]
    }
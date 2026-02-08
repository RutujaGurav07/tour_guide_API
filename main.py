from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
import pandas as pd
import math
import ollama
import json
from geopy.geocoders import Nominatim

app = FastAPI()

# Load dataset once at startup
df = pd.read_csv("Top Indian Places to Visit with missing LatLong.csv.csv")


# ===============================
# Utility Functions
# ===============================

# ==============================
# Haversine Distance
# ==============================

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c



# ==============================
# Geocoding
# ==============================

def get_lat_lon(place_name):
    geolocator = Nominatim(user_agent="trip_adviser_app")
    location = geolocator.geocode(place_name)
    if location:
        return location.latitude, location.longitude
    return None


# ==============================
# Trip Logic
# ==============================

def trip_logic(days, speed=50, sleep=6, meal=3, buffer=2, compromise=False):
    total_hours = days * 24
    usable = total_hours - (days * (sleep + meal + buffer))

    if compromise:
        usable += (sleep - 4)

    travel_hours = (2 / 3) * usable
    explore_hours = (1 / 3) * usable
    max_distance = travel_hours * speed

    return max_distance, usable


# ==============================
# Bounding Box Filter
# ==============================

def bounding_box(lat, lon, distance_km):
    delta_lat = distance_km / 111.0
    delta_lon = distance_km / (111.0 * math.cos(math.radians(lat)))
    return lat - delta_lat, lat + delta_lat, lon - delta_lon, lon + delta_lon



def filter_places(df, lat_x, lon_x, max_distance_km, tolerance=150):
    min_lat, max_lat, min_lon, max_lon = bounding_box(lat_x, lon_x, max_distance_km + tolerance)
    
    # Step 1: Bounding box filter
    candidates = df[(df['Latitude'] >= min_lat) & (df['Latitude'] <= max_lat) &
                    (df['Longitude'] >= min_lon) & (df['Longitude'] <= max_lon)].copy()
    
    # Step 2: Exact Haversine distance
    candidates['distance_km'] = candidates.apply(
        lambda row: haversine(lat_x, lon_x, row['Latitude'], row['Longitude']),
        axis=1
    )
    
    # Step 3: Keep only within max_distance ± tolerance
    min_dist = max_distance_km - tolerance
    max_dist = max_distance_km + tolerance
    filtered_df = candidates[(candidates['distance_km'] >= min_dist) & (candidates['distance_km'] <= max_dist)]
    filtered_df = filtered_df.sort_values(by='distance_km')
    city = []
    if 'City' in filtered_df.columns and 'Name' in filtered_df.columns:
        for _, row in filtered_df.iterrows():
            if row["City"] not in city:
                city.append(row["City"])
        print(city[0:5])

    else:
        print("Columns 'City' and 'Name' not found in DataFrame")
    return city[0:5]

# ===============================
# 1️⃣ API - Recommend Cities
# ===============================

class RecommendRequest(BaseModel):
    user_location: str = Field(
        ...,
        example="Mumbai",
        description="Starting city or user current location"
    )
    trip_days: int = Field(
        ...,
        example=3,
        description="Number of days for the trip"
    )
    speed: int = Field(
        50,
        example=60,
        description="Travel speed in km per hour (default 50)"
    )


@app.post(
    "/recommend-cities",
    summary="Recommend cities based on travel distance",
    description="""
    Given a user's location and trip duration, recommend cities that can be visited within the travel distance  
    """
)
def recommend_cities(request: RecommendRequest):
    coords = get_lat_lon(request.user_location)
    if not coords:
        return {"error": "Location not found"}

    lat, lon = coords
    # max_distance = trip_logic(request.trip_days, request.speed)
    max_distance, usable_hours = trip_logic(request.trip_days, request.speed)
    tour_city = filter_places(df, lat, lon, max_distance)


    return {
        "max_distance_km": round(max_distance, 2),
        "recommended_cities": tour_city[:5]
    }


# ===============================
# 2️⃣ API - Get Places in City
# ===============================
class CityRequest(BaseModel):
    city: str = Field(
        ...,
        example="Jaipur",
        description="Name of the city to fetch tourist places"
    )


@app.post(\
    "/city-places",
    summary="Get tourist places in a city",
    description="Fetch tourist places in the specified city with details like type, visit hours, and Google rating"
          )
def city_places(request: CityRequest):
    filtered = df[df["City"].str.lower() == request.city.lower()]

    places = filtered[
        ["Name", "Type",
         "time needed to visit in hrs",
         "Google review rating"]
    ].to_dict(orient="records")

    return {
        "city": request.city,
        "places": places
    }


# ===============================
# 3️⃣ API - Generate Itinerary
# ===============================

class ItineraryRequest(BaseModel):
    city: str = Field(..., example="Jaipur")
    trip_days: int = Field(..., example=3)
    arrival_info: str = Field(
        ...,
        example="Arriving by train at 9 AM"
    )
    preferred_types: List[str] = Field(
        ...,
        example=["Historical", "Cultural"]
    )
    group: str = Field(
        ...,
        example="Family",
        description="Type of travel group"
    )
    pace: str = Field(
        ...,
        example="Moderate",
        description="Trip pace: Relaxed / Moderate / Fast"
    )


@app.post(
    "/generate-itinerary",
    summary="Generate a day-wise itinerary for a city",
    description=""" Generate a day-wise itinerary for the specified city based on user preferences and tourist places.
    The itinerary will consider arrival information, preferred types of places, group type, and trip pace.
    """)
def generate_itinerary(request: ItineraryRequest):

    filtered = df[df["City"].str.lower() == request.city.lower()]

    places = filtered[
        ["Name", "Type",
         "time needed to visit in hrs",
         "Google review rating"]
    ].to_dict(orient="records")

    # Sort by rating
    places = sorted(
        places,
        key=lambda x: x["Google review rating"],
        reverse=True
    )[:10]

    places_text = ""
    for i, p in enumerate(places):
        places_text += f"""
{i+1}. {p['Name']}
   - Type: {p['Type']}
   - Required Visit Hours: {p['time needed to visit in hrs']}
   - Google Rating: {p['Google review rating']}
"""

    system_prompt = """
You are an expert Indian travel planner.
Only use the provided places.
Do NOT invent new locations.
Return strictly valid JSON.
"""

    user_prompt = f"""
Create a {request.trip_days}-day itinerary for {request.city}.

Arrival Info:
{request.arrival_info}

User Preferences:
Group: {request.group}
Preferred Types: {", ".join(request.preferred_types)}
Trip Pace: {request.pace}

Tourist Places:
{places_text}

Return JSON format:
{{
  "city": "{request.city}",
  "days": []
}}
"""

    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        options={
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 1200
        }
    )

    try:
        itinerary = json.loads(response["message"]["content"])
        return itinerary
    except:
        return {"raw_output": response["message"]["content"]}


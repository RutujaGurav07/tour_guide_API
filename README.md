## 🧭 AI Tour Guide – Trip Planner API
A FastAPI-based intelligent travel planning system that recommends cities, lists tourist places, and generates AI-powered itineraries based on user preferences and trip duration.

## 📖 Table of Contents
- Overview
- Architecture
- Features
- Tech Stack
- Installation
- Running the Application
- API Documentation
    1. Recommend Cities
    2. City Places
    3. Generate Itinerary
- Internal Logic
- Future Enhancements
  
## Overview
The AI Tour Guide API helps users plan trips efficiently by:
- Calculating travelable distance based on trip duration
- Recommending nearby cities within range
- Listing tourist attractions in selected cities
- Generating structured AI-based itineraries

The system uses geographic distance calculations and LLM-based itinerary generation.

## Architecture
```
Client (Postman / Frontend)
        │
        ▼
FastAPI Backend
        │
        ├── Pandas Dataset (Tourist Places)
        ├── Geopy (Geocoding)
        ├── Haversine Distance Logic
        └── Ollama (Llama3) – AI Itinerary
```

## Features
- Distance-based travel recommendation
- Bounding box optimization for filtering cities
- AI-powered itinerary generation
- Swagger UI auto-documentation
- Clean modular utility functions

## Tech Stack

| Technology | Purpose |
|------------|----------|
| FastAPI    | Backend framework |
| Pandas     | Data processing |
| Geopy      | Geocoding |
| Ollama     | AI itinerary generation |


## Installation
### 1. Clone Repository
```
git clone https://github.com/your-username/ai-tour-guide.git
cd ai-tour-guide
```

### 2. Create Virtual Environment
```
python -m venv venv
```

**Activate:**

Windows
```
venv\Scripts\activate
```

Mac/Linux
```
source venv/bin/activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

## Running the Application

Start the server:

```
uvicorn main:app --reload
```

Access:
- Base URL: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Documentation
### 1. Recommend Cities
#### Endpoint
```
POST /recommend-cities
```
#### Description
Calculates maximum travelable distance based on trip duration and recommends nearby cities.

**Request Body**
```
{
  "user_location": "Mumbai",
  "trip_days": 3,
  "speed": 50
}
```
**Response**
```
{
  "max_distance_km": 600.0,
  "recommended_cities": [
    "Jaipur",
    "Udaipur",
    "Indore"
  ]
}
```
### 2. City Places

**Endpoint**
```
POST /city-places
```
**Description**
Returns tourist attractions in a selected city.

**Request Body**
```
{
  "city": "Jaipur"
}
```
**Response**
```
{
  "city": "Jaipur",
  "places": [
    {
      "Name": "Hawa Mahal",
      "Type": "Historical",
      "time needed to visit in hrs": 2,
      "Google review rating": 4.5
    }
  ]
}
```

### 3. Generate Itinerary
Endpoint
```
POST /generate-itinerary
```
**Description**

Generates a structured multi-day itinerary using Llama3.

**Request Body**
```
{
  "city": "Jaipur",
  "trip_days": 3,
  "arrival_info": "Arriving by train at 9 AM",
  "preferred_types": ["Historical", "Cultural"],
  "group": "Family",
  "pace": "Moderate"
}
```
**Response (Example)**
```
{
  "city": "Jaipur",
  "days": [
    {
      "day": 1,
      "activities": [
        {
          "place": "Amber Fort",
          "start_time": "10:00 AM",
          "duration_hours": 3
        }
      ]
    }
  ]
}
```
## Internal Logic

#### Distance Calculation
- Uses Haversine formula to compute real geographic distance.
- Applies bounding box filtering for optimization.
- Calculates travelable distance using trip duration and travel speed.

#### Itinerary Generation
- Filters top 10 highest-rated places.
- Sends structured prompt to Llama3 via Ollama.
- Returns strictly valid JSON response.

#### Future Enhancements

- Add JWT Authentication
- Add Database (PostgreSQL / MongoDB)
- Add Budget Optimization
- Add Hotel & Transport Integration
- Docker Deployment
- CI/CD Pipeline
- Frontend Integration

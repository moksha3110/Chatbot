"""
A real external tool: get_weather.

Unlike get_current_time, this tool (a) calls a real external API and (b) takes
an ARGUMENT — the city. When you ask "what's the weather in Chennai?", Gemini
extracts city="Chennai" from your sentence and passes it here.

We use Open-Meteo (https://open-meteo.com), a free public weather API that needs
NO API KEY — so we can focus on the mechanics. It takes two calls:
  1. Geocoding: turn a city NAME into latitude/longitude.
  2. Forecast:  get the CURRENT weather at those coordinates.

(If we used a keyed API instead, the key would live in .env and be read via
app/core/config.py — the same pattern as GEMINI_API_KEY.)
"""

import httpx

from app.tools.base import Tool

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Open-Meteo returns weather as a numeric code; this maps the common ones to text
# the model can phrase naturally.
WEATHER_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "rime fog",
    51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "snow", 75: "heavy snow",
    80: "rain showers", 81: "rain showers", 82: "violent rain showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "thunderstorm with hail",
}


def _get_weather(args: dict) -> str:
    """Fetch current weather for the given city. Returns a human-readable string."""
    city = (args.get("city") or "").strip()
    if not city:
        return "Error: no city was provided."

    try:
        # 1. Geocode the city name -> coordinates.
        geo = httpx.get(GEOCODE_URL, params={"name": city, "count": 1}, timeout=10)
        geo.raise_for_status()
        results = geo.json().get("results")
        if not results:
            return f"Could not find a place called '{city}'."
        place = results[0]
        lat, lon = place["latitude"], place["longitude"]
        name = place["name"]
        country = place.get("country", "")

        # 2. Fetch the current weather at those coordinates.
        forecast = httpx.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            },
            timeout=10,
        )
        forecast.raise_for_status()
        current = forecast.json()["current"]

        description = WEATHER_CODES.get(current["weather_code"], "unknown conditions")
        return (
            f"Current weather in {name}, {country}: {description}, "
            f"{current['temperature_2m']}°C, "
            f"humidity {current['relative_humidity_2m']}%, "
            f"wind {current['wind_speed_10m']} km/h."
        )
    except Exception as e:
        # Never crash the request — hand a readable error back to the model.
        return f"Error fetching weather for '{city}': {e}"


weather_tool = Tool(
    name="get_weather",
    description=(
        "Get the CURRENT weather for a city. Use this whenever the user asks "
        "about the weather, temperature, or conditions in a specific place."
    ),
    run=_get_weather,
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city to get weather for, e.g. 'Chennai' or 'London'.",
            }
        },
        "required": ["city"],
    },
)

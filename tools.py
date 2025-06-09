import os
import requests
import json
from datetime import datetime
from langchain_core.tools import tool

device_states = {
    "lamps": {
        "kitchen": "off",
        "bathroom": "off",
        "room 1": "off",
        "room 2": "off",
    },
    "ac_units": {
        "room 1": {"state": "off", "temperature": 24},
        "kitchen": {"state": "off", "temperature": 25},
    },
    "tv": {
        "living_room": {"state": "off", "channel": 1}
    },
    "doors": {
        "front": "locked",
        "back": "locked"
    },
    "blinds": {
        "kitchen": "closed",
        "room 1": "closed"
    }
}


@tool(return_direct=True)
def toggle_light(location: str, state: str) -> str:
    """Turns a light on or off in a specific location. Use this to control lamps.
    'location' must be one of ['kitchen', 'bathroom', 'room 1', 'room 2'].
    'state' must be 'on' or 'off'.
    """
    location = location.lower()
    state = state.lower()
    if location not in device_states["lamps"]:
        return f"Error: Light location '{location}' not found."
    if state not in ["on", "off"]:
        return f"Error: Invalid state '{state}'. Must be 'on' or 'off'."

    device_states["lamps"][location] = state
    return f"Successfully turned the {location} light {state}."


@tool(return_direct=True)
def set_ac_temperature(location: str, temperature: int) -> str:
    """Sets the temperature for an AC unit in a specific location.
    'location' must be one of ['room 1', 'kitchen'].
    This function also turns the AC on if it's off.
    """
    location = location.lower()
    if location not in device_states["ac_units"]:
        return f"Error: AC location '{location}' not found."

    device_states["ac_units"][location]["temperature"] = temperature
    if device_states["ac_units"][location]["state"] == "off":
        device_states["ac_units"][location]["state"] = "on"
        return f"Successfully set AC in {location} to {temperature}°C and turned it on."

    return f"Successfully set AC temperature in {location} to {temperature}°C."


@tool(return_direct=True)
def get_device_status(device_type: str = "all") -> str:
    """Gets the current status of all devices or a specific type of device.
    'device_type' can be 'all', 'lamps', 'ac_units', or 'tv'.
    """
    if device_type == "all":
        return json.dumps(device_states, indent=2)
    if device_type in device_states:
        return f"Status for {device_type}: {json.dumps(device_states[device_type], indent=2)}"
    return f"Error: Unknown device type '{device_type}'."


@tool(return_direct=True)
def get_weather() -> str:
    """Fetches the current weather for a given city."""
    city = "tehran"
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OpenWeatherMap API key not found."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"The current weather in {city} is {temp}°C with {weather_desc}."
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather: {e}"

@tool(return_direct=True)
def get_latest_news(country: str = "us") -> str:
    """Fetches the latest news headlines for a given country code (e.g., 'us' for USA, 'ir' for Iran)."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "Error: NewsAPI key not found."

    url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        headlines = [f"- {article['title']}" for article in articles[:5]]  # Get top 5
        if not headlines:
            return f"No news found for country code '{country}'."
        return "Here are the latest headlines:\n" + "\n".join(headlines)
    except requests.exceptions.RequestException as e:
        return f"Error fetching news: {e}"


@tool(return_direct=True)
def get_current_datetime() -> str:
    """Returns the current date and time."""
    now = datetime.now()
    return f"The current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}."


@tool(return_direct=True)
def turn_on_tv(location: str) -> str:
    """Turns on the TV in the specified location. Only works if the TV is currently off."""
    location = location.lower()
    if location not in device_states["tv"]:
        return f"Error: TV location '{location}' not found."

    if device_states["tv"][location]["state"] == "on":
        return f"The TV in {location} is already on."

    device_states["tv"][location]["state"] = "on"
    return f"The TV in {location} is now turned on."


@tool(return_direct=True)
def change_tv_channel(location: str, channel: int) -> str:
    """Changes the channel of the TV in the specified location.
    Turns the TV on if it's currently off.
    """
    location = location.lower()
    if location not in device_states["tv"]:
        return f"Error: TV location '{location}' not found."

    if device_states["tv"][location]["state"] == "off":
        device_states["tv"][location]["state"] = "on"

    device_states["tv"][location]["channel"] = channel
    return f"Changed the TV channel in {location} to channel {channel}."


@tool(return_direct=True)
def lock_door(location: str) -> str:
    """Locks the door in the specified location. Valid locations: ['front', 'back']"""
    location = location.lower()
    if location not in device_states["doors"]:
        return f"Error: Door location '{location}' not found."

    device_states["doors"][location] = "locked"
    return f"The {location} door is now locked."


@tool(return_direct=True)
def unlock_door(location: str) -> str:
    """Unlocks the door in the specified location. Valid locations: ['front', 'back']"""
    location = location.lower()
    if location not in device_states["doors"]:
        return f"Error: Door location '{location}' not found."

    device_states["doors"][location] = "unlocked"
    return f"The {location} door is now unlocked."


@tool(return_direct=True)
def open_blinds(location: str) -> str:
    """Opens the blinds in the specified location. Valid locations: ['kitchen', 'room 1']"""
    location = location.lower()
    if location not in device_states["blinds"]:
        return f"Error: Blinds location '{location}' not found."

    device_states["blinds"][location] = "open"
    return f"The blinds in {location} are now open."


@tool(return_direct=True)
def close_blinds(location: str) -> str:
    """Closes the blinds in the specified location. Valid locations: ['kitchen', 'room 1']"""
    location = location.lower()
    if location not in device_states["blinds"]:
        return f"Error: Blinds location '{location}' not found."

    device_states["blinds"][location] = "closed"
    return f"The blinds in {location} are now closed."


@tool(return_direct=True)
def activate_sleep_mode() -> str:
    """Puts the home into sleep mode: turns off lights, turns off AC, closes blinds, locks doors."""
    for light in device_states["lamps"]:
        device_states["lamps"][light] = "off"

    for ac in device_states["ac_units"]:
        device_states["ac_units"][ac]["state"] = "off"

    for blind in device_states["blinds"]:
        device_states["blinds"][blind] = "closed"

    for door in device_states["doors"]:
        device_states["doors"][door] = "locked"

    return "Sleep mode activated: lights and ACs turned off, blinds closed, doors locked."


@tool(return_direct=True)
def activate_guest_mode() -> str:
    """Puts the home into guest mode: turns on living room light and AC, opens blinds, unlocks front door."""
    if "room 1" in device_states["lamps"]:
        device_states["lamps"]["room 1"] = "on"
    if "room 1" in device_states["ac_units"]:
        device_states["ac_units"]["room 1"]["state"] = "on"

    for blind in device_states["blinds"]:
        device_states["blinds"][blind] = "open"

    if "front" in device_states["doors"]:
        device_states["doors"]["front"] = "unlocked"

    return "Guest mode activated: lights and AC turned on, blinds opened, front door unlocked."

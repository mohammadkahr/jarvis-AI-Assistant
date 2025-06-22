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
        "living_room": {"state": "off", "channel": 1, "volume": 20}
    },
    "doors": {
        "front": "locked",
        "back": "locked"
    },
    "blinds": {
        "kitchen": "closed",
        "room 1": "closed"
    },
    "coffee_machine": {
        "kitchen": "off"
    }
}


@tool
def toggle_light(location: str, state: str) -> str:
    """Turns a light on or off in a specific location. Use this to control lamps.
    Valid locations are ['kitchen', 'bathroom', 'room 1', 'room 2'].
    Valid states are 'on' or 'off'.
    """
    location = location.lower()
    state = state.lower()
    if location not in device_states["lamps"]:
        return f"Error: Light location '{location}' not found. Valid locations are: kitchen, bathroom, room 1, room 2."
    if state not in ["on", "off"]:
        return f"Error: Invalid state '{state}'. Must be 'on' or 'off'."

    device_states["lamps"][location] = state
    return f"Successfully turned the {location} light {state}."


@tool
def turn_on_ac(location: str) -> str:
    """Turns on an AC unit in a specific location.
    Valid locations are ['room 1', 'kitchen'].
    """
    location = location.lower()
    if location not in device_states["ac_units"]:
        return f"Error: AC location '{location}' not found. Valid locations are: room 1, kitchen."

    if device_states["ac_units"][location]["state"] == "on":
        return f"The AC in {location} is already on."

    device_states["ac_units"][location]["state"] = "on"
    return f"Successfully turned the AC in {location} on."


@tool
def turn_off_ac(location: str) -> str:
    """Turns off an AC unit in a specific location.
    Valid locations are ['room 1', 'kitchen'].
    """
    location = location.lower()
    if location not in device_states["ac_units"]:
        return f"Error: AC location '{location}' not found. Valid locations are: room 1, kitchen."

    if device_states["ac_units"][location]["state"] == "off":
        return f"The AC in {location} is already off."

    device_states["ac_units"][location]["state"] = "off"
    return f"Successfully turned the AC in {location} off."


@tool
def set_ac_temperature(location: str, temperature: int) -> str:
    """Sets the temperature for an AC unit in a specific location.
    Valid locations are ['room 1', 'kitchen'].
    This function also turns the AC on if it's off.
    """
    location = location.lower()
    if location not in device_states["ac_units"]:
        return f"Error: AC location '{location}' not found. Valid locations are: room 1, kitchen."

    device_states["ac_units"][location]["temperature"] = temperature
    if device_states["ac_units"][location]["state"] == "off":
        device_states["ac_units"][location]["state"] = "on"
        return f"Successfully set AC in {location} to {temperature}°C and turned it on."

    return f"Successfully set AC temperature in {location} to {temperature}°C."


@tool
def get_device_status(device_type: str = "all") -> str:
    """Gets the current status of all devices or a specific type of device.
    'device_type' can be 'all', 'lamps', 'ac_units', 'tv', 'doors', 'blinds', 'security_system', 'music_player', 'coffee_machine'.
    """
    if device_type == "all":
        return json.dumps(device_states, indent=2)
    if device_type in device_states:
        return f"Status for {device_type}: {json.dumps(device_states[device_type], indent=2)}"
    return f"Error: Unknown device type '{device_type}'."


@tool
def get_weather() -> str:
    """Fetches the current weather for the default city (Tehran)."""
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


@tool
def get_latest_news(country: str = "us") -> str:
    """Fetches the latest news headlines for a given country code (e.g., 'us' for USA, 'ir' for Iran)."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "Error: NewsAPI key not found."

    url = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={api_key}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        headlines = [f"- {article['title']}" for article in articles[:5]]
        if not headlines:
            return f"No news found for country code '{country}'."
        return "Here are the latest headlines:\n" + "\n".join(headlines)
    except requests.exceptions.RequestException as e:
        return f"Error fetching news: {e}"


@tool
def get_current_datetime() -> str:
    """Returns the current date and time."""
    now = datetime.now()
    return f"The current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}."


@tool
def turn_on_tv(location: str) -> str:
    """Turns on the TV in the specified location. The only valid location is 'living_room'."""
    location = location.lower()
    if location != "living_room":
        return f"Error: TV location '{location}' not found. The only valid location is 'living_room'."

    if device_states["tv"][location]["state"] == "on":
        return f"The TV in {location} is already on."

    device_states["tv"][location]["state"] = "on"
    return f"The TV in {location} is now turned on."


@tool
def turn_off_tv(location: str) -> str:
    """Turns off the TV in the specified location. The only valid location is 'living_room'."""
    location = location.lower()
    if location != "living_room":
        return f"Error: TV location '{location}' not found. The only valid location is 'living_room'."

    if device_states["tv"][location]["state"] == "off":
        return f"The TV in {location} is already off."

    device_states["tv"][location]["state"] = "off"
    return f"The TV in {location} is now turned off."


@tool
def change_tv_channel(location: str, channel: int) -> str:
    """Changes the channel of the TV in the specified location. The only valid location is 'living_room'.
    This function also turns the TV on if it's currently off.
    """
    location = location.lower()
    if location != "living_room":
        return f"Error: TV location '{location}' not found. The only valid location is 'living_room'."

    if device_states["tv"][location]["state"] == "off":
        device_states["tv"][location]["state"] = "on"

    device_states["tv"][location]["channel"] = channel
    return f"Changed the TV channel in {location} to channel {channel}."


@tool
def set_tv_volume(location: str, volume: int) -> str:
    """Sets the volume of the TV in a specified location. The only valid location is 'living_room'.
    Volume should be between 0 and 100.
    """
    location = location.lower()
    if location != "living_room":
        return f"Error: TV location '{location}' not found. The only valid location is 'living_room'."
    if not 0 <= volume <= 100:
        return "Error: Volume must be between 0 and 100."

    device_states["tv"][location]["volume"] = volume
    return f"Successfully set TV volume in {location} to {volume}."


@tool
def lock_door(location: str) -> str:
    """Locks the door in the specified location. Valid locations: ['front', 'back']"""
    location = location.lower()
    if location not in device_states["doors"]:
        return f"Error: Door location '{location}' not found."
    device_states["doors"][location] = "locked"
    return f"The {location} door is now locked."


@tool
def unlock_door(location: str) -> str:
    """Unlocks the door in the specified location. Valid locations: ['front', 'back']"""
    location = location.lower()
    if location not in device_states["doors"]:
        return f"Error: Door location '{location}' not found."
    device_states["doors"][location] = "unlocked"
    return f"The {location} door is now unlocked."


@tool
def open_blinds(location: str) -> str:
    """Opens the blinds in the specified location. Valid locations: ['kitchen', 'room 1']"""
    location = location.lower()
    if location not in device_states["blinds"]:
        return f"Error: Blinds location '{location}' not found."
    device_states["blinds"][location] = "open"
    return f"The blinds in {location} are now open."


@tool
def close_blinds(location: str) -> str:
    """Closes the blinds in the specified location. Valid locations: ['kitchen', 'room 1']"""
    location = location.lower()
    if location not in device_states["blinds"]:
        return f"Error: Blinds location '{location}' not found."
    device_states["blinds"][location] = "closed"
    return f"The blinds in {location} are now closed."


@tool
def turn_off_all_lights(confirm: bool = True) -> str:
    """Turns off all lights in the house."""
    for light in device_states["lamps"]:
        device_states["lamps"][light] = "off"
    return "All lights have been turned off."


@tool
def turn_on_all_lights(confirm: bool = True) -> str:
    """Turns off all lights in the house."""
    for light in device_states["lamps"]:
        device_states["lamps"][light] = "on"
    return "All lights have been turned on."

@tool
def start_coffee_machine(confirm: bool = True) -> str:
    """Starts the coffee machine in the kitchen."""
    if device_states["coffee_machine"]["kitchen"] == "on":
        return "The coffee machine is already on."
    device_states["coffee_machine"]["kitchen"] = "on"
    return "The coffee machine has been started. Enjoy your coffee soon!"


@tool
def stop_coffee_machine(confirm: bool = True) -> str:
    """Stops the coffee machine in the kitchen."""
    if device_states["coffee_machine"]["kitchen"] == "off":
        return "The coffee machine is already off."
    device_states["coffee_machine"]["kitchen"] = "off"
    return "The coffee machine has been stopped."

@tool
def activate_guest_mode(confirm: bool = True) -> str:
    """Puts the home into guest mode: turns on room 1 light and AC, opens all blinds, and unlocks the front door."""
    if "room 1" in device_states["lamps"]:
        device_states["lamps"]["room 1"] = "on"
    if "room 1" in device_states["ac_units"]:
        device_states["ac_units"]["room 1"]["state"] = "on"
        device_states["ac_units"]["room 1"]["temperature"] = 22
    for blind in device_states["blinds"]:
        device_states["blinds"][blind] = "open"
    if "front" in device_states["doors"]:
        device_states["doors"]["front"] = "unlocked"
    return "Guest mode activated: Room 1 light and AC are on, all blinds are open, and the front door is unlocked."
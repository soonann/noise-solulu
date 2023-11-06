import random
import time
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

# Constants
UNIX_WEEK = 7 * 24 * 60 * 60
INTERVAL = 300  # 5 minutes
DAY = 86400  # Seconds in a day
MORNING = 6 * 3600  # 6 AM in Singapore Time
EVENING = 22 * 3600  # 10 PM in Singapore Time
SGT_OFFSET = 8 * 3600  # Singapore Time offset from UTC

# Sound definitions
class_labels = [
    "air_conditioner",
    "car_horn",
    "children_playing",
    "dog_bark",
    "drilling",
    "engine_idling",
    "neutral",
    "jackhammer",
    "siren",
    "street_music"
]

sound_parameters = {
    "air_conditioner": {"mean": 55, "sd": 5, "min": 37, "max": 82},
    "car_horn": {"mean": 80, "sd": 10, "min": 70, "max": 100},
    "children_playing": {"mean": 65, "sd": 5, "min": 55, "max": 95},
    "dog_bark": {"mean": 70, "sd": 8, "min": 60, "max": 80},
    "drilling": {"mean": 80, "sd": 5, "min": 70, "max": 90},
    "engine_idling": {"mean": 55, "sd": 5, "min": 45, "max": 65},
    "neutral": {"mean": 40, "sd": 5, "min": 30, "max": 50},
    "jackhammer": {"mean": 85, "sd": 5, "min": 75, "max": 95},
    "siren": {"mean": 90, "sd": 10, "min": 80, "max": 100},
    "street_music": {"mean": 75, "sd": 5, "min": 65, "max": 85}
}

# This dictionary will determine how long a sound lasts based on its class
sound_durations = {
    "air_conditioner": (10, 20),
    "car_horn": (1, 2),
    "children_playing": (10, 30),
    "dog_bark": (2, 5),
    "drilling": (30, 60),
    "engine_idling": (5, 10),
    "jackhammer": (30, 60),
    "siren": (1, 3),
    "street_music": (10, 30),
    "neutral": (30, 60)  # Neutral sound lasts longer
}

# Weights are only used during daytime to simulate higher activity
daytime_weights = {
    "air_conditioner": 5,
    "car_horn": 5,
    "children_playing": 5,
    "dog_bark": 5,
    "drilling": 5,
    "engine_idling": 5,
    "neutral": 80,  # Neutral is still the most common sound
    "jackhammer": 5,
    "siren": 5,
    "street_music": 5
}

# Utility functions
def get_random_loc():
    lat = round(random.uniform(1.2, 1.5), 4)
    lng = round(random.uniform(103.6, 104.0), 4)
    return lat, lng

def get_timestamp():
    return int(time.time())

def get_decibel_for_class(sound_class):
    params = sound_parameters[sound_class]
    decibel = random.gauss(params["mean"], params["sd"])
    return round(max(min(decibel, params["max"]), params["min"]), 2)

# Core functions
def is_night_time(timestamp):
    """ Determine if the timestamp is within the night time in Singapore. """
    sgt_hour = (timestamp + SGT_OFFSET) % DAY // 3600
    return sgt_hour >= 22 or sgt_hour < 6  # Between 10 PM and 6 AM SGT

def choose_sound_class(timestamp):
    """ Choose the sound class based on the time of day in Singapore. """
    if is_night_time(timestamp):
        return 'neutral'  # Night time is almost always neutral
    else:
        return random.choices(
            population=class_labels,
            weights=[daytime_weights.get(sound, 1) for sound in class_labels],
            k=1
        )[0]

def get_duration_for_sound_class(sound_class):
    """ Randomly choose a duration for the sound class within specified ranges. """
    return random.randint(*sound_durations[sound_class]) * 60

def generate_mock_data(users=1):
    """ Generate mock data for the specified number of users. """
    mock_data = []
    start_time = get_timestamp() - UNIX_WEEK  # Start one week ago
    for _ in range(users):
        currLat, currLng = get_random_loc()
        currTime = start_time
        row = []
        while currTime < start_time + UNIX_WEEK:
            sound_class = choose_sound_class(currTime)
            duration = get_duration_for_sound_class(sound_class)
            decibels = get_decibel_for_class(sound_class)
            row.append({
                "timestamp": currTime,
                "class": sound_class,
                "decibels": decibels
            })
            currTime += duration
        mock_data.append({
            "id": _,
            "lat": currLat,
            "lng": currLng,
            "data": row
        })
    return mock_data

# Function to analyze data
def analyze_noise_data(data, quiet_threshold=45, active_threshold=70):
    """ Analyze the noise data to identify quiet and active periods. """
    quiet_periods = []
    active_periods = []
    current_quiet_start = None
    current_active_start = None

    for entry in data:
        timestamp = entry['timestamp']
        decibels = entry['decibels']

        # Handle quiet periods
        if decibels < quiet_threshold:
            if current_quiet_start is None:
                current_quiet_start = timestamp  # Start of a new quiet period
        else:
            if current_quiet_start is not None:
                # End of the quiet period
                quiet_periods.append((current_quiet_start, timestamp))
                current_quiet_start = None

        # Handle active periods
        if decibels > active_threshold:
            if current_active_start is None:
                current_active_start = timestamp  # Start of a new active period
        else:
            if current_active_start is not None:
                # End of the active period
                active_periods.append((current_active_start, timestamp))
                current_active_start = None

    # Close any open periods at the end
    last_timestamp = data[-1]['timestamp']
    if current_quiet_start is not None:
        quiet_periods.append((current_quiet_start, last_timestamp))
    if current_active_start is not None:
        active_periods.append((current_active_start, last_timestamp))

    return quiet_periods, active_periods

# Main execution

    # Continue with the recommendation and formatting logic...

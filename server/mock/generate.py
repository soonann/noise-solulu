import random
import time
import json

# List of class labels
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

users = 1
rows = 10000
UNIX_WEEK = 7 * 24 * 60 * 60
INTERVAL = 300


# some random lat, lng in singapore
def get_random_loc():
    lat = round(random.uniform(1.2, 1.5), 4)
    lng = round(random.uniform(103.6, 104.0), 4)
    return lat, lng


# get the timestamp, if none is passed it will get the current timestamp
def get_timestamp():
    timestamp = int(time.time())  # Current Unix timestamp
    return timestamp


# generate a random class and its decibels
def get_random_class_decibel():
    class_label = random.choice(class_labels)
    decibels = round(random.uniform(30, 100), 2)
    return class_label, decibels


# Generate users
for i in range(0, users):

    currLat, currLng = get_random_loc()
    currTime = get_timestamp()
    startTime = currTime  # save start
    currTime = currTime - UNIX_WEEK  # go back 1 week
    row = []
    # for each user, generate a week worth of data since the curr time
    while currTime < startTime:
        class_label, decibels = get_random_class_decibel()
        entry = {
            "class": class_label,
            "decibels": decibels,
            "timestamp": currTime,
        }
        row.append(entry)
        currTime += INTERVAL

    data_obj = {
        "id": i,
        "lat": currLat,  # assume they don't move
        "lng": currLng,
        "data": row,
    }

    # save data to a JSON file
    with open(
            f"mock-{i}.json",
            "w",
            # indent=4,  # save space
            ) as json_file:
        json.dump(data_obj, json_file)

    print(f"Data saved to mock-{i}.json")

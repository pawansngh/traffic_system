import random

def get_vehicle_counts():
    return {
        "North": random.randint(50, 300),
        "South": random.randint(50, 300),
        "East":  random.randint(50, 300),
        "West":  random.randint(50, 300),
    }
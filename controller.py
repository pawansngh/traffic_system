from config import CONGESTION_THRESHOLDS, GREEN_DURATION

def get_signal_states(lanes):
    signals = {}
    busiest = max(lanes, key=lanes.get)
    for lane, count in lanes.items():
        if lane == busiest:
            signals[lane] = "GREEN"
        elif count > CONGESTION_THRESHOLDS["high"]:
            signals[lane] = "AMBER"
        else:
            signals[lane] = "RED"
    return signals

def get_green_duration(count):
    if count < CONGESTION_THRESHOLDS["low"]:
        return GREEN_DURATION["low"]
    elif count < CONGESTION_THRESHOLDS["high"]:
        return GREEN_DURATION["medium"]
    else:
        return GREEN_DURATION["high"]
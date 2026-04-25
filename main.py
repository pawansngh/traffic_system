import time
from sensors import get_vehicle_counts
from controller import get_signal_states
from display import show_signals

print("Traffic Management System Started")
print("Press Ctrl+C to stop\n")

try:
    while True:
        lanes = get_vehicle_counts()
        signals = get_signal_states(lanes)
        show_signals(lanes, signals)
        time.sleep(3)
except KeyboardInterrupt:
    print("\nSystem stopped.")
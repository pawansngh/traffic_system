def show_signals(lanes, signals):
    print("\n=============================")
    print("   TRAFFIC SIGNAL STATUS")
    print("=============================")
    for lane in lanes:
        count = lanes[lane]
        state = signals[lane]
        bar = "█" * (count // 20)
        print(f"  {lane:6s} | {state:6s} | {bar} ({count})")
    print("=============================\n")
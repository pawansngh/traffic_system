import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from database import init_db, log_signals, log_stats, get_recent_logs
from sensors import get_vehicle_counts
from controller import get_signal_states, get_green_duration
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'traffic_secret_key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize DB
init_db()

# ── Background thread — pushes live data every 3 seconds ─────
def background_traffic_loop():
    while True:
        lanes   = get_vehicle_counts()
        signals = get_signal_states(lanes)
        total   = sum(lanes.values())
        peak    = max(lanes, key=lanes.get)

        signal_data = []
        for lane in lanes:
            signal_data.append({
                "lane":     lane,
                "vehicles": lanes[lane],
                "signal":   signals[lane],
                "duration": get_green_duration(lanes[lane])
            })

        stats = {
            "total_vehicles":   total,
            "peak_lane":        peak,
            "avg_wait_time":    round(total / 40),
            "active_junctions": 6
        }

        # Save to database
        log_signals(signal_data)
        log_stats(stats)

        # Push to all connected browsers instantly
        socketio.emit('traffic_update', {
            "signals": signal_data,
            "stats":   stats,
            "history": get_recent_logs(20)
        })

        time.sleep(3)

# Start background thread when app boots
thread = threading.Thread(target=background_traffic_loop, daemon=True)
thread.start()

# ── Routes ────────────────────────────────────────────────────
@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/api/signals')
def get_signals():
    lanes   = get_vehicle_counts()
    signals = get_signal_states(lanes)
    result  = [{"lane": l, "vehicles": lanes[l],
                "signal": signals[l], "duration": get_green_duration(lanes[l])}
               for l in lanes]
    return jsonify({"status": "ok", "data": result})

@app.route('/api/stats')
def get_stats():
    lanes = get_vehicle_counts()
    total = sum(lanes.values())
    peak  = max(lanes, key=lanes.get)
    return jsonify({
        "total_vehicles":   total,
        "peak_lane":        peak,
        "avg_wait_time":    round(total / 40),
        "active_junctions": 6
    })

@app.route('/api/history')
def get_history():
    return jsonify({"status": "ok", "data": get_recent_logs(20)})

@app.route('/api/health')
def health():
    return jsonify({"status": "running"})

# ── SocketIO events ───────────────────────────────────────────
@socketio.on('connect')
def on_connect():
    print('Client connected')
    emit('connected', {'message': 'Connected to Traffic Server'})

@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected')

# ── Run ───────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
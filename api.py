from flask import Flask, jsonify, render_template
from flask_cors import CORS
from sensors import get_vehicle_counts
from controller import get_signal_states, get_green_duration
from database import init_db, log_signals, log_stats, get_recent_logs, get_stats_history

app = Flask(__name__)
CORS(app)

# Initialize DB when app starts
init_db()

# ── Dashboard ─────────────────────────────────────────────────
@app.route('/')
def dashboard():
    return render_template('index.html')

# ── Route 1: Live signals (now also logs to DB) ───────────────
@app.route('/api/signals', methods=['GET'])
def get_signals():
    lanes   = get_vehicle_counts()
    signals = get_signal_states(lanes)

    result = []
    for lane in lanes:
        result.append({
            "lane":     lane,
            "vehicles": lanes[lane],
            "signal":   signals[lane],
            "duration": get_green_duration(lanes[lane])
        })

    log_signals(result)   # ← save to database

    return jsonify({"status": "ok", "data": result})

# ── Route 2: Live stats (now also logs to DB) ─────────────────
@app.route('/api/stats', methods=['GET'])
def get_stats():
    lanes = get_vehicle_counts()
    total = sum(lanes.values())
    peak  = max(lanes, key=lanes.get)

    stats = {
        "total_vehicles":   total,
        "peak_lane":        peak,
        "avg_wait_time":    round(total / 40),
        "active_junctions": 6
    }

    log_stats(stats)   # ← save to database

    return jsonify(stats)

# ── Route 3: Signal history from DB ──────────────────────────
@app.route('/api/history', methods=['GET'])
def get_history():
    logs = get_recent_logs(limit=20)
    return jsonify({"status": "ok", "data": logs})

# ── Route 4: Stats history from DB ───────────────────────────
@app.route('/api/stats/history', methods=['GET'])
def get_stats_history_route():
    history = get_stats_history(limit=10)
    return jsonify({"status": "ok", "data": history})

# ── Route 5: Health check ─────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "running"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
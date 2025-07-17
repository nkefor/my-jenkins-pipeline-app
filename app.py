from flask import Flask, jsonify
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Train Schedule API!",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/schedule')
def get_schedule():
    # Mock train schedule data
    schedule = [
        {"train_id": "T101", "origin": "Station A", "destination": "Station B", "departure_time": "08:00", "arrival_time": "08:30"},
        {"train_id": "T102", "origin": "Station B", "destination": "Station C", "departure_time": "09:15", "arrival_time": "09:45"},
        {"train_id": "T103", "origin": "Station A", "destination": "Station C", "departure_time": "10:00", "arrival_time": "11:00"},
    ]
    return jsonify(schedule)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, render_template, request, jsonify
import joblib
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Load AI model
model = joblib.load("ortho_model.pkl")

# Store latest sensor data
latest_sensor_data = {
    "step_count": 0,
    "cadence": 0,
    "balance": 0,
    "symmetry": 0
}


# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect("ortho_data.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            age INTEGER,
            step_count REAL,
            cadence REAL,
            balance REAL,
            symmetry REAL,
            risk TEXT,
            risk_score REAL,
            movement_quality REAL,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- DASHBOARD ----------------

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# ---------------- MANUAL AI ANALYSIS ----------------

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    patient_id = data.get("patient_id", "P001")
    age = int(data.get("age", 0))

    step_count = float(data["step_count"])
    cadence = float(data["cadence"])
    balance = float(data["balance"])
    symmetry = float(data["symmetry"])

    features = [[
        step_count,
        cadence,
        balance,
        symmetry
    ]]

    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]

    risk_score = round(probability * 100, 2)

    risk = "Higher Risk" if prediction == 1 else "Lower Risk"

    movement_quality = round(
        (balance + symmetry) / 2,
        2
    )

    # Save assessment
    conn = sqlite3.connect("ortho_data.db")

    conn.execute("""
        INSERT INTO assessments
        (
            patient_id,
            age,
            step_count,
            cadence,
            balance,
            symmetry,
            risk,
            risk_score,
            movement_quality,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        age,
        step_count,
        cadence,
        balance,
        symmetry,
        risk,
        risk_score,
        movement_quality,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "risk": risk,
        "risk_score": risk_score,
        "movement_quality": movement_quality,
        "step_count": step_count,
        "cadence": cadence,
        "balance": balance,
        "symmetry": symmetry
    })


# ---------------- SENSOR DATA ----------------

@app.route("/sensor-data", methods=["POST"])
def sensor_data():

    global latest_sensor_data

    data = request.get_json()

    step_count = float(data.get("step_count", 0))
    cadence = float(data.get("cadence", 0))
    balance = float(data.get("balance", 0))
    symmetry = float(data.get("symmetry", 0))

    # Store latest sensor values
    latest_sensor_data = {
        "step_count": step_count,
        "cadence": cadence,
        "balance": balance,
        "symmetry": symmetry
    }

    # AI analysis
    features = [[
        step_count,
        cadence,
        balance,
        symmetry
    ]]

    prediction = model.predict(features)[0]

    probability = model.predict_proba(features)[0][1]

    risk_score = round(
        probability * 100,
        2
    )

    risk = "Higher Risk" if prediction == 1 else "Lower Risk"

    movement_quality = round(
        (balance + symmetry) / 2,
        2
    )

    return jsonify({
        "status": "success",
        "risk": risk,
        "risk_score": risk_score,
        "movement_quality": movement_quality,
        "step_count": step_count,
        "cadence": cadence,
        "balance": balance,
        "symmetry": symmetry
    })


# ---------------- LATEST SENSOR DATA ----------------

@app.route("/latest-sensor", methods=["GET"])
def latest_sensor():

    return jsonify(latest_sensor_data)


# ---------------- HISTORY ----------------

@app.route("/history")
def history():

    conn = sqlite3.connect("ortho_data.db")

    conn.row_factory = sqlite3.Row

    records = conn.execute("""
        SELECT *
        FROM assessments
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "history.html",
        records=records
    )


# ---------------- START SERVER ----------------

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
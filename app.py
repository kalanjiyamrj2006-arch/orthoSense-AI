from flask import Flask, render_template, request, jsonify
import joblib
import sqlite3
from datetime import datetime

app = Flask(__name__)

# =========================================================
# LOAD AI MODEL
# =========================================================

model = joblib.load("ortho_model.pkl")


# =========================================================
# LATEST SENSOR DATA
# =========================================================

latest_sensor_data = {
    "step_count": 0,
    "cadence": 0,
    "balance": 0,
    "symmetry": 0,
    "risk": "Waiting...",
    "risk_score": 0,
    "movement_quality": 0
}


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

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


# =========================================================
# AI MOVEMENT ANALYSIS
# =========================================================

def analyze_movement(
    step_count,
    cadence,
    balance,
    symmetry
):

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

    if prediction == 1:
        risk = "Higher Risk"
    else:
        risk = "Lower Risk"

    movement_quality = round(
        (balance + symmetry) / 2,
        2
    )

    return (
        risk,
        risk_score,
        movement_quality
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def dashboard():

    return render_template(
        "dashboard.html"
    )


# =========================================================
# MANUAL AI ANALYSIS
# =========================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    data = request.get_json()

    patient_id = data.get(
        "patient_id",
        "P001"
    )

    age = int(
        data.get(
            "age",
            0
        )
    )

    step_count = float(
        data.get(
            "step_count",
            0
        )
    )

    cadence = float(
        data.get(
            "cadence",
            0
        )
    )

    balance = float(
        data.get(
            "balance",
            0
        )
    )

    symmetry = float(
        data.get(
            "symmetry",
            0
        )
    )

    # AI analysis

    risk, risk_score, movement_quality = analyze_movement(
        step_count,
        cadence,
        balance,
        symmetry
    )

    # Save to database

    conn = sqlite3.connect(
        "ortho_data.db"
    )

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
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    ))

    conn.commit()
    conn.close()

    return jsonify({

        "risk": risk,

        "risk_score":
            risk_score,

        "movement_quality":
            movement_quality,

        "step_count":
            step_count,

        "cadence":
            cadence,

        "balance":
            balance,

        "symmetry":
            symmetry

    })


# =========================================================
# LIVE AI PREDICTION
# =========================================================

@app.route(
    "/live-predict",
    methods=["POST"]
)
def live_predict():

    data = request.get_json()

    step_count = float(
        data.get(
            "step_count",
            0
        )
    )

    cadence = float(
        data.get(
            "cadence",
            0
        )
    )

    balance = float(
        data.get(
            "balance",
            0
        )
    )

    symmetry = float(
        data.get(
            "symmetry",
            0
        )
    )

    risk, risk_score, movement_quality = analyze_movement(
        step_count,
        cadence,
        balance,
        symmetry
    )

    return jsonify({

        "risk": risk,

        "risk_score":
            risk_score,

        "movement_quality":
            movement_quality,

        "step_count":
            step_count,

        "cadence":
            cadence,

        "balance":
            balance,

        "symmetry":
            symmetry

    })


# =========================================================
# SENSOR DATA
# =========================================================

@app.route(
    "/sensor-data",
    methods=["POST"]
)
def sensor_data():

    global latest_sensor_data

    data = request.get_json()

    step_count = float(
        data.get(
            "step_count",
            0
        )
    )

    cadence = float(
        data.get(
            "cadence",
            0
        )
    )

    balance = float(
        data.get(
            "balance",
            0
        )
    )

    symmetry = float(
        data.get(
            "symmetry",
            0
        )
    )

    risk, risk_score, movement_quality = analyze_movement(
        step_count,
        cadence,
        balance,
        symmetry
    )

    latest_sensor_data = {

        "step_count":
            step_count,

        "cadence":
            cadence,

        "balance":
            balance,

        "symmetry":
            symmetry,

        "risk":
            risk,

        "risk_score":
            risk_score,

        "movement_quality":
            movement_quality

    }

    return jsonify({

        "status": "success",

        **latest_sensor_data

    })


# =========================================================
# LATEST SENSOR DATA
# =========================================================

@app.route(
    "/latest-sensor",
    methods=["GET"]
)
def latest_sensor():

    return jsonify(
        latest_sensor_data
    )


# =========================================================
# DASHBOARD STATISTICS
# =========================================================

@app.route("/statistics")
def statistics():

    conn = sqlite3.connect(
        "ortho_data.db"
    )

    total = conn.execute("""
        SELECT COUNT(*)
        FROM assessments
    """).fetchone()[0]

    lower_risk = conn.execute("""
        SELECT COUNT(*)
        FROM assessments
        WHERE risk = 'Lower Risk'
    """).fetchone()[0]

    higher_risk = conn.execute("""
        SELECT COUNT(*)
        FROM assessments
        WHERE risk = 'Higher Risk'
    """).fetchone()[0]

    average_quality = conn.execute("""
        SELECT AVG(movement_quality)
        FROM assessments
    """).fetchone()[0]

    conn.close()

    return jsonify({

        "total_assessments":
            total,

        "lower_risk":
            lower_risk,

        "higher_risk":
            higher_risk,

        "average_quality":
            round(
                average_quality or 0,
                2
            )

    })


# =========================================================
# ASSESSMENT HISTORY
# =========================================================

@app.route("/history")
def history():

    conn = sqlite3.connect(
        "ortho_data.db"
    )

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


# =========================================================
# PATIENT-WISE ASSESSMENTS
# =========================================================

@app.route("/patient/<patient_id>")
def patient_details(patient_id):

    conn = sqlite3.connect(
        "ortho_data.db"
    )

    conn.row_factory = sqlite3.Row

    records = conn.execute("""
        SELECT *
        FROM assessments
        WHERE patient_id = ?
        ORDER BY id DESC
    """, (patient_id,)).fetchall()

    conn.close()

    return render_template(
        "patient_details.html",
        records=records,
        patient_id=patient_id
    )


# =========================================================
# SENSOR MONITOR PAGE
# =========================================================

@app.route("/sensor-monitor")
def sensor_monitor():

    return render_template(
        "sensor_monitor.html"
    )


# =========================================================
# AI ANALYSIS PAGE
# =========================================================

@app.route("/ai-analysis")
def ai_analysis():

    return render_template(
        "ai_analysis.html"
    )


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
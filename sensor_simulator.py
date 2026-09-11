import requests
import random
import time

URL = "http://127.0.0.1:5000/sensor-data"

while True:

    data = {
        "step_count": random.randint(70, 130),
        "cadence": random.randint(60, 90),
        "balance": random.randint(60, 95),
        "symmetry": random.randint(65, 98)
    }

    print("Sending sensor data:")
    print(data)

    try:
        response = requests.post(URL, json=data)
        print("Server:", response.json())

    except Exception as e:
        print("Error:", e)

    time.sleep(3)
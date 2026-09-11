import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

data = {
    "step_count": [80, 100, 120, 60, 90, 110, 70, 130, 55, 115],
    "cadence": [70, 75, 80, 60, 72, 78, 65, 82, 55, 79],
    "balance": [90, 85, 80, 60, 88, 82, 65, 92, 55, 86],
    "symmetry": [95, 90, 85, 65, 92, 88, 70, 96, 60, 89],
    "risk": [0, 0, 0, 1, 0, 0, 1, 0, 1, 0]
}

df = pd.DataFrame(data)

X = df[["step_count", "cadence", "balance", "symmetry"]]
y = df["risk"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, "ortho_model.pkl")

print("AI model trained successfully!")
print("Model saved as ortho_model.pkl")
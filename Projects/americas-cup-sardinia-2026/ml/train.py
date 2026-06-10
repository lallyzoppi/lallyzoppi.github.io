import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

df = pd.read_csv("../data/boat_track.csv")

X = df[["wind_speed", "heading"]]
y = df["speed_knots"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LinearRegression()
model.fit(X_train, y_train)

joblib.dump(model, "model.pkl")

print("R2 score:", model.score(X_test, y_test))

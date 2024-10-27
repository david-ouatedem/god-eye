import tensorflow as tf
from keras import Sequential
# from tensorflow.keras.layers import Dense
import pandas as pd
from keras.src.layers import Dense
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import json

with open("sumo.json", "r") as f:
    traffic_data = json.load(f)

data = pd.DataFrame(traffic_data)
print(data.head())

scaler = MinMaxScaler()
data[['vehicle_count', 'avg_speed', 'traffic_density']] = scaler.fit_transform(data[['vehicle_count', 'avg_speed', 'traffic_density']])

data['label'] = data['traffic_density'].apply(lambda x: 2 if x > 0.75 else (1 if x >= 0.5 else 0))

routes = data['route_id'].unique()
for route in routes:
    route_data = data[data['route_id'] == route]
    route_data[['vehicle_count', 'avg_speed', 'traffic_density']] = scaler.fit_transform(route_data[['vehicle_count', 'avg_speed', 'traffic_density']])


model = Sequential([
    Dense(32, activation='relu', input_shape=(4,)),  # Input : route_id, vehicle_count, avg_speed, traffic_density
    Dense(16, activation='relu'),
    Dense(3, activation='softmax')  # Output : 3 classes (fluide, congestion légère, congestion importante)
])

model.compile(optimizer='adam',loss='sparse_categorical_crossentropy',metrics=['accuracy'])
x = data[['route_id','vehicle_count', 'avg_speed', 'traffic_density']]
y = data['label']

model.fit(x, y, epochs=10, batch_size=4, validation_split=0.2)

def send_route_alert(route, label, alternatives):
    alert_message = {
        "route_id": route,
        "traffic_status": "fluide" if label == 0 else ("congestion légère" if label == 1 else "congestion importante"),
        "recommended_routes": alternatives
    }

    with open("route_alert.json", "w", encoding="utf-8") as outfile:
        json.dump(alert_message, outfile)

model.save('traffic_model.keras')
model = tf.keras.models.load_model('traffic_model.keras')
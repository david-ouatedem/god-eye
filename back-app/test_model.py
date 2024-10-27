import json
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
import sumolib
import traci
import requests
import time
import json


with open("sumo1.json", "r") as f:
    traffic_data = json.load(f)

data_df = pd.DataFrame(traffic_data)

scaler = MinMaxScaler()
data_df[['vehicle_count', 'avg_speed', 'traffic_density']] = scaler.fit_transform(data_df[['vehicle_count', 'avg_speed', 'traffic_density']])

features = data_df[['route_id', 'vehicle_count', 'avg_speed', 'traffic_density']]
route_ids = data_df['route_id']

model = tf.keras.models.load_model('traffic_model.keras')

predictions = model.predict(features)
congestion_labels = predictions.argmax(axis=1)

results = pd.DataFrame({
    'route_id': route_ids,
    'congestion_level': congestion_labels,
    'vehicle_count': data_df['vehicle_count'],
    'avg_speed': data_df['avg_speed'],
    'traffic_density': data_df['traffic_density']
})

def get_recommendations(results):
    recommendations = []
    for _, row in results.iterrows():
        if row['congestion_level'] == 2:
            alternative_routes = results[results['congestion_level'] == 0]['route_id'].tolist()
            recommendations.append({
                'route_id': row['route_id'],
                'status': 'congestion importante',
                'recommended_routes': alternative_routes if alternative_routes else ["Aucune route alternative disponible"]
            })
    return recommendations

recommendations = get_recommendations(results)

while True:
    for recommendation in recommendations:
        print(f"Route : {recommendation['route_id']}, Statut : {recommendation['status']}")
        print("Routes recommandées :", recommendation['recommended_routes'])
        print("_" * 40)

with open("recommendations.json", "w", encoding="utf-8") as f:
    json.dump(recommendations, f, indent=4)

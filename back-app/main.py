import random

import sumolib
import traci
import requests
import time
import json


sumo_config_path = r"C:\Users\USER\Sumo\2024-10-26-09-35-20\osm.sumocfg"

url = 'http://localhost:8080'

traci.start(['sumo-gui', '-c', sumo_config_path])

unique_vehicle_ids = set()

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()

    # Get the current simulation time
    current_time = traci.simulation.getTime()

    # Get the current list of vehicle IDs in the simulation
    vehicle_ids = traci.vehicle.getIDList()

    # Add only new vehicle IDs to the set
    for vehicle_id in vehicle_ids:
        unique_vehicle_ids.add(vehicle_id)  # Duplicates are automatically ignored in a set

    # Calculate average speed of all vehicles
    total_speed = 0.0
    vehicle_count = len(vehicle_ids)  # Total number of vehicles in the current step

    lane_vehicle_count = {}  # Dictionary to store vehicle count per lane
    for vehicle_id in vehicle_ids:
        speed = traci.vehicle.getSpeed(vehicle_id)
        total_speed += speed

        # Get lane ID of each vehicle and count vehicles per lane
        lane_id = traci.vehicle.getLaneID(vehicle_id)
        if lane_id in lane_vehicle_count:
            lane_vehicle_count[lane_id] += 1
        else:
            lane_vehicle_count[lane_id] = 1

    # Calculate the average speed (avoid division by zero)
    avg_speed = total_speed / vehicle_count if vehicle_count > 0 else 0

    # Length of the set gives the unique vehicle count
    unique_vehicle_count = len(unique_vehicle_ids)

    # Calculate traffic density for each lane and prepare JSON data
    data_to_send = []
    for lane_id, count in lane_vehicle_count.items():
        lane_length = traci.lane.getLength(lane_id)
        density = (count / lane_length) * 10 if lane_length > 0 else 0

        # Generate a random unique ID (float or integer)
        unique_id = random.randint(1000, 9999)  # For integer unique ID
        # unique_id = round(random.uniform(1.0, 9.9), 2)  # For float unique ID, adjust range as needed

        # Prepare data as JSON object
        route_data = {
            "route_id": float(unique_id),
            "vehicle_count": count,
            "avg_speed": avg_speed,
            "traffic_density": density,
            "timestamp": current_time
        }
        data_to_send.append(route_data)
        print(route_data)

        with open("sumo1.json", "w", encoding="utf-8") as outfile:
            json.dump(data_to_send, outfile)

    time.sleep(0.1)
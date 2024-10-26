import sumolib
import traci
import json
import requests

# Configuration for SUMO simulation
sumo_config_path = r"C:\Users\USER\Sumo\2024-10-26-10-29-57\osm.sumocfg"

# FastAPI server URL to send data
server_url = "http://localhost:8081/traffic-data"

# Create a set to track unique vehicle IDs
unique_vehicle_ids = set()

def run_simulation():
    # Start SUMO GUI
    traci.start(['sumo-gui', '-c', sumo_config_path])

    global latest_traffic_data  # Store data here for server GET requests

    try:
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()

            # Get the current simulation time
            current_time = traci.simulation.getTime()

            # Get the current list of vehicle IDs in the simulation
            vehicle_ids = traci.vehicle.getIDList()

            # Add only new vehicle IDs to the set
            for vehicle_id in vehicle_ids:
                unique_vehicle_ids.add(vehicle_id)

            # Calculate average speed of all vehicles
            total_speed = 0.0
            vehicle_count = len(vehicle_ids)

            lane_vehicle_count = {}
            for vehicle_id in vehicle_ids:
                speed = traci.vehicle.getSpeed(vehicle_id)
                total_speed += speed

                # Get lane ID of each vehicle and count vehicles per lane
                lane_id = traci.vehicle.getLaneID(vehicle_id)
                lane_vehicle_count[lane_id] = lane_vehicle_count.get(lane_id, 0) + 1

            # Calculate the average speed
            avg_speed = total_speed / vehicle_count if vehicle_count > 0 else 0

            # Prepare data to send
            data_to_send = []
            for lane_id, count in lane_vehicle_count.items():
                lane_length = traci.lane.getLength(lane_id)
                density = count / lane_length if lane_length > 0 else 0

                # Prepare data as JSON object
                route_data = {
                    "route_id": lane_id,
                    "vehicle_count": count,
                    "avg_speed": avg_speed,
                    "traffic_density": density,
                    "timestamp": current_time
                }
                data_to_send.append(route_data)

            # Send data to FastAPI server
            requests.post(server_url, json=data_to_send)

    finally:
        traci.close()

# Entry point to start the simulation
if __name__ == "__main__":
    run_simulation()

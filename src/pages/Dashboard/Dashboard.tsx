"use client";

import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {BarChart, Car, Clock, Gauge} from "lucide-react";
import {useEffect, useState, useMemo} from "react";
import "leaflet/dist/leaflet.css"
import {MapContainer, Marker, Popup, TileLayer} from 'react-leaflet'

// Define the TrafficData interface
interface TrafficData {
    route_id: string;
    vehicle_count: number;
    avg_speed: number;
    traffic_density: number;
    timestamp: number;
}

// Create a separate component for individual statistics
const StatCard = ({
                      name,
                      value,
                      Icon,
                  }: {
    name: string;
    value: number | string | undefined;
    Icon: any;
}) => (
    <Card className="overflow-hidden">
        <CardContent className="p-4">
            <div className="flex items-center space-x-4">
                <div className="p-2 bg-primary rounded-full">
                    <Icon className="h-6 w-6 text-primary-foreground"/>
                </div>
                <div>
                    <p className="text-sm font-medium text-muted-foreground">{name}</p>
                    <p className="text-2xl font-bold">{value ?? "N/A"}</p>
                </div>
            </div>
        </CardContent>
    </Card>
);

export default function Dashboard() {
    const [trafficData, setTrafficData] = useState<TrafficData[]>([]);
    const [latestData, setLatestData] = useState<TrafficData | null>(null);

    // Fetch traffic data at specified intervals
    const fetchTrafficData = async () => {
        try {
            const response = await fetch("http://localhost:8081/traffic-data");
            if (!response.ok) throw new Error("Network response was not ok");
            const data = await response.json();
            setTrafficData(data.traffic_data);
        } catch (error) {
            console.error("Error fetching traffic data:", error);
        }
    };

    // Set an interval to fetch data every 10 seconds
    useEffect(() => {
        fetchTrafficData(); // Initial fetch
        const intervalId = setInterval(fetchTrafficData, 10000); // Fetch data every 10 seconds
        return () => clearInterval(intervalId); // Clear interval on component unmount
    }, []);

    // Update latestData with the most recent entry from trafficData
    useEffect(() => {
        if (trafficData.length > 0) {
            setLatestData(trafficData[trafficData.length - 1]);
        }
    }, [trafficData]);

    // Calculate total vehicle count and average speed
    const totalVehicleCount = useMemo(() => {
        return trafficData.reduce((sum, data) => sum + data.vehicle_count, 0);
    }, [trafficData]);

    const averageSpeed = useMemo(() => {
        if (trafficData.length === 0) return 0;
        const totalSpeed = trafficData.reduce(
            (sum, data) => sum + data.avg_speed,
            0
        );
        return totalSpeed / trafficData.length; // Average speed calculation
    }, [trafficData]);

    const stats = useMemo(
        () => [
            {
                name: "Total Vehicles",
                value: totalVehicleCount,
                icon: Car,
            },
            {
                name: "Average Speed",
                value: `${averageSpeed.toFixed(2)} mph`, // Format average speed to 2 decimal places
                icon: Gauge,
            },
            {
                name: "Traffic Density",
                value: latestData?.traffic_density.toFixed(2) ?? 0,
                icon: BarChart,
            },
            {
                name: "Last Updated",
                value: latestData
                    ? new Date(latestData.timestamp * 1000).toLocaleString()
                    : "-",
                icon: Clock,
            },
        ],
        [totalVehicleCount, averageSpeed, latestData]
    );


    return (
        <div className="px-4">
            <div className="h-12 flex items-center justify-start">
                <h1 className="text-2xl font-bold">Traffic Tracking Panel</h1>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 min-h-[calc(100vh-48px)]">
                <Card className="md:col-span-2">
                    <CardContent className="p-0 overflow-hidden">
                        <MapContainer className="leaflet-container" center={[4.04505, 9.71891]} zoom={13} scrollWheelZoom={false}>
                            <TileLayer
                                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            />
                            <Marker position={[4.04505, 9.71891]}>
                                 <Popup>
                                 https://www.openstreetmap.org/copyright
                                    A pretty CSS3 popup. <br/> Easily customizable.
                                </Popup>
                             </Marker>
                        </MapContainer>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <CardTitle>Traffic Statistics</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex flex-col gap-4">
                            {stats.map((stat) => (
                                <StatCard
                                    key={stat.name}
                                    name={stat.name}
                                    value={stat.value}
                                    Icon={stat.icon}
                                />
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

import paho.mqtt.client as mqtt
import csv
import json
from datetime import datetime
import portalocker

MQTT_HOST = "broker.mqttdashboard.com"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 45 #45 seconds
MQTT_TOPIC = "CPE_DEMO_HOUSE/#"
CSV_FILE = "sensor_data.csv"

def on_connect(self,client, userdata, rc):
    print("MQTT Connected.")
    self.subscribe(MQTT_TOPIC)
    # add more subscribe ...
    # e.g.;
    # self.subscribe("CPE_DEMO_HOUSE/room2/#")

def on_message(client, userdata, msg):
    print("message received...")
    print(msg.topic + " "+ str(msg.qos) + " " + str(msg.payload.decode("utf-8","strict")))

     # Try parsing the message payload as JSON
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        topic = msg.topic
        temperature = data.get("Temperature", "N/A")
        humidity = data.get("Humidity", "N/A")
        light = data.get("Light", "N/A")

        # Open CSV in append mode and write the data
        with open(CSV_FILE, mode='a', newline='') as file:
            # Acquire file lock
            portalocker.lock(file, portalocker.LOCK_EX)
            
            writer = csv.writer(file)
            # Write headers if the file is empty
            if file.tell() == 0:
                writer.writerow(["Timestamp", "Topic", "Temperature", "Humidity", "Light"])
            # Write the data row
            writer.writerow([timestamp, topic, temperature, humidity, light])
            # Release file lock
            portalocker.unlock(file)

        print(f"Data written to {CSV_FILE}: {timestamp}, {topic}, {temperature}, {humidity}, {light}")

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST)
client.loop_forever()

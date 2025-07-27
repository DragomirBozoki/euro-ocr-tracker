#!/usr/bin/env python3
"""
Send a YAML configuration file over MQTT as a JSON payload at a fixed interval.
"""

import json
import time
import yaml
import paho.mqtt.client as mqtt


MQTT_BROKER = "test.mosquitto.org"   # Change to your broker (e.g., "localhost")
MQTT_PORT = 1883
MQTT_TOPIC = "test/ocr/config"       # Topic to publish the config to


def on_connect(client, userdata, flags, rc):
    """MQTT callback: called when the client connects to the broker."""
    if rc == 0:
        print("✔ Connected to MQTT broker")
    else:
        print(f"✖ Failed to connect, return code = {rc}")


def main():
    # 1) Load YAML config
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 2) Convert to JSON (MQTT messages are typically strings/bytes)
    payload = json.dumps(config, indent=2)
    print("MQTT PAYLOAD TO BE SENT:\n", payload)

    # 3) Create and configure MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect

    # (Optional) Last Will & Testament: if this publisher dies, broker will emit this message
    client.will_set(MQTT_TOPIC, payload='{"status":"publisher_down"}', qos=0, retain=False)

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    # Start a background network loop so publish() works without blocking
    client.loop_start()

    try:
        # 4) Publish the same payload every `interval` seconds
        interval = config.get("interval", 5)
        print(f"▶ Publishing every {interval}s. Press Ctrl+C to stop.\n")

        while True:
            # You can add a timestamp if you want each message to differ:
            # msg = {"ts": time.time(), "config": config}
            # payload = json.dumps(msg)

            client.publish(MQTT_TOPIC, payload)
            print(f"✓ Published to {MQTT_TOPIC}")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n■ Stopped by user.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()

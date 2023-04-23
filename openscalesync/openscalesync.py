import time
import argparse
import threading
import support.utils.config as config_utils
import support.utils.scale as scale_utils
import support.scales.scale
import paho.mqtt.client as mqtt

if __name__ == '__main__':
  # Parse command line arguments
  parser = argparse.ArgumentParser(description='OpenScaleSync')
  parser.add_argument('-c', '--config', help='Path to config file', required=True)
  parser.add_argument('-d', '--debug', help='Enable debug logging', action='store_true')
  args = parser.parse_args()

  # Load config
  config = config_utils.load_config(args.config)

  # Connect to mqtt broker
  mqtt_client = mqtt.Client()
  mqtt_client.username_pw_set(config['mqtt']['username'], config['mqtt']['password'])
  print('Connecting to MQTT broker...')
  mqtt_client.connect(config['mqtt']['host'], config['mqtt']['port'], 60)
  print('Connected to MQTT broker')

  topic_namespace = f"{config['mqtt']['topic']}/"
  def topic(*topic: str):
    if args.debug:
      print(f"Topic: {topic_namespace}{'/'.join(topic)}")
    return f"{topic_namespace}{'/'.join(topic)}"

  # Broadcast to topic
  mqtt_client.publish(topic('status'), 'OK')
  if args.debug:
    print('Debug mode enabled')
    mqtt_client.publish(topic('debug'), 'ON')

  # Start mqtt loop
  mqtt_client.loop_start()

  state = { 'last_mass': None }
  # Define a function to publish the mass to mqtt
  def publish_mass(scale: support.scales.scale.Scale, mass: float):
    if args.debug:
      print(f"Mass: {mass}kg, Weight: {mass * 2.20462}lbs")

    mqtt_client.publish(topic(config['scale']['topic'], 'mass'), mass)
    mqtt_client.publish(topic(config['scale']['topic'], 'weight'), mass * 2.20462)

    if state['last_mass'] and (mass - state['last_mass']) > 1:
      mqtt_client.publish(topic(config['scale']['topic'], 'mass_delta'), mass - state['last_mass'])
      mqtt_client.publish(topic(config['scale']['topic'], 'weight_delta'), (mass - state['last_mass']) * 2.20462)

    state['last_mass'] = mass
    scale.disconnect()

  scale = scale_utils.load_scale(config['scale'])
  scale.on_measurement(publish_mass)

  def status_loop():
    last_connected = False
    mqtt_client.publish(topic(config['scale']['topic'], 'connected'), 0)

    while True:
      if scale.connected != last_connected:
        mqtt_client.publish(topic(config['scale']['topic'], 'connected'), 1 if scale.connected else 0)
        last_connected = scale.connected
      time.sleep(0.5)

  # Start status loop
  status_thread = threading.Thread(target=status_loop, daemon=True)
  status_thread.start()

  while True:
    time.sleep(1)


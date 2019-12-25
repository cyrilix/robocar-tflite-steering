"""
Compute steering from camera images

Usage:
rc-keras-steering.py (-u USERNAME | --mqtt-username=USERNAME) --mqtt-password=PASSWORD --mqtt-broker=HOSTNAME --mqtt-topic-steering=TOPIC_STEERING

Options:
-h --help                                       Show this screen.
-u USERID --mqtt-username=USERNAME              MQTT user
-p PASSWORD --mqtt-password=PASSWORD            MQTT password
-b HOSTNAME --mqtt-broker=HOSTNAME              MQTT broker host
-C CLIENT_ID --mqtt-client-id=CLIENT_ID         MQTT client id
-m MODEL_PATH --tf-model-path                   Tensorflow model path
-s TOPIC_STEERING --mqtt-topic-steering         MQTT topic to publish steering value
-c TOPIC_CAMERA --mqtt-topic-camera             MQTT topic where to read camera frames
"""
import json
import logging
import os

from docopt import docopt
import paho.mqtt.client as mqtt

from steering.tensorflowlite import SteeringPart

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

default_client_id = "robocar-tflite-steering"


def start_mqtt_client(broker_host: str, user: str, password: str, client_id: str, part: SteeringPart,
                      camera_topic: str, steering_topic: str):
    logger.info("Start tflite-steering part")
    client = mqtt.Client(client_id=client_id, clean_session=True, userdata=None, protocol=mqtt.MQTTv311)
    client.username_pw_set(username=user, password=password)

    def on_message(mqtt_client: mqtt.Client, userdata: SteeringPart, msg: mqtt.MQTTMessage):
        steering = userdata.get_steering(msg.payload)
        payload = json.dumps(steering)

        mqtt_client.publish(topic=steering_topic,
                            payload=payload,
                            qos=0,
                            retain=False)

    client.user_data_set(part)
    client.username_pw_set(user, password)
    client.message_callback_add(camera_topic, on_message)
    client.connect(host=broker_host, port=1883, keepalive=60)
    client.loop_forever()

    return client


def execute_from_command_line():
    args = docopt(__doc__)
    steering_part = SteeringPart(model_path=args["--tf-model-path"])

    start_mqtt_client(broker_host=get_default_value(args["--mqtt-broker"], "MQTT_BROKER","localhost"),
                      user=get_default_value(args["--mqtt-username"], "MQTT_USERNAME", ""),
                      password=get_default_value(args["--mqtt-password"], "MQTT_PASSWORD", ""),
                      client_id=get_default_value(args["--mqtt-client-id"], "MQTT_CLIENT_ID", default_client_id),
                      steering_topic=get_default_value(args["--mqtt-topic-steering"], "MQTT_STEERING_TOPIC", "/steering"),
                      camera_topic=get_default_value(args["--mqtt-topic-camera"], "MQTT_CAMERA_TOPIC", "/camera"),
                      part=steering_part
                      )


def get_default_value(value, env_var:str, default_value):
    if value:
        return value
    if env_var in os.environ:
        return os.environ[env_var]
    return default_value

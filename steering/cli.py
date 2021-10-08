"""
Compute steering from camera images

Usage:
rc-tflite-steering [-u USERNAME | --mqtt-username=USERNAME] [--mqtt-password=PASSWORD] [--mqtt-broker=HOSTNAME] [--mqtt-topic-camera="TOPIC_CAMERA"] [--mqtt-topic-steering=TOPIC_STEERING] [--mqtt-client-id=CLIENT_ID] [--tf-model-path=MODEL_PATH]

Options:
-h --help                                               Show this screen.
-u USERID --mqtt-username=USERNAME                      MQTT user
-p PASSWORD --mqtt-password=PASSWORD                    MQTT password
-b HOSTNAME --mqtt-broker=HOSTNAME                      MQTT broker host
-C CLIENT_ID --mqtt-client-id=CLIENT_ID                 MQTT client id
-m MODEL_PATH --tf-model-path=MODEL_PATH                Tensorflow model path
-s TOPIC_STEERING --mqtt-topic-steering=TOPIC_STEERING  MQTT topic to publish steering value
-c TOPIC_CAMERA --mqtt-topic-camera=TOPIC_CAMERA        MQTT topic where to read camera frames
"""
import logging
import os
import time
from io import BytesIO
from queue import Queue
from threading import Thread

import numpy as np
from PIL import Image
from docopt import docopt
import paho.mqtt.client as mqtt
from events import events_pb2

from steering.tensorflowlite import SteeringPart, configure_interpreter

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

default_client_id = "robocar-tflite-steering"


def init_mqtt_client(queue: Queue, broker_host: str, user: str, password: str, client_id: str,
                     camera_topic: str) -> mqtt.Client:
    logger.info("Start tflite-steering part")
    client = mqtt.Client(client_id=client_id, clean_session=True, userdata=None, protocol=mqtt.MQTTv311)

    def on_connect(client, userdata, flags, rc):
        logger.info("Register callback on topic %s", camera_topic)
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(camera_topic)

    def on_message(mqtt_client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        if not queue.empty():
            logger.debug("too many frames to process, skip frame")
            return
        try:
            queue.put(msg.payload, block=False, timeout=0)
        except:
            logger.debug("unexpected error: too many frames to process, skip frame")

    client.username_pw_set(user, password)
    client.on_connect = on_connect
    client.on_message = on_message
    logger.info("Connect to mqtt broker")
    client.connect(host=broker_host, port=1883, keepalive=60)
    logger.info("Connected to mqtt broker")
    return client


class FrameProcessor(Thread):
    def __init__(self, mqtt_client: mqtt.Client, queue: Queue, part: SteeringPart, steering_topic: str):
        super().__init__(name="FrameProcessor")
        self._mqtt_client = mqtt_client
        self._part = part
        self._steering_topic = steering_topic
        self._queue = queue

    def run(self):
        logger.info("start frame processing")
        while True:
            try:
                try:
                    payload = self._queue.get(timeout=0.5)
                except:
                    logger.warn('unexpected timeout')
                    continue

                msg_frame = events_pb2.FrameMessage()
                msg_frame.ParseFromString(payload)

                content = BytesIO(msg_frame.frame)
                img = np.array(Image.open(content))

                start = time.time_ns()
                steering = self._part.get_steering(img)
                end = time.time_ns()
                logger.debug("steering computed in %s ns", str(end - start))
                steering_msg = events_pb2.SteeringMessage()
                steering_msg.steering = steering.value
                steering_msg.confidence = steering.confidence
                steering_msg.frame_ref.CopyFrom(msg_frame.id)
                logger.debug("new steering '%s(%s)' processed from img %s", str(steering.value),
                             str(steering.confidence),
                             str(msg_frame.id))

                self._mqtt_client.publish(topic=self._steering_topic,
                                          payload=steering_msg.SerializeToString(),
                                          qos=0,
                                          retain=False)
            except Exception as e:
                logger.exception("unexpected error")


def execute_from_command_line():
    logging.basicConfig(level=logging.INFO)

    args = docopt(__doc__)
    model_path = get_default_value(args["--tf-model-path"], "TF_MODEL_PATH", "")
    steering_part = SteeringPart(configure_interpreter(model_path, True))

    queue = Queue(maxsize=1)
    client = init_mqtt_client(queue=queue,
                              broker_host=get_default_value(args["--mqtt-broker"], "MQTT_BROKER", "localhost"),
                              user=get_default_value(args["--mqtt-username"], "MQTT_USERNAME", ""),
                              password=get_default_value(args["--mqtt-password"], "MQTT_PASSWORD", ""),
                              client_id=get_default_value(args["--mqtt-client-id"], "MQTT_CLIENT_ID",
                                                          default_client_id),
                              camera_topic=get_default_value(args["--mqtt-topic-camera"], "MQTT_TOPIC_CAMERA",
                                                             "/camera")
                              )
    steering_topic = get_default_value(args["--mqtt-topic-steering"], "MQTT_TOPIC_STEERING", "/steering")

    frame_processor = FrameProcessor(mqtt_client=client, queue=queue, part=steering_part, steering_topic=steering_topic)
    frame_processor.start()

    client.loop_forever()


def get_default_value(value, env_var: str, default_value) -> str:
    if value:
        return value
    if env_var in os.environ:
        return os.environ[env_var]
    return default_value

import logging
from collections import namedtuple
from pathlib import Path

import numpy as np
import tflite_runtime.interpreter as tflite

logger = logging.getLogger(__name__)

Steering = namedtuple("Steering", "value confidence")


class SteeringPart:

    def __init__(self, model_path: Path):
        logger.info("init steering part")
        logger.info('load model' + str(model_path))
        self.interpreter = tflite.Interpreter(model_path=str(model_path))
        logger.info('model loaded')
        self.interpreter.allocate_tensors()

        # Get input and output tensors.
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

    def get_steering(self, img: np.array) -> Steering:
        # Get input and output tensors.
        img_arr = img.reshape((1,) + img.shape)
        img_arr = np.float32(img_arr)

        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        input_shape = input_details[0]['shape']
        self.interpreter.set_tensor(input_details[0]['index'], img_arr)

        self.interpreter.invoke()

        # The function `get_tensor()` returns a copy of the tensor data.
        # Use `tensor()` in order to get a pointer to the tensor.
        output_data = self.interpreter.get_tensor(output_details[0]['index'])
        print(output_data)
        return linear_unbin(output_data)


def example():
    # Load TFLite model and allocate tensors.
    interpreter = tflite.Interpreter(model_path="converted_model.tflite")
    interpreter.allocate_tensors()

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Test model on random input data.
    input_shape = input_details[0]['shape']
    input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)

    interpreter.invoke()

    # The function `get_tensor()` returns a copy of the tensor data.
    # Use `tensor()` in order to get a pointer to the tensor.
    output_data = interpreter.get_tensor(output_details[0]['index'])
    print(output_data)


def linear_unbin(arr) -> Steering:
    b = np.argmax(arr)
    a = float(b) * (2. / 14.) - 1.
    return Steering(a, arr[0][b])

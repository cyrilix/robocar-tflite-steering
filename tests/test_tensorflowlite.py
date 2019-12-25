import os
from array import array

import numpy as np
from PIL import Image
from pathlib import Path
from pytest import fixture

from steering.tensorflowlite import SteeringPart


def _base_path() -> Path:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    return Path(path)


@fixture(name='model_path')
def model_path() -> Path:
    return _base_path().joinpath('tests', 'data', 'model.tflite')


@fixture(name='img')
def img() -> np.array:
    img_path = _base_path().joinpath('tests', 'data', 'image.jpg')
    img = Image.open(str(img_path))
    return np.array(img)


@fixture(name='img_reverse')
def img_reverse() -> np.array:
    img_path = _base_path().joinpath('tests', 'data', 'image-reverse.jpg')
    img = Image.open(str(img_path))
    return np.array(img)


class TestTensorflowLite:

    def test_get_steering(self, model_path: Path, img: array, img_reverse: array):
        steering_part = SteeringPart(model_path=model_path)

        steering = steering_part.get_steering(img)
        assert steering.value == 0.
        assert 0.97 > steering.confidence > 0.96

        steering = steering_part.get_steering(img_reverse)
        assert steering.value == 0.
        assert 0.998 > steering.confidence > 0.997

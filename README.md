# robocar-tflite-steering

Compute steering with tensorflow lite
  
## Install

Clone repository and install tensorflowlite pip package as describe on https://www.tensorflow.org/lite/guide/python:

```bash
pip3 install tflite_runtime-1.14.0-cp37-cp37m-linux_armv7l.whl
```

## Docker

To build images, run:
```bash 
docker buildx build . --platform linux/arm/7,linux/arm64,linux/amd64 -t cyrilix/robocar-tflite-steering
steering
```

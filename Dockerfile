FROM python:3.7-alpine


WORKDIR /src

RUN wget https://dl.google.com/coral/python/tflite_runtime-1.14.0-cp37-cp37m-linux_$(uname -m).whl && \
    pip3 install tflite_runtime-1.14.0-cp37-cp37m-linux_$(uname -m).whl && \
    apk add -U py3-numpy py3-pillow

ADD . .
RUN python3 setup.py install && rm -rf /src

WORKDIR /tmp
USER 1234

ENTRYPOINT ["/usr/local/bin/rc-tflite-steering"]

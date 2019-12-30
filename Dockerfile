FROM cyrilix/numpy

WORKDIR /tmp

RUN wget https://dl.google.com/coral/python/tflite_runtime-1.14.0-cp37-cp37m-linux_$(uname -m).whl && \
    pip3 install tflite_runtime-1.14.0-cp37-cp37m-linux_$(uname -m).whl && \
    apt-get update && apt-get install -y python3-pillow && \
    pip3 install numpy

ADD . .
RUN python3 setup.py install && rm -rf /src

WORKDIR /tmp
USER 1234

ENTRYPOINT ["/usr/local/bin/rc-tflite-steering"]

FROM cyrilix/robocar-python-base

ADD . .
RUN python3 setup.py install && rm -rf /src

ENV PYTHON_EGG_CACHE=/tmp/cache

WORKDIR /tmp
USER 1234
RUN mkdir -p ${PYTHON_EGG_CACHE}

ENTRYPOINT ["/usr/local/bin/rc-tflite-steering"]

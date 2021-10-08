#FROM cyrilix/robocar-python-base
FROM docker.io/library/python:3.9-slim

# Configure piwheels repo to use pre-compiled numpy wheels for arm
RUN echo -n "[global]\nextra-index-url=https://www.piwheels.org/simple\n" >> /etc/pip.conf

RUN apt-get update && apt-get install -y curl gnupg

RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" > /etc/apt/sources.list.d/coral-edgetpu.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && \
    apt-get install -y libedgetpu1-std


RUN pip3 install numpy pillow
RUN pip3 install --index-url https://google-coral.github.io/py-repo/ tflite_runtime

ADD events .
ADD steering .
ADD Pipfile .
ADD setup.cfg .
ADD setup.py .


RUN python3 setup.py install && rm -rf /src
ENV PYTHON_EGG_CACHE=/tmp/cache

WORKDIR /tmp
USER 1234
RUN mkdir -p ${PYTHON_EGG_CACHE}

ENTRYPOINT ["/usr/local/bin/rc-tflite-steering"]

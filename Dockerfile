# https://github.com/intezer/docker-ida/blob/master/ida-base/Dockerfile

FROM debian:10

ARG IDA_PASSWORD

# Add 32 bit architecture support for IDA
RUN dpkg --add-architecture i386 && apt-get -y update

# Replace the python version in the original image with a 32-bit version, so when we install external libraries -
# IDAPython (32bit) could import them
RUN apt-get -y install python2.7-minimal:i386 python2.7:i386

# Create a symlink for python for convenience (instead of typing python2.7)
RUN link /usr/bin/python2.7 /usr/bin/python

# Install necessary libraries for IDA and IDAPython to work
RUN apt-get -y install --fix-missing \
    lib32gcc1 \
    libc6-i686:i386 \
    libfontconfig:i386 \
    libfreetype6:i386 \
    libglib2.0-0:i386 \
    libpython2.7:i386 \
    libsm6:i386 \
    libssl-dev:i386 \
    libstdc++6:i386 \
    libxext6:i386 \
    libxrender1:i386 \
    python-dev \
	libssl1.1 \
	libssl-dev

# Install pip for python 2.7
RUN apt-get -y install python-pip
RUN pip2 install --upgrade pip

RUN apt-get -y install python3 python3-pip
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools

# install IDA
RUN mkdir /ida
COPY ida.run /
RUN chmod +x /ida.run
RUN printf "\n\n\n\n\n\ny\n$IDA_PASSWORD\n/ida\ny\ny\n" | /ida.run
RUN touch /ida/license.displayed

COPY decompile.py /

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN mkdir /app
COPY . /app/

WORKDIR /app
RUN python3 -m pip install -r requirements.txt

EXPOSE 8000
CMD flask db-init && gunicorn -w 2 -b 0.0.0.0:8000 "daas:create_app()"

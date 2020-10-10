FROM ubuntu:focal

RUN apt -y update
RUN apt install python3 python3-pip
COPY . /opt/build/python-rfb

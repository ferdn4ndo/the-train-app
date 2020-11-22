FROM ubuntu:20.04

LABEL maintaner="const.fernando@gmail.com"
LABEL version="1.0"
LABEL description="TheTrainSim App"

ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt update && \
	apt -y upgrade && \
	apt -y install \
	bash \
	gcc \
	git \
	libc-dev \
	libxslt-dev \
	libxml2-dev \
	ffmpeg \
	graphviz \
	python3 \
	python3-pip \
	libopencv-dev \
	python3-opencv \
	&& \
	rm -rf /var/cache/apk/*

COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

WORKDIR /code

ENTRYPOINT [ "/code/entrypoint.sh" ]


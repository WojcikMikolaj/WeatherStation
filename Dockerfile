FROM python:3.8

WORKDIR /usr/src/WeatherStation

COPY config config

COPY main.py main.py

RUN mkdir logs

CMD python3 main.py -l=Warsaw
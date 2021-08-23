FROM python:3.8

WORKDIR /usr/src/WeatherStation

COPY config config

COPY main.py main.py

EXPOSE 4000/udp

RUN pip install --no-cache-dir requests argparse
RUN mkdir logs

CMD python3 main.py -l=Warsaw
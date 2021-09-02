FROM python:3.8

WORKDIR /usr/src/WeatherStation

COPY config config

COPY *.py ./

EXPOSE 4000/udp
EXPOSE 4001/udp
EXPOSE 4001/tcp

RUN pip install --no-cache-dir requests argparse

VOLUME ["/usr/src/WeatherStation/logs"]

CMD python3 main.py -l=Warsaw
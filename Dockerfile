FROM python:3.8

WORKDIR /usr/src/WeatherStation

COPY config config

COPY *.py ./

EXPOSE 4000/udp

RUN pip install --no-cache-dir requests argparse
RUN mkdir logs

VOLUME ~/WeatherStation/logs ./logs

CMD python3 main.py -l=Warsaw
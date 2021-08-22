FROM python:3.8

WORKDIR /usr/src/WeatherStation

COPY config config

COPY main.py main.py

RUN pip install --no-cache-dir requests argparse logging time
RUN mkdir logs

CMD python3 main.py -l=Warsaw
FROM python:slim

MAINTAINER LightQuantum

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY sjtu_traffic_exporter ./sjtu_traffic_exporter

CMD ["gunicorn", "-b", "0.0.0.0:9142", "sjtu_traffic_exporter:app"]

FROM python:3.9.2-slim-buster

COPY . /configuration_controller

WORKDIR /configuration_controller

RUN pip3 install --upgrade pip --no-cache-dir -r requirements.txt

ENV PYTHONPATH=$PYTHONPATH:/

ENTRYPOINT ["python", "run.py", "-m", "Hello World"]

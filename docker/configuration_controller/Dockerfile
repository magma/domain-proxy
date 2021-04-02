FROM python:3.9.2-slim-buster

COPY ./backend/configuration_controller /backend/configuration_controller

WORKDIR /backend/configuration_controller

RUN pip3 install --upgrade pip --no-cache-dir -r requirements.txt

ENV PYTHONPATH=$PYTHONPATH:/backend

ENTRYPOINT ["python", "run.py", "-m", "Hello World"]

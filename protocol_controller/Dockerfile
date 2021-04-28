ARG ENV=standard
FROM python:3.9.2-slim-buster as standard-version

COPY . /protocol_controller
WORKDIR /protocol_controller
RUN pip3 install --upgrade pip --no-cache-dir -r requirements.txt

FROM standard-version as tests-version
RUN pip3 install --upgrade pip --no-cache-dir -r tests/requirements.txt

FROM ${ENV}-version as final
ENV PYTHONPATH=$PYTHONPATH:/

EXPOSE 8000

ENTRYPOINT ["python"]
CMD ["run.py"]

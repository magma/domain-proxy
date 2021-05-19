ARG ENV=standard
FROM python:3.9.2-slim-buster as standard-version

COPY configuration_controller /configuration_controller
COPY db /db
WORKDIR /configuration_controller
RUN pip3 install --upgrade pip --no-cache-dir -r requirements.txt

FROM standard-version as tests-version
RUN pip3 install --upgrade pip --no-cache-dir -r tests/requirements.txt

FROM ${ENV}-version as final
ENV PYTHONPATH=$PYTHONPATH:/
ENTRYPOINT ["python"]
CMD ["run.py"]

ARG ENV=standard
FROM python:3.9.2-slim-buster as standard-version

COPY protocol_controller /protocol_controller
COPY protobufs /protobufs
WORKDIR /protocol_controller
RUN pip3 install --upgrade pip --no-cache-dir -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs/requests --python_out=. --grpc_python_out=. ../protobufs/requests/requests.proto

FROM standard-version as tests-version
RUN pip3 install --upgrade pip --no-cache-dir -r plugins/cbsd_sas/tests/requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs/requests --python_out=. --grpc_python_out=. ../protobufs/requests/requests.proto

FROM ${ENV}-version as final
ENV PYTHONPATH=$PYTHONPATH:/

EXPOSE 8000

CMD ["python", "service.py"]

ARG ENV=standard
FROM python:3.9.2-slim-buster as builder

COPY db_service /db_service
COPY mappings /mappings
WORKDIR /db_service/migrations
RUN pip3 install --upgrade pip --no-cache-dir -r ../requirements.txt

FROM builder as final
ENV PYTHONPATH=$PYTHONPATH:/
ENV ALEMBIC_CONFIG=./alembic.ini

ENTRYPOINT ["python"]
CMD ["../db_initialize.py"]
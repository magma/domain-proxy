FROM python:2.7.18-alpine3.11 as builder

RUN apk add --no-cache \
	gcc=9.3.0-r0 \
	musl-dev=1.1.24-r3 \
	libffi-dev=3.2.1-r6 \
	openssl-dev=1.1.1k-r0 \
	&& pip install virtualenv

RUN virtualenv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

FROM python:2.7.18-alpine3.11

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN mkdir /opt/server  && chown -R nobody /opt/server
COPY fake_sas.py /opt/server
COPY sas_interface.py /opt/server
COPY sas.cfg /opt/server
EXPOSE 9000
WORKDIR /opt/server
USER nobody
ENTRYPOINT ["python"]
CMD ["fake_sas.py"]


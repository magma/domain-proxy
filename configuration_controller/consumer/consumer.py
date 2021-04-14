import logging

import pika


logger = logging.getLogger(__name__)


class RequestsConsumer:
    """Consumer for RabbitMQ to receive data
    from multiple queues for every type of request to SAS.

    :param rabbitmq_url: URL qualified address to RabbitMQ instance
    :type rabbitmq_url: str
    """
    request_list = [
        "registrationRequest",
        "spectrumInquiryRequest",
        "grantRequest",
        "heartbeatRequest",
        "relinquishmentRequest",
        "deregistrationRequest",
    ]

    def __init__(self, rabbitmq_url: str):
        self._rabbitmq_url = rabbitmq_url
        self._connection = None
        self._channel = None
        self._create_connection()
        self._create_channel()
        self._received_requests = dict()

    def _create_connection(self):
        """This method creates communication channel to RabbitMQ
        and declares queues for every type of requests.
        Requests queues are based on self._requests list
        and created channel is stored in self._channel.
        """
        logger.info("Creating connection")
        conn_params = pika.ConnectionParameters(self._rabbitmq_url)
        self._connection = pika.BlockingConnection(conn_params)

    def _create_channel(self):
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange='requests', exchange_type='topic')
        for request_name in self.request_list:
            self._set_up_queue(request_name)
        logger.info("Communication channel created successfully")

    def _set_up_queue(self, request_name):
        self._channel.queue_declare(request_name)
        self._channel.queue_bind(
            exchange='requests',
            queue=request_name,
            routing_key=request_name
        )
        self._channel.basic_consume(
            queue=request_name,
            on_message_callback=lambda ch, method, properties, body:
            self._queue_callback(method.routing_key, body),
            auto_ack=True
        )

    def _queue_callback(self, routing_key, body):
        """Callback method for pika channel basic_consume on_message_callback
        This method appends body to proper request string based on routing key

        :param routing_key: RabbitMQ routing key
        :type routing_key: str
        :param body: Body of the received message
        :type body: bytes
        """
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        self._received_requests[routing_key].append(body)

    def process_data_events(self, time_limit=3) -> dict:
        """This method process data events
        in RabbitMQ queues for specified time limit.

        All requests received from RabbitMQ are stored in... <TBD>

        :param time_limit: Time limit of collecting requests
        from RabbitMQ in seconds
        :type time_limit: int

        :return: Dict with keys of request types and values with strings
        of all requests collected by specific routing key
        :rtype: dict
        """
        self._received_requests = {request: [] for request in self.request_list}
        self._channel.connection.process_data_events(time_limit=time_limit)
        return self._received_requests

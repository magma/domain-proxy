import pika


class RequestsConsumer:
    """Consumer for RabbitMQ to receive data
    from multiple queues for every type of request to SAS.

    :param rabbitmq_host: Host address to RabbitMQ instance
    :type rabbitmq_host: str
    """
    _requests = [
        "RegistrationRequest",
        "SpectrumInquiryRequest",
        "GrantRequest",
        "HeartbeatRequest",
        "RelinquishmentRequest",
        "DeregistrationRequest",
    ]

    def __init__(self, rabbitmq_host=None):
        if rabbitmq_host:
            self._host = rabbitmq_host
        else:
            raise Exception("No RabbitMQ host has been specified")
        self._create_communication_channel()
        self._received_requests = dict()

    def _create_communication_channel(self):
        """This method creates communication channel to RabbitMQ
        and declares queues for every type of requests.
        Requests queues are based on self._requests list
        and created channel is stored in self._channel.
        """
        connection_params = pika.ConnectionParameters(host=self._host)
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        channel.exchange_declare(exchange='topic_logs', exchange_type='topic')
        for requestName in self._requests:
            result = channel.queue_declare('', exclusive=True)
            channel.queue_bind(exchange='topic_logs',
                               queue=result.method.queue,
                               routing_key=f'"{requestName}"')
            channel.basic_consume(queue=result.method.queue,
                                  on_message_callback=lambda ch,
                                  method, properties, body:
                                  self._queue_callback(method.routing_key,
                                                       body),
                                  auto_ack=True)
        self._channel = channel

    def _queue_callback(self, routing_key, body):
        """Callback method for pika channel basic_consume on_message_callback
        This method appends body to proper request string based on routing key

        :param ch: Pika channel
        :type ch: pika.channel.Channel
        :param method: Basic delivery parameters
        :type method: pika.spec.Basic.Deliver
        :param properties: Properties of message
        :type properties: pika.spec.BasicProperties
        :param body: Body of the received message
        :type body: bytes
        """
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        self._received_requests[routing_key] += body + ','

    def process_data_events(self, time_limit=1) -> dict:
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
        self._received_requests = dict.fromkeys(self._requests, '[')
        self._channel.connection.process_data_events(time_limit=time_limit)
        for request in self._requests:
            if len(self._received_requests[request]) > 1:
                self._received_requests[request] = \
                    self._received_requests[request][:-1] + ']'
            else:
                self._received_requests[request] += ']'
        return self._received_requests

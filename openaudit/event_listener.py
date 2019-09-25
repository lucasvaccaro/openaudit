import sys
import logging as log
import configparser
import json
from kombu import BrokerConnection, Exchange, Queue
from kombu.mixins import ConsumerMixin

log.basicConfig(stream=sys.stdout, level=log.INFO)

class Worker(ConsumerMixin):

    connection = None
    queues = []
    events = None

    def __init__(self, connection, queue_name, exchange, routing_key, events):
        self.connection = connection
        self.events = events
        self.set_queues(queue_name, exchange, routing_key)

    def set_queues(self, queue_name, exchange, routing_key):
        for i, q in enumerate(queue_name):
            e = Exchange(exchange[i], type="topic", durable=False)
            self.queues.append(Queue(q, e, routing_key[i], durable=False, auto_delete=True, no_ack=True))

    def get_consumers(self, consumer, channel):
        return [consumer(self.queues, callbacks = [self.on_message])]

    def on_message(self, body, message):
        jbody = json.loads(body["oslo.message"])
        event_type = jbody["event_type"]
        payload = jbody["payload"]
        log.info("Caught event %s Payload %s", event_type, json.dumps(payload))

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    rabbitmq = config["rabbitmq"]
    broker_uri= "amqp://{0}:{1}@{2}//".format(rabbitmq["user"], rabbitmq["pass"], rabbitmq["host"])
    log.info("Connecting to broker at {}".format(broker_uri))
    with BrokerConnection(broker_uri) as connection:
        Worker(connection, rabbitmq["queue_name"].split("|"), rabbitmq["exchange"].split("|"), rabbitmq["routing_key"].split("|"), rabbitmq["events"].split(",")).run()

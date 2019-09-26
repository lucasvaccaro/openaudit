import sys
import logging as log
import configparser
import json
import sched
import time
import socket
import run_collector
from kombu import BrokerConnection, Exchange, Queue
from kombu.mixins import ConsumerMixin

log.basicConfig(stream=sys.stdout, level=log.INFO)

def runControllerCollectors():
    log.info("Running at %s", time.time())
    snapshot_id = run_collector.getSnapshotId()
    run_collector.runControllerCollectors(snapshot_id)

class Worker(ConsumerMixin):

    connection = None
    queues = []
    events = None
    port = None

    def __init__(self, connection, queue_name, exchange, routing_key, events, port):
        self.connection = connection
        self.events = events
        self.port = port
        self.set_queues(queue_name, exchange, routing_key)

    def set_queues(self, queue_name, exchange, routing_key):
        for i, q in enumerate(queue_name):
            e = Exchange(exchange[i], type="topic", durable=False)
            self.queues.append(Queue(q, e, routing_key[i], durable=False, auto_delete=True, no_ack=True))

    def get_consumers(self, consumer, channel):
        return [consumer(self.queues, callbacks = [self.on_message])]

    def on_message(self, body, message):
        log.debug(body)
        jbody = json.loads(body["oslo.message"])
        event_type = jbody["event_type"]
        payload = jbody["payload"]
        log.info("Caught event %s", event_type)
        # Check if event triggers verification
        if event_type in self.events:
            host = jbody["publisher_id"].split(".")[1]
            # Safe delay for synchronization
            timestamp = time.time() + 10
            # Sends request to compute node with the timestamp to execute the collector
            self.send_signal(host, timestamp)
            delay = timestamp - time.time()
            # Schedule the controller collector
            scheduler = sched.scheduler(time.time, time.sleep)
            scheduler.enter(delay, 1, runControllerCollectors, ())
            scheduler.run()

    def send_signal(self, host, data):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, self.port))
            log.info("Connected to %s", host)
            log.info("Sending data: %s", data)
            client.send(str(data))
            client.close()
        except Exception as e:
            log.error("Failed to connect to %s on port %s: %s", host, self.port, str(e))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Inform the port where the compute nodes listen to")
        sys.exit(1)

    port = int(sys.argv[1])

    # Get data from ini file

    config = configparser.ConfigParser()
    config.read("config.ini")

    rabbitmq = config["rabbitmq"]
    broker_uri= "amqp://{0}:{1}@{2}//".format(rabbitmq["user"], rabbitmq["pass"], rabbitmq["host"])
    queue_name = rabbitmq["queue_name"].split("|")
    exchange = rabbitmq["exchange"].split("|")
    routing_key = rabbitmq["routing_key"].split("|")
    events = rabbitmq["events"].split(",")

    # Connect to message broker
    log.info("Connecting to broker at {}".format(broker_uri))
    with BrokerConnection(broker_uri) as connection:
        Worker(connection, queue_name, exchange, routing_key, events, port).run()

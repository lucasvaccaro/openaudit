import sys
import logging as log
import socket
import sched
import time
import run_collector

log.basicConfig(stream=sys.stdout, level=log.INFO)

def runComputeCollectors():
    log.info("Running at %s", time.time())
    snapshot_id = run_collector.getSnapshotId()
    run_collector.runComputeCollectors(snapshot_id)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Inform the port to listen to")
        sys.exit(1)

    port = int(sys.argv[1])
    if port < 1024:
        print("Invalid port (must be an integer greater than 1023)")
        sys.exit(2)

    scheduler = sched.scheduler(time.time, time.sleep)

    log.info("Will listen on port %s", port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        log.info("Received connection from %s", addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            log.info("Received data: %s", data)
            delay = float(data) - time.time()
            scheduler.enter(delay, 1, runComputeCollectors, ())
            scheduler.run()
        conn.close()
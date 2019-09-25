import sys
import logging as log
import snapshot
import compute_collector
import controller_collector

log.basicConfig(stream=sys.stdout, level=log.INFO)

def getSnapshotId():
    snap = snapshot.Snapshot()
    return snap.getLastId()

def runControllerCollectors(snapshot_id):
    log.info("Running controller collectors for snapshot id %s", snapshot_id)
    log.info("Isolation...")
    c1 = controller_collector.IsolationControllerCollector()
    c1.run(snapshot_id)
    log.info("SecurityGroups...")
    c2 = controller_collector.SecurityGroupsControllerCollector()
    c2.run(snapshot_id)
    log.info("Routes...")
    c3 = controller_collector.RoutesControllerCollector()
    c3.run(snapshot_id)
    log.info("Finished")

def runComputeCollectors(snapshot_id):
    log.info("Running compute collectors for snapshot id %s", snapshot_id)
    log.info("Isolation...")
    c1 = compute_collector.IsolationComputeCollector()
    c1.run(snapshot_id)
    log.info("SecurityGroups...")
    c2 = compute_collector.SecurityGroupsComputeCollector()
    c2.run(snapshot_id)
    log.info("Routes...")
    c3 = compute_collector.RoutesComputeCollector()
    c3.run(snapshot_id)
    log.info("Finished")

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Inform the module to be executed (compute or controller)")
        sys.exit(1)

    module = sys.argv[1]
    snapshot_id = getSnapshotId()

    if (module == "controller"):
        runControllerCollectors(snapshot_id)
    elif (module == "compute"):
        runComputeCollectors(snapshot_id)
    else:
        print("Invalid module")
        sys.exit(2)

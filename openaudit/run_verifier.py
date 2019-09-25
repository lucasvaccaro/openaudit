import sys
import logging as log
import verifier
import reporter

log.basicConfig(stream=sys.stdout, level=log.INFO)

def getSnapshotId():
    snap = snapshot.Snapshot()
    return snap.getLastId()

if __name__ == '__main__':
    snapshot_id = getSnapshotId()

    log.info("Running verifier for snapshot id %s", snapshot_id)

    log.info("Isolation...")
    v1 = verifier.IsolationVerifier()
    noncompliant_hosts, missing_instances = v1.run()
    r1 = reporter.IsolationReporter(snapshot_id)
    r1.saveData(noncompliant_hosts, missing_instances)

    log.info("SecurityGroups...")
    v2 = verifier.SecurityGroupsVerifier()
    inconsistent_ports = v2.run()
    r2 = reporter.SecurityGroupsReporter(snapshot_id)
    r2.saveData(inconsistent_ports)

    log.info("Routes...")
    v3 = verifier.RoutesVerifier()
    inconsistent_routes = v3.run()
    r3 = reporter.RoutesReporter(snapshot_id)
    r3.saveData(inconsistent_routes)

    log.info("Finished")

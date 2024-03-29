import sys
import logging as log
import snapshot
import verifier
import reporter

log.basicConfig(stream=sys.stdout, level=log.INFO)

if __name__ == '__main__':
    snap = snapshot.Snapshot()
    snapshot_id = snap.getUnverifiedSnapshot()

    log.info("Running verifier for snapshot id %s", snapshot_id)

    log.info("Isolation...")
    v1 = verifier.IsolationVerifier()
    noncompliant_hosts, missing_instances = v1.run(snapshot_id)
    r1 = reporter.IsolationReporter(snapshot_id)
    r1.saveData(noncompliant_hosts, missing_instances)

    log.info("SecurityGroups...")
    v2 = verifier.SecurityGroupsVerifier()
    inconsistent_ports = v2.run(snapshot_id)
    r2 = reporter.SecurityGroupsReporter(snapshot_id)
    r2.saveData(inconsistent_ports)

    log.info("Routes...")
    v3 = verifier.RoutesVerifier()
    inconsistent_routes = v3.run(snapshot_id)
    r3 = reporter.RoutesReporter(snapshot_id)
    r3.saveData(inconsistent_routes)

    log.info("Finishing...")
    snap.setVerified()

    log.info("Finished")

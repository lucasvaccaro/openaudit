import sys
sys.path.append('../openaudit')
import verifier
import reporter
import unittest


class IsolationVerifierTest(unittest.TestCase):

    v = verifier.IsolationVerifier()
    r = reporter.IsolationReporter()

    def testCompliant1(self):
        hosts_controller = [
            {"uuid":"inst1", "host":"server1", "project_id":"p1"},
            {"uuid":"inst2", "host":"server1", "project_id":"p1"},
            {"uuid":"inst3", "host":"server2", "project_id":"p2"},
            {"uuid":"inst4", "host":"server2", "project_id":"p2"}
        ]

        hosts_compute = [
            {"uuid":"inst1", "host":"server1"},
            {"uuid":"inst2", "host":"server1"},
            {"uuid":"inst3", "host":"server2"},
            {"uuid":"inst4", "host":"server2"}
        ]

        dict_hosts_controller = self.v.getDictHostsController(hosts_controller)
        dict_hosts_compute = self.v.getDictHostsCompute(hosts_compute)

        noncompliant_hosts, missing_instances = self.v.verify(dict_hosts_controller, dict_hosts_compute)

        self.assertEqual(noncompliant_hosts, [], "Non-compliant hosts should be empty")
        self.assertEqual(missing_instances, [], "Missing instances should be empty")

    def testNoncompliant1(self):
        hosts_controller = [
            {"uuid":"inst1", "host":"server1", "project_id":"p1"},
            {"uuid":"inst2", "host":"server1", "project_id":"p2"},
            {"uuid":"inst3", "host":"server2", "project_id":"p2"},
            {"uuid":"inst4", "host":"server2", "project_id":"p2"}
        ]

        hosts_compute = [
            {"uuid":"inst1", "host":"server1"},
            {"uuid":"inst2", "host":"server1"},
            {"uuid":"inst3", "host":"server2"},
            {"uuid":"inst4", "host":"server2"}
        ]

        dict_hosts_controller = self.v.getDictHostsController(hosts_controller)
        dict_hosts_compute = self.v.getDictHostsCompute(hosts_compute)

        noncompliant_hosts, missing_instances = self.v.verify(dict_hosts_controller, dict_hosts_compute)

        self.assertEqual(noncompliant_hosts, ["server1"], "Should contain 'server1'")

    def testNoncompliant2(self):
        hosts_controller = [
            {"uuid":"inst1", "host":"server1", "project_id":"p1"},
            {"uuid":"inst2", "host":"server1", "project_id":"p1"},
            {"uuid":"inst3", "host":"server2", "project_id":"p2"},
            {"uuid":"inst4", "host":"server2", "project_id":"p2"}
        ]

        hosts_compute = [
            {"uuid":"inst1", "host":"server1"},
            {"uuid":"inst2", "host":"server1"},
            {"uuid":"inst4", "host":"server2"}
        ]

        dict_hosts_controller = self.v.getDictHostsController(hosts_controller)
        dict_hosts_compute = self.v.getDictHostsCompute(hosts_compute)

        noncompliant_hosts, missing_instances = self.v.verify(dict_hosts_controller, dict_hosts_compute)

        self.assertEqual(missing_instances, ["inst3"], "Should contain 'inst3'")


if __name__ == '__main__':
    unittest.main()
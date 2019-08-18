import sys
sys.path.append('../openaudit')
import verifier
import reporter
import unittest


class IsolationVerifierTest(unittest.TestCase):

    v = verifier.IsolationVerifier()
    r = reporter.IsolationReporter()

    def testCompliant(self):
        hosts = {
            "server1": [{"uuid":"qwe", "host":"server1", "project_id":"p1"}, {"uuid":"asd", "host":"server1", "project_id":"p1"}],
            "server2": [{"uuid":"poi", "host":"server2", "project_id":"p2"}, {"uuid":"lkj", "host":"server2", "project_id":"p2"}]
        }
        self.assertEqual(self.v.verify(hosts), [], "Should be empty")

    def testNoncompliant(self):
        hosts = {
            "server1": [{"uuid":"qwe", "host":"server1", "project_id":"p1"}, {"uuid":"asd", "host":"server1", "project_id":"p1"}],
            "server2": [{"uuid":"poi", "host":"server2", "project_id":"p1"}, {"uuid":"lkj", "host":"server2", "project_id":"p2"}]
        }
        noncompliant_hosts = self.v.verify(hosts)
        self.assertEqual(noncompliant_hosts, ["server2"], "Should contain 'server2'")
        rows = self.r.save(noncompliant_hosts)
        self.assertEqual(rows, 1, "Should be 1")


if __name__ == '__main__':
    unittest.main()
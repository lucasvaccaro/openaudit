import sys
sys.path.append('../openaudit')
import unittest
import verifier


class VerifierTest(unittest.TestCase):

    v = verifier.IsolationVerifier()

    def testCompliant(self):
        hosts = {
            "server1": [("qwe", "server1", "p1"), (("asd", "server1", "p1"))],
            "server2": [("poi", "server2", "p2"), (("lkj", "server2", "p2"))]
        }
        self.assertEqual(self.v.verify(hosts), [], "Should be empty")

    def testNoncompliant(self):
        hosts = {
            "server1": [("qwe", "server1", "p1"), (("asd", "server1", "p1"))],
            "server2": [("poi", "server2", "p1"), (("lkj", "server2", "p2"))]
        }
        noncompliant_hosts = self.v.verify(hosts)
        self.assertEqual(noncompliant_hosts, ["server2"], "Should contain 'server2'")
        rows = self.v.saveReport(noncompliant_hosts)
        self.assertEqual(rows, 1, "Should be 1")


if __name__ == '__main__':
    unittest.main()
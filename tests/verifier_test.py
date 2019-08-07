import sys
sys.path.append('../openaudit')

import verifier

v = verifier.IsolationVerifier()
hosts = {
    "host1": [("qwe", "host1", "proj2"), (("asd", "host1", "proj1"))],
    "host2": [("poi", "host2", "proj2"), (("lkj", "host2", "proj2"))]
}
print v.verify(hosts)
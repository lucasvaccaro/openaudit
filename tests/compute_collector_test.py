import sys
sys.path.append('../openaudit')
import compute_collector
import unittest


class IsolationComputeCollectorTest(unittest.TestCase):

    c = compute_collector.IsolationComputeCollector()

    def test(self):
        snapshot_id = 1
        host = "ubuntusrv"
        vms = "wiqeue289e19\nweiqoje329\neje28ej1ei"
        data = self.c.parseData((host, vms))
        res = self.c.saveData(data, snapshot_id)
        size = 3
        msg = "Result: " + str(res) + " Should be " + str(size)
        self.assertEqual(res, size, msg)

class RoutesComputeCollectorTest(unittest.TestCase):

    c = compute_collector.RoutesComputeCollector()

    def test(self):
        netns = ["   qrouter-5ed262ef-920f-4e51-a0a1-5021f1671288 (id: 3)", " qdhcp-4c1b2a8f-35e1-4a1c-a434-9c790f090b02 (id: 2)"]
        inets = ["  inet 127.0.0.1/8 scope host lo", "inet 172.24.4.94/24 brd 172.24.4.255 scope global qg-f94db071-e1", "inet 10.2.0.1/16 brd 10.2.255.255 scope global qr-c65e73a3-89"]
        routes = ["  default via 172.24.4.1 dev qg-f94db071-e1", "  10.2.0.0/16 dev qr-c65e73a3-89 proto kernel scope link src 10.2.0.1", "172.24.4.0/24 dev qg-f94db071-e1 proto kernel scope link src 172.24.4.94"]
        
        routers = self.c.getRouters(netns)
        for uuid in routers:
            self.c.getInet(routers, uuid, inets)
            self.c.getRoutes(routers, uuid, routes)

        snapshot_id = 1
        res = self.c.saveData(routers, snapshot_id)
        size = 2
        msg = "Result: " + str(res) + " Should be " + str(size)
        self.assertEqual(res, size, msg)


if __name__ == '__main__':
    unittest.main()
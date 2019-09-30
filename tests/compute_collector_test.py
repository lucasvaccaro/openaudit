import sys
sys.path.append('../openaudit')
import compute_collector
import unittest

import pdb


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


class SecurityGroupsComputeCollectorTest(unittest.TestCase):

    c = compute_collector.SecurityGroupsComputeCollector()

    def test(self):
        links = ["  1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 10007: br-int: <BROADCAST,MULTICAST> mtu 1450 qdisc noop state DOWN mode DEFAULT group default qlen 1000", "      link/ether a2:5f:d1:b5:4d:4c brd ff:ff:ff:ff:ff:ff", " 8: br-ex: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000", "link/ether 76:dd:ad:22:ad:46 brd ff:ff:ff:ff:ff:ff", "9: br-tun: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN mode DEFAULT group default qlen 1000", "link/ether 02:07:fd:af:2d:4c brd ff:ff:ff:ff:ff:ff", "18: tap263581b9-3c: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1450 qdisc fq_codel master ovs-system state UNKNOWN mode DEFAULT group default qlen 1000", "link/ether fe:16:3e:af:8e:60 brd ff:ff:ff:ff:ff:ff"]
        flows_e = ["table=72, priority=75,ct_state=+new-est,icmp,reg5=0x1 actions=resubmit(,73)", "  table=72, priority=75,ct_state=+new-est,udp,reg5=0x1,tp_dst=56 actions=resubmit(,73)"]
        flows_i = ["    cookie=0xa711cf9f52b99a45, duration=2861.990s, table=82, n_packets=0, n_bytes=0, idle_age=2861, priority=70,ct_state=+est-rel-rpl,udp,reg5=0x5,dl_dst=fa:16:3e:7c:b9:5c,tp_dst=80 actions=strip_vlan,output:5", "cookie=0xa711cf9f52b99a45, duration=2861.989s, table=82, n_packets=0, n_bytes=0, idle_age=2861, priority=70,ct_state=+est-rel-rpl,tcp,reg5=0x5,dl_dst=fa:16:3e:7c:b9:5c,tp_dst=80 actions=strip_vlan,output:5", "cookie=0x35db15bbd3e62818, duration=304.998s, table=82, n_packets=0, n_bytes=0, priority=75,ct_state=+est-rel-rpl,icmp,reg5=0xc,dl_dst=fa:16:3e:7c:b9:5c,nw_src=10.2.0.0/16 actions=output:\"tap263581b9-3c\""]

        ports = self.c.getPorts(links)
        for uuid in ports:
            self.c.getFlows(ports, uuid, flows_e, flows_i)

        snapshot_id = 1
        res = self.c.saveData(ports, snapshot_id)
        size = 5
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
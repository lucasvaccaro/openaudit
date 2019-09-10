import sys
sys.path.append('../openaudit')
import verifier
import reporter
import unittest


class IsolationVerifierTest(unittest.TestCase):

    v = verifier.IsolationVerifier()
    r = reporter.IsolationReporter(snapshot_id=1)

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

        rows = self.r.saveData(noncompliant_hosts, missing_instances)
        self.assertEqual(rows, 1, "Should be 1")

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

        rows = self.r.saveData(noncompliant_hosts, missing_instances)
        self.assertEqual(rows, 1, "Should be 1")


class SecurityGroupsVerifierTest(unittest.TestCase):

    v = verifier.SecurityGroupsVerifier()
    r = reporter.SecurityGroupsReporter(snapshot_id=1)
    snapshot_id = 1

    def testCompliant1(self):
        
        secgroups_controller = [
            {"group_id": '153601dd-2606-487e-8405-cf9242d49b6e', "group_name": 'default', "direction": 'egress', "protocol": None, "port_min": None, "port_max": None, "remote_ip": None, "port_id": '505f8fea-8e12-404c-8789-d769e728449d', "inst_uuid": '927a447e-0884-4a53-9016-f731503a9c9b'},
            {"group_id": '153601dd-2606-487e-8405-cf9242d49b6e', "group_name": 'default', "direction": 'ingress', "protocol": "tcp", "port_min": "80", "port_max": "80", "remote_ip": None, "port_id": '505f8fea-8e12-404c-8789-d769e728449d', "inst_uuid": '927a447e-0884-4a53-9016-f731503a9c9b'},
            {"group_id": '153601dd-2606-487e-8405-cf9242d49b6e', "group_name": 'default', "direction": 'ingress', "protocol": "tcp", "port_min": "22", "port_max": "22", "remote_ip": "10.2.0.0/16", "port_id": '505f8fea-8e12-404c-8789-d769e728449d', "inst_uuid": '927a447e-0884-4a53-9016-f731503a9c9b'},
            {"group_id": 'cf9242d4-2606-487e-8405-153601dd9b6e', "group_name": 'default', "direction": 'ingress', "protocol": "tcp", "port_min": "8443", "port_max": "8445", "remote_ip": None, "port_id": 'd769e728-e912-404c-8789-505f8fea449d', "inst_uuid": '927a447e-0884-4a53-9016-f731503a9c9b'},
            {"group_id": 'cf9242d4-2606-487e-8405-153601dd9b6e', "group_name": 'default', "direction": 'ingress', "protocol": "udp", "port_min": "55", "port_max": "56", "remote_ip": "8.8.0.0/16", "port_id": 'd769e728-e912-404c-8789-505f8fea449d', "inst_uuid": '927a447e-0884-4a53-9016-f731503a9c9b'}
        ]

        secgroups_compute = [
            {"direction": 'egress', "protocol": None, "port": None, "cidr": None, "port_id": '505f8fea-8e'},
            {"direction": 'ingress', "protocol": "tcp", "port": "80", "cidr": None, "port_id": '505f8fea-8e'},
            {"direction": 'ingress', "protocol": "tcp", "port": "80", "cidr": None, "port_id": '505f8fea-8e'},
            {"direction": 'ingress', "protocol": "tcp", "port": "22", "cidr": "10.2.0.0/16", "port_id": '505f8fea-8e'},
            {"direction": 'ingress', "protocol": "tcp", "port": "22", "cidr": "10.2.0.0/16", "port_id": '505f8fea-8e'},
            {"direction": 'ingress', "protocol": "tcp", "port": "8443", "cidr": None, "port_id": 'd769e728-e9'},
            {"direction": 'ingress', "protocol": "tcp", "port": "8445", "cidr": None, "port_id": 'd769e728-e9'},
            {"direction": 'ingress', "protocol": "udp", "port": "55", "cidr": "8.8.0.0/16", "port_id": 'd769e728-e9'},
            {"direction": 'ingress', "protocol": "udp", "port": "56", "cidr": "8.8.0.0/16", "port_id": 'd769e728-e9'}
        ]

        dict_secgroups_controller = self.v.getDictSecurityGroupsController(secgroups_controller)
        dict_secgroups_compute = self.v.getDictSecurityGroupsCompute(secgroups_compute)

        inconsistent_ports = self.v.verify(dict_secgroups_controller, dict_secgroups_compute)
        self.assertEqual(inconsistent_ports, [], "Inconsistent rules should be empty")

    def testNonCompliant1(self):
        
        secgroups_controller = [
            {"group_id": '153601dd-2606-487e-8405-cf9242d49b6e', "group_name": 'default', "direction": 'egress', "protocol": None, "port_min": None, "port_max": None, "remote_ip": None, "port_id": '505f8fea-8e12-404c-8789-d769e728449d', "inst_uuid": '927a447e-0884-4a53-9016-f731503a9c9b'},
            {"group_id": '153601dd-2606-487e-8405-cf9242d49b6e', "group_name": 'default', "direction": 'ingress', "protocol": "tcp", "port_min": "80", "port_max": "80", "remote_ip": "174.4.0.0/16", "port_id": '505f8fea-8e12-404c-8789-d769e728449d', "inst_uuid": '927a447e-0884-4a53-9016-f731503a9c9b'},
            {"group_id": '153601dd-2606-487e-8405-cf9242d49b6e', "group_name": 'default', "direction": 'ingress', "protocol": "tcp", "port_min": "22", "port_max": "22", "remote_ip": "10.2.0.0/16", "port_id": 'fea505f8-4k12-404c-8789-d769e728449d', "inst_uuid": '927a447e-0884-4a53-9016-f731503a9c9b'},
            {"group_id": 'cf9242d4-2606-487e-8405-153601dd9b6e', "group_name": 'default', "direction": 'ingress', "protocol": "tcp", "port_min": "8443", "port_max": "8445", "remote_ip": None, "port_id": 'd769e728-e912-404c-8789-505f8fea449d', "inst_uuid": '927a447e-0884-4a53-9016-f731503a9c9b'},
            {"group_id": 'cf9242d4-2606-487e-8405-153601dd9b6e', "group_name": 'default', "direction": 'ingress', "protocol": "udp", "port_min": "55", "port_max": "56", "remote_ip": "8.8.0.0/16", "port_id": 'd769e728-e912-404c-8789-505f8fea449d', "inst_uuid": '927a447e-0884-4a53-9016-f731503a9c9b'}
        ]

        secgroups_compute = [
            {"direction": 'egress', "protocol": None, "port": None, "cidr": None, "port_id": '505f8fea-8e'},
            {"direction": 'ingress', "protocol": "tcp", "port": "80", "cidr": None, "port_id": '505f8fea-8e'},
            {"direction": 'ingress', "protocol": "tcp", "port": "80", "cidr": None, "port_id": '505f8fea-8e'},
            {"direction": 'ingress', "protocol": "tcp", "port": "22", "cidr": "10.2.0.0/16", "port_id": 'fea505f8-4k'},
            {"direction": 'ingress', "protocol": "tcp", "port": "22", "cidr": "10.2.0.0/16", "port_id": 'fea505f8-4k'},
            {"direction": 'ingress', "protocol": "tcp", "port": None, "cidr": None, "port_id": 'd769e728-e9'},
            {"direction": 'ingress', "protocol": "tcp", "port": None, "cidr": None, "port_id": 'd769e728-e9'},
            {"direction": 'ingress', "protocol": "udp", "port": "55", "cidr": None, "port_id": 'd769e728-e9'},
            {"direction": 'ingress', "protocol": "udp", "port": "56", "cidr": "172.22.0.0/16", "port_id": 'd769e728-e9'}
        ]

        dict_secgroups_controller = self.v.getDictSecurityGroupsController(secgroups_controller)
        dict_secgroups_compute = self.v.getDictSecurityGroupsCompute(secgroups_compute)

        inconsistent_ports = self.v.verify(dict_secgroups_controller, dict_secgroups_compute)
        self.assertEqual(inconsistent_ports, ["505f8fea-8e12-404c-8789-d769e728449d", "d769e728-e912-404c-8789-505f8fea449d"], "Inconsistent rules should contain 505f8fea-8e and d769e728-e9")

        rows = self.r.saveData(inconsistent_ports)
        self.assertEqual(rows, 2, "Should be 2")


class RoutesVerifierTest(unittest.TestCase):

    v = verifier.RoutesVerifier()
    r = reporter.RoutesReporter(snapshot_id=1)
    snapshot_id = 1

    def testCompliant1(self):
        routes_controller = [
            {"router_id": '5ed262ef-920f-4e51-a0a1-5021f1671288', "name": 'router1', "port_id": 'f94db071-e123-45d7-9fa3-81a74c3720e0', "cidr": '172.24.4.0/24', "gateway_ip": '172.24.4.1'},
            {"router_id": '5ed262ef-920f-4e51-a0a1-5021f1671288', "name": 'router1', "port_id": 'c65e73a3-89b2-41f6-acff-c5f66b60082c', "cidr": '10.2.0.0/16', "gateway_ip": '10.2.0.1'}
        ]

        routes_compute = [
            {"uuid": '5ed262ef-920f-4e51-a0a1-5021f1671288', "iface": 'qg-f94db071-e1', "inet": '172.24.4.94/24', "cidr": '172.24.4.0/24', "src": '172.24.4.94', "default_gw": '172.24.4.1'},
            {"uuid": '5ed262ef-920f-4e51-a0a1-5021f1671288', "iface": 'qr-c65e73a3-89', "inet": '10.2.0.1/16', "cidr": '10.2.0.0/16', "src": '10.2.0.1', "default_gw": '172.24.4.1'}
        ]

        dict_routes_controller = self.v.getDictRoutesController(routes_controller)
        dict_routes_compute = self.v.getDictRoutesCompute(routes_compute)

        inconsistent_routes = self.v.verify(dict_routes_controller, dict_routes_compute)
        self.assertEqual(inconsistent_routes, [], "Inconsistent routes should be empty")

    def testNonCompliant1(self):
        routes_controller = [
            {"router_id": '5ed262ef-920f-4e51-a0a1-5021f1671288', "name": 'router1', "port_id": 'f94db071-e123-45d7-9fa3-81a74c3720e0', "cidr": '172.24.4.0/24', "gateway_ip": '172.24.4.1'},
            {"router_id": '5ed262ef-920f-4e51-a0a1-5021f1671288', "name": 'router1', "port_id": 'c65e73a3-89b2-41f6-acff-c5f66b60082c', "cidr": '10.2.0.0/16', "gateway_ip": '10.2.0.1'}
        ]

        routes_compute = [
            {"uuid": '5ed262ef-920f-4e51-a0a1-5021f1671288', "iface": 'qg-f94db071-e1', "inet": '10.24.4.94/24', "cidr": '172.24.4.0/24', "src": '172.24.4.94', "default_gw": '172.24.4.1'},
            {"uuid": '5ed262ef-920f-4e51-a0a1-5021f1671288', "iface": 'qr-c65e73a3-89', "inet": '10.2.0.1/16', "cidr": '10.2.0.0/16', "src": '10.2.0.1', "default_gw": '172.24.4.1'}
        ]

        dict_routes_controller = self.v.getDictRoutesController(routes_controller)
        dict_routes_compute = self.v.getDictRoutesCompute(routes_compute)

        inconsistent_routes_assert = [("5ed262ef-920f-4e51-a0a1-5021f1671288", "f94db071-e123-45d7-9fa3-81a74c3720e0")]

        inconsistent_routes = self.v.verify(dict_routes_controller, dict_routes_compute)
        self.assertEqual(inconsistent_routes, inconsistent_routes_assert, "Should contain 1 route")

        rows = self.r.saveData(inconsistent_routes)
        self.assertEqual(rows, 1, "Should be 1")

    def testNonCompliant2(self):
        routes_controller = [
            {"router_id": '5ed262ef-920f-4e51-a0a1-5021f1671288', "name": 'router1', "port_id": 'f94db071-e123-45d7-9fa3-81a74c3720e0', "cidr": '72.24.4.0/24', "gateway_ip": '172.24.4.1'},
            {"router_id": '5ed262ef-920f-4e51-a0a1-5021f1671288', "name": 'router1', "port_id": 'c65e73a3-89b2-41f6-acff-c5f66b60082c', "cidr": '10.2.0.0/24', "gateway_ip": '10.2.0.1'}
        ]

        routes_compute = [
            {"uuid": '5ed262ef-920f-4e51-a0a1-5021f1671288', "iface": 'qg-f94db071-e1', "inet": '172.24.4.94/24', "cidr": '172.24.4.0/24', "src": '172.24.4.94', "default_gw": '172.24.4.1'},
            {"uuid": '5ed262ef-920f-4e51-a0a1-5021f1671288', "iface": 'qr-c65e73a3-89', "inet": '10.2.0.1/16', "cidr": '10.2.0.0/16', "src": '10.2.0.1', "default_gw": '172.24.4.1'}
        ]

        dict_routes_controller = self.v.getDictRoutesController(routes_controller)
        dict_routes_compute = self.v.getDictRoutesCompute(routes_compute)

        inconsistent_routes_assert = [("5ed262ef-920f-4e51-a0a1-5021f1671288", "f94db071-e123-45d7-9fa3-81a74c3720e0"), ("5ed262ef-920f-4e51-a0a1-5021f1671288", "c65e73a3-89b2-41f6-acff-c5f66b60082c")]

        inconsistent_routes = self.v.verify(dict_routes_controller, dict_routes_compute)
        self.assertEqual(inconsistent_routes, inconsistent_routes_assert, "Should contain both routes")

        rows = self.r.saveData(inconsistent_routes)
        self.assertEqual(rows, 2, "Should be 2")

    def testNonCompliant3(self):
        routes_controller = [
            {"router_id": '5ed262ef-920f-4e51-a0a1-5021f1671288', "name": 'router1', "port_id": 'f94db071-e123-45d7-9fa3-81a74c3720e0', "cidr": '172.24.4.0/24', "gateway_ip": '172.24.4.1'},
            {"router_id": '5ed262ef-920f-4e51-a0a1-5021f1671288', "name": 'router1', "port_id": 'c65e73a3-89b2-41f6-acff-c5f66b60082c', "cidr": '10.2.0.0/24', "gateway_ip": '10.2.0.1'}
        ]

        routes_compute = [
            {"uuid": '5ed262ef-920f-4e51-a0a1-5021f1671288', "iface": 'qg-f94db071-e1', "inet": '172.24.4.94/24', "cidr": '172.24.4.0/24', "src": '172.24.4.94', "default_gw": '172.24.4.1'}
        ]

        dict_routes_controller = self.v.getDictRoutesController(routes_controller)
        dict_routes_compute = self.v.getDictRoutesCompute(routes_compute)

        inconsistent_routes_assert = [("5ed262ef-920f-4e51-a0a1-5021f1671288", "c65e73a3-89b2-41f6-acff-c5f66b60082c")]

        inconsistent_routes = self.v.verify(dict_routes_controller, dict_routes_compute)
        self.assertEqual(inconsistent_routes, inconsistent_routes_assert, "Should contain 1 route")

        rows = self.r.saveData(inconsistent_routes)
        self.assertEqual(rows, 1, "Should be 1")


if __name__ == '__main__':
    unittest.main()
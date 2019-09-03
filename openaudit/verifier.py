import database_connection as db
from abc import ABCMeta, abstractmethod
import ipaddress


class Verifier:
    __metaclass__ = ABCMeta
    
    db_conn = None

    def __init__(self):
        self.db_conn = db.DatabaseConnection("openauditDB")
        self.db_conn = self.db_conn.getConn();

    def getData(self, snapshot_id, table):
        """
        Fetches all data of a snapshot from a table
        """
        sql = (
            "SELECT ALL "
            "FROM openaudit." + table + " "
            "WHERE snapshot_id = %d",
            (snapshot_id,)
        )
        db_cursor = self.db_conn_stack.cursor()
        db_cursor.execute(sql)
        return db_cursor.fetchall()

    def toDict(self, ls, attr):
        """
        Receives a list and an attribute
        Rturns a dictionary where the key is the attribute and the value is a list of properties collected
        """
        dic = {}
        for item in ls:
            key = item[attr]
            if (key in dic):
                dic[key].append(item)
            else:
                dic[key] = [item]
        return dic

    @abstractmethod
    def getControllerData(self, snapshot_id):
        pass

    @abstractmethod
    def getComputeData(self, snapshot_id):
        pass

    @abstractmethod
    def verify(self, controller_data, compute_data):
        pass


class IsolationVerifier(Verifier):

    def getControllerData(self, snapshot_id):
        """
        Returns the instances collected from the controller host in a snapshot
        """
        return self.getData(snapshot_id, "snapshot_isolation_controller")

    def getComputeData(self, snapshot_id):
        """
        Returns the instances collected from the compute node hosts in a snapshot
        """
        return self.getData(snapshot_id, "snapshot_isolation_compute")
        
    def getDictHostsController(self, instances):
        """
        Receives a list of instances taken from the controller node
        Returns dictionary where the key is the host and the value is the list of instances running on the host
        """
        return self.toDict(instances, "host")

    def getDictHostsCompute(self, instances):
        """
        Receives a list of hosts and instances taken from the compute nodes
        Returns dictionary where the key is the host and the value is the list of instances running on the host
        """
        hosts = {}
        for inst in instances:
            host = inst["host"]
            if (host in hosts):
                hosts[host].append(inst["uuid"])
            else:
                hosts[host] = [inst["uuid"]]
        return hosts

    def verify(self, hosts_controller, hosts_compute):
        """
        Checks whether instances from different projects are running on the same host
        Checks whether instances from the database are missing in a compute node
        Receives a dictionary of hosts (controller and compute)
        Returns an array of uncompliant instances and missing instances
        """
        noncompliant_hosts = []
        missing_instances = []
        for host in hosts_controller:
            project_id = None
            for inst in hosts_controller[host]:
                if (project_id != None and inst["project_id"] != project_id):
                    noncompliant_hosts.append(inst["host"])
                elif not inst["uuid"] in hosts_compute[host]:
                    missing_instances.append(inst["uuid"])
                else:
                    project_id = inst["project_id"]
        return (noncompliant_hosts, missing_instances)


class SecurityGroupsVerifier(Verifier):
    def getControllerData(self, snapshot_id):
        """
        Returns the security groups rules collected from the controller host in a snapshot
        """
        return self.getData(snapshot_id, "snapshot_securitygroups_controller")

    def getComputeData(self, snapshot_id):
        """
        Returns the security groups rules collected from the compute nodes in a snapshot
        """
        return self.getData(snapshot_id, "snapshot_securitygroups_compute")

    def getDictSecurityGroupsController(self, security_groups):
        """
        Receives a list of security groups taken from the controller node
        Returns dictionary where the key is the port ID and the value is the list of rules
        """
        return self.toDict(security_groups, "port_id")

    def getDictSecurityGroupsCompute(self, security_groups):
        """
        Receives a list of security groups taken from the compute nodes
        Returns dictionary where the key is the port ID and the value is the list of rules
        """
        return self.toDict(security_groups, "port_id")

    def verify(self, controller_data, compute_data):
        """
        Performs the verirication process against the data collected
        Returns a list of inconsistent ports
        """
        inconsistent_ports = []
        for ctl_port in controller_data:
            cmp_port = self.findComputePort(compute_data, ctl_port)
            if not self.verifyRules(controller_data[ctl_port], compute_data[cmp_port]):
                inconsistent_ports.append(ctl_port)
        return inconsistent_ports

    def findComputePort(self, controller_data, ctl_port_id):
        """
        Searches a port among compute rules
        """
        for cmp_port_id in controller_data:
            if ctl_port_id.startswith(cmp_port_id):
                return cmp_port_id
        return None

    def verifyRules(self, ctl_port_rules, cmp_port_rules):
        """
        Runs the tests against the controller and compute interfaces
        Returns True if all controller rules have been found and there are no remaining rules in the compute node, False otherwise
        """
        rules_ctl_remaining = len(ctl_port_rules)
        rules_cmp_remaining = len(cmp_port_rules)
        for ctl_rule in ctl_port_rules:
            found = False
            for cmp_rule in cmp_port_rules:
                # Compare values
                direction = ctl_rule["direction"] == cmp_rule["direction"]
                protocol = ctl_rule["protocol"] == cmp_rule["protocol"]
                cidr = ctl_rule["remote_ip"] == cmp_rule["cidr"]
                if (protocol == "icmp"):
                    port = True # icmp has no port
                else:
                    port = cmp_rule["port"] == ctl_rule["port_min"] or cmp_rule["port"] == ctl_rule["port_max"]
                # Assert
                if direction and protocol and cidr and port:
                    found = True
                    rules_cmp_remaining -= 1
                # Dont break the loop because the rules can repeat in the compute node (e.g. max/min port)
            # If rule was found at least once
            if found:
                rules_ctl_remaining -= 1
        return rules_ctl_remaining == 0 and rules_cmp_remaining == rules_ctl_remaining


class RoutesVerifier(Verifier):
    def getControllerData(self, snapshot_id):
        """
        Returns the security groups rules collected from the controller host in a snapshot
        """
        return self.getData(snapshot_id, "snapshot_routes_controller")

    def getComputeData(self, snapshot_id):
        """
        Returns the security groups rules collected from the end hosts in a snapshot
        """
        return self.getData(snapshot_id, "snapshot_routes_compute")

    def getDictRoutesController(self, routes):
        """
        Receives a list of routes taken from the controller node
        Returns dictionary where the key is the router and the value is the list of properties
        """
        return self.toDict(routes, "router_id")

    def getDictRoutesCompute(self, routes):
        """
        Receives a list of routes taken from the compute node
        Returns dictionary where the key is the router and the value is the list of properties
        """
        return self.toDict(routes, "uuid")

    def verify(self, controller_data, compute_data):
        """
        Performs the verirication process against the data collected
        Returns a list of inconsistent routes (router ID and port ID)
        """
        inconsistent_routes = []
        for router_id in controller_data:
            for ctl_iface in controller_data[router_id]:
                cmp_iface = self.findComputeIface(compute_data, ctl_iface["port_id"])
                if cmp_iface is None or not self.verifyInterfaces(ctl_iface, cmp_iface):
                    inconsistent_routes.append((ctl_iface["router_id"], ctl_iface["port_id"]))
        return inconsistent_routes

    def findComputeIface(self, compute_data, iface_name):
        """
        Searches an interface among routes from the compute node
        """
        for router_id in compute_data:
            for iface in compute_data[router_id]:
                if iface_name.startswith(iface["iface"][3:]):
                    return iface
        return None

    def verifyInterfaces(self, ctl_iface, cmp_iface):
        """
        Runs the tests against the controller and compute interfaces
        """
        equals_cidr = cmp_iface["cidr"] == ctl_iface["cidr"]
        equals_gw = cmp_iface["default_gw"] == ctl_iface["gateway_ip"] or cmp_iface["src"] == ctl_iface["gateway_ip"]
        try:
            ip_in_cidr = ipaddress.ip_address(unicode(cmp_iface["inet"][:-3])) in ipaddress.ip_network(unicode(ctl_iface["cidr"]))
        except:
            ip_in_cidr = False
        return equals_cidr and equals_gw and ip_in_cidr

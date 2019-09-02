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
        Receives a list and returns a dictionary where the key is a common attribute
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
        Returns the security groups rules collected from the end hosts in a snapshot
        """
        return self.getData(snapshot_id, "snapshot_securitygroups_compute")

    def verify(self, controller_data, compute_data):
        pass


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
        inconsistent_routes = []
        for router_id in compute_data:
            for cmp_iface in compute_data[router_id]:
                ctl_iface = self.findControllerIface(controller_data, cmp_iface["iface"])
                if not self.verifyInterfaces(ctl_iface, cmp_iface):
                    inconsistent_routes.append((ctl_iface["router_id"], ctl_iface["port_id"]))
        return inconsistent_routes


    def findControllerIface(self, controller_data, iface_name):
        """
        Searches an interface among controller routes
        """
        for router_id in controller_data:
            for iface in controller_data[router_id]:
                if iface["port_id"].startswith(iface_name[3:]):
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

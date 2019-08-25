from abc import ABCMeta, abstractmethod
import database_connection as db


class Verifier:
    __metaclass__ = ABCMeta
    
    db_conn = None

    def __init__(self):
        self.db_conn = db.DatabaseConnection("openauditDB")
        self.db_conn = self.db_conn.getConn();


class IsolationVerifier(Verifier):

    def getControllerData(self, snapshot_id):
        """
        Returns the instances collected from the controller host in a snapshot
        """
        db_cursor = self.db_conn.cursor(dictionary=True)
        db_cursor.execute(
            "SELECT uuid, host, project_id "
            "FROM openaudit.snapshot_isolation_controller "
            "WHERE snapshot_id = %d",
            (snapshot_id,)
        )
        return db_cursor.fetchall()

    def getComputeData(self, snapshot_id):
        """
        Returns the instances collected from the compute node hosts in a snapshot
        """
        db_cursor = self.db_conn.cursor(dictionary=True)
        db_cursor.execute(
            "SELECT uuid, host "
            "FROM openaudit.snapshot_isolation_compute "
            "WHERE snapshot_id = %d",
            (snapshot_id,)
        )
        return db_cursor.fetchall()

    def getDictHostsController(self, instances):
        """
        Receives a list of instances taken from the controller node
        Returns dictionary where the key is the host and the value is the list of instances running on the host
        """
        hosts = {}
        for inst in instances:
            host = inst["host"]
            if (host in hosts):
                hosts[host].append(inst)
            else:
                hosts[host] = [inst]
        return hosts

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
        db_cursor = self.db_conn.cursor(dictionary=True)
        db_cursor.execute(
            "SELECT ALL "
            "FROM openaudit.snapshot_securitygroups_controller "
            "WHERE snapshot_id = %d",
            (snapshot_id,)
        )
        return db_cursor.fetchall()

    def getComputeData(self, snapshot_id):
        """
        Returns the security groups rules collected from the end hosts in a snapshot
        """
        db_cursor = self.db_conn.cursor(dictionary=True)
        db_cursor.execute(
            "SELECT ALL "
            "FROM openaudit.snapshot_securitygroups_endhosts "
            "WHERE snapshot_id = %d",
            (snapshot_id,)
        )
        return db_cursor.fetchall()

    def getDictInstancesController(self, rules):
        """
        Receives a list of rules
        Returns dictionary where the key is the instance and the value is the list of security groups rules
        """
        instances = {}
        for rule in rules:
            inst = rule["instance"]
            if (inst in instances):
                instances[inst].append(rule)
            else:
                instances[inst] = [rule]
        return instances


    def verify(self, controller_data, endhost_data):
        pass


class RoutesVerifier(Verifier):
    pass

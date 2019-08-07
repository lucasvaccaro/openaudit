import database_connection as db

class Verifier:
    db_conn_stack = None
    db_conn_local = None

    def __init__(self):
        self.db_conn_stack = db.DatabaseConnection("openstackDB")
        self.db_conn_stack = self.db_conn_stack.getConn();
        self.db_conn_local = db.DatabaseConnection("localDB")
        self.db_conn_local = self.db_conn_local.getConn();

class IsolationVerifier(Verifier):

    def getAllInstances(self):
        """
        Returns all the instances with their host and project
        """
        db_cursor = self.db_conn_stack.cursor()
        db_cursor.execute(
            "SELECT uuid, host, project_id "
            "FROM nova_cell1.instances "
            "WHERE deleted = 0 "
        )
        return db_cursor.fetchall()
    
    def getDictHosts(self, instances):
        """
        Receives a list of instances (uuid, host, project_id)
        Returns dictionary where the key is the host and the value is the list of instances running on the host
        """
        hosts = {}
        for inst in instances:
            host = inst[1]
            if (host in hosts):
                hosts[host].append(inst)
            else:
                hosts[host] = [inst]
        return hosts

    def verify(self, hosts):
        """
        Checks whether instances from different projects are running on the same host
        Receives a dictionary of hosts
        Returns an array of uncompliant hosts
        """
        noncompliant_hosts = []
        for host in hosts:
            project_id = None
            for inst in hosts[host]:
                if (project_id != None and inst[2] != project_id):
                    noncompliant_hosts.append(host)
                    break
                else:
                    project_id = inst[2]
        return noncompliant_hosts

    def run(self):
        return self.verify(self.getDictHosts(self.getAllInstances()))


class SecurityGroupsVerifier(Verifier):
    pass


class RoutesVerifier(Verifier):
    pass
from abc import ABCMeta, abstractmethod
import database_connection as db
import subprocess


class ComputeCollector():
    __metaclass__ = ABCMeta

    db_conn = None

    def __init__(self):
        self.db_conn = db.DatabaseConnection("openauditDB")
        self.db_conn = self.db_conn.getConn();

    @abstractmethod
    def getData(self):
        pass

    @abstractmethod
    def parseData(self, data):
        pass

    @abstractmethod
    def saveData(self, data, snapshot_id):
        pass


class IsolationComputeCollector(ComputeCollector):
    """
    Returns ouput of OS commands 'hostname' and 'virsh'
    """ 
    def getData(self):
        host = subprocess.check_output("hostname", shell=True)
        vms = subprocess.check_output("virsh list --uuid", shell=True)
        return (host, vms)

    """
    Parses the raw data
    Returns formatted data
    """
    def parseData(self, data):
        host, vms = data
        host = host.strip()
        vms = vms.strip().splitlines()
        return (host, vms)

    """
    Saves data collected into OpenAudit DB
    Returns number of rows inserted
    """
    def saveData(self, data, snapshot_id):
        host, vms = data
        sql_insert = "INSERT INTO openaudit.snapshot_isolation_compute (uuid, host, snapshot_id) VALUES (%s, %s, %s)"
        cursor = self.db_conn.cursor()
        rowcount = 0
        for vm in vms:
            values = (vm, host, snapshot_id)
            cursor.execute(sql_insert, values)
            rowcount += cursor.rowcount
        self.db_conn.commit()
        return rowcount
    

class SecurityGroupsComputeCollector(ComputeCollector):
    def getData(self):
        pass

    def parseData(self, data):
        pass

    def saveData(self, data, snapshot_id):
        pass


class RoutesComputeCollector(ComputeCollector):
    def getData(self):
        pass

    def parseData(self, data):
        pass

    def saveData(self, data, snapshot_id):
        pass


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
    def saveData(self, data, snapshot_id):
        pass

    def runCmd(self, cmd):
        return subprocess.check_output(cmd, shell=True)


class IsolationComputeCollector(ComputeCollector):
    """
    Returns ouput of OS commands 'hostname' and 'virsh'
    """ 
    def getData(self):
        host = self.runCmd("hostname")
        vms = self.runCmd("virsh list --uuid")
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
        # Get dict of routers
        routers = self.getRouters()
        for uuid in routers:
            # Get routers` configuration
            self.getInet(routers, uuid)
            self.getRoutes(routers, uuid)
        return routers

    def getRouters(self, lines = None):
        """
        Gets all the routers in the host
        Returns a dictionary where the key is the router`s uuid
        """
        # Get namespaces
        if lines is None:
            lines = self.runCmd("ip netns").strip().splitlines()
        # Build map of routers where the key is the uuid
        routers = {}
        for line in lines:
            net = line.strip()
            if net.startswith("qrouter"):
                uuid = net[8:44]
                routers[uuid] = {}
        return routers

    def getInet(self, routers, uuid, lines = None):
        """
        Gets the IP address of each interface of a router
        """
        if lines is None:
            cmd = "sudo ip netns exec qrouter-" + uuid + " ip -4 addr | grep inet"
            lines = self.runCmd(cmd).strip().splitlines()
        lines.pop(0) # Remove loopback
        for line in lines:
            elements = line.strip().split()
            inet = elements[1]
            iface = elements[6]
            if not iface in routers[uuid]:
                routers[uuid][iface] = {}
            routers[uuid][iface].update({"inet": inet})

    def getRoutes(self, routers, uuid, lines = None):
        """
        Gets the routing table of a router
        """
        if lines is None:
            cmd = "sudo ip netns exec qrouter-" + uuid + " ip route"
            lines = self.runCmd(cmd).strip().splitlines()
        default_gw = lines.pop(0).split()[2] # Get default gateway
        for line in lines:
            elements = line.strip().split()
            cidr = elements[0]
            iface = elements[2]
            src = elements[8]
            if not iface in routers[uuid]:
                routers[uuid][iface] = {}
            routers[uuid][iface].update({"cidr": cidr, "src": src, "default_gw": default_gw})
    
    def saveData(self, data, snapshot_id):
        sql_insert = "INSERT INTO openaudit.snapshot_routes_compute (uuid, iface, inet, cidr, src, default_gw, snapshot_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor = self.db_conn.cursor()
        rowcount = 0
        for uuid in data:
            for iface, config in data[uuid].items():
                values = (uuid, iface, config["inet"], config["cidr"], config["src"], config["default_gw"], snapshot_id)
                cursor.execute(sql_insert, values)
                rowcount += cursor.rowcount
        self.db_conn.commit()
        return rowcount

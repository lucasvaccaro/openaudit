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
    """
    Returns a dictionary of ports and their security rules
    """
    def getData(self):
        # Get dict of ports
        ports = self.getPorts()
        for uuid in ports:
            # Get routers` configuration
            self.getFlows(ports, uuid)
        return routers

    """
    Gets all the ports (tap interfaces) in the host
    Returns a dictionary where the key is the port's partial uuid (tap) with the mac address as one nested value
    """
    def getPorts(self, lines = None):
        # Get namespaces
        if lines is None:
            lines = self.runCmd("ip link").strip().splitlines()
        # Build map of ports where the key is the partial uuid from the tap iface
        ports = {}
        for i, item in enumerate(lines):
            iface = item.strip().split()[1][:-1]
            if iface.startswith("tap"):
                uuid = iface[3:]
                mac = lines[i+1].strip().split()[1]
                ports[iface] = {"egress": [], "ingress": []}
            i += 2
        return ports

    """
    Gets all the flows that represent securiry groups of a port (tap iface)
    """
    def getFlows(self, ports, uuid, lines_eg = None, lines_ig = None):
        if lines_eg is None:
            cmd_eg = "ovs-ofctl dump-flows br-int table=72 | grep \"" + mac + "\""
            lines_eg = self.runCmd(cmd).splitlines()

        if lines_ig is None:
            cmd_ig = "ovs-ofctl dump-flows br-int table=82 | grep \"" + mac + "\""
            lines_ig = self.runCmd(cmd).splitlines()

        for line in lines_eg:
            protocol, cidr, port = self.parseFlow(line)
            ports[uuid]["egress"].append([protocol, cidr, port])

        for line in lines_ig:
            protocol, cidr, port = self.parseFlow(line)
            ports[uuid]["ingress"].append([protocol, cidr, port])

    """
    Extracts information from a flow line
    """
    def parseFlow(self, line):
        protocol = None
        cidr = None
        port = None
        elements = line.strip().split(",")
        # Protocol
        if "tcp" in elements:
            protocol = "tcp"
        elif "udp" in elements:
            protocol = "udp"
        elif "icmp" in elements:
            protocol = "icmp"
        # CIDR and port
        for el in elements:
            if el.startswith("nw_src"):
                cidr = el[7:].split()[0]
            elif el.startswith("tp_dst"):
                port = el[7:].split()[0]
        # Returb
        return (protocol, cidr, port)

    """
    Saves data collected into OpenAudit DB
    Returns number of rows inserted
    """
    def saveData(self, data, snapshot_id):
        sql_insert = (
            "INSERT INTO openaudit.snapshot_securitygroups_compute "
            "(port_id, direction, protocol, cidr, port, snapshot_id) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        cursor = self.db_conn.cursor()
        rowcount = 0
        for uuid in data:
            for direction, rules in data[uuid].items():
                for rule in rules:
                    values = (uuid[3:], direction, rule[0], rule[1], rule[2], snapshot_id)
                    cursor.execute(sql_insert, values)
                    rowcount += cursor.rowcount
        self.db_conn.commit()
        return rowcount


class RoutesComputeCollector(ComputeCollector):
    """
    Returns a dictionary of routers and their configuration
    """
    def getData(self):
        # Get dict of routers
        routers = self.getRouters()
        for uuid in routers:
            # Get routers` configuration
            self.getInet(routers, uuid)
            self.getRoutes(routers, uuid)
        return routers

    """
    Gets all the routers in the host
    Returns a dictionary where the key is the router's uuid
    """
    def getRouters(self, lines = None):
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

    """
    Gets the IP address of each interface of a router
    """ 
    def getInet(self, routers, uuid, lines = None):
        if lines is None:
            cmd = "ip netns exec qrouter-" + uuid + " ip -4 addr | grep inet"
            lines = self.runCmd(cmd).strip().splitlines()

        lines.pop(0) # Remove loopback

        for line in lines:
            elements = line.strip().split()
            inet = elements[1]
            iface = elements[6]
            if not iface in routers[uuid]:
                routers[uuid][iface] = {}
            routers[uuid][iface].update({"inet": inet})

    """
    Gets the routing table of a router
    """
    def getRoutes(self, routers, uuid, lines = None):
        if lines is None:
            cmd = "ip netns exec qrouter-" + uuid + " ip route"
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
    
    """
    Saves data collected into OpenAudit DB
    Returns number of rows inserted
    """
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

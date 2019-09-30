from abc import ABCMeta, abstractmethod
import database_connection as db
import sys
import logging as log
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
        out = None
        try:
            out = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            log.error(e.output)
        return out

    @abstractmethod
    def run(self, snapshot_id):
        pass


class IsolationComputeCollector(ComputeCollector):
     
    def getData(self):
        """
        Returns ouput of OS commands 'hostname' and 'virsh'
        """
        host = self.runCmd("hostname")
        vms = self.runCmd("virsh list --uuid")
        return (host, vms)

    def parseData(self, data):
        """
        Parses the raw data
        Returns formatted data
        """
        host, vms = data
        host = host.strip()
        vms = vms.strip().splitlines()
        return (host, vms)

    def saveData(self, data, snapshot_id):
        """
        Saves data collected into OpenAudit DB
        Returns number of rows inserted
        """
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

    def run(self, snapshot_id):
        data = self.getData()
        parsed_data = self.parseData(data)
        self.saveData(parsed_data, snapshot_id)


class SecurityGroupsComputeCollector(ComputeCollector):
    
    def getData(self):
        """
        Returns a dictionary of ports and their security rules
        """
        # Get dict of ports
        ports = self.getPorts()
        for uuid in ports:
            # Get routers` configuration
            self.getFlows(ports, uuid)
        return ports
    
    def getPorts(self, lines = None):
        """
        Gets all the ports (tap interfaces) in the host
        Returns a dictionary where the key is the port's partial uuid (tap) with the mac address as one nested value
        """
        # Get namespaces
        if lines is None:
            lines = self.runCmd("ip link")
            if not lines is None:
                lines = lines.strip().splitlines()
        # Build map of ports where the key is the partial uuid from the tap iface
        ports = {}
        for i, item in enumerate(lines):
            iface = item.strip().split()[1][:-1]
            if iface.startswith("tap"):
                uuid = iface[3:]
                mac = lines[i+1].strip().split()[1]
                ports[iface] = {"egress": [], "ingress": [], "mac": mac}
            i += 2
        return ports

    def getFlows(self, ports, uuid, lines_eg = None, lines_ig = None):
        """
        Gets all the flows that represent securiry groups of a port (tap iface)
        """
        mac = ports[uuid]["mac"]

        if lines_eg is None:
            cmd_eg = "ovs-ofctl dump-flows br-int table=72 | grep \"" + mac + "\""
            lines_eg = self.runCmd(cmd_eg)
            if not lines_eg is None:
                lines_eg = lines_eg.splitlines()

        if lines_ig is None:
            cmd_ig = "ovs-ofctl dump-flows br-int table=82 | grep \"" + mac + "\""
            lines_ig = self.runCmd(cmd_ig)
            if not lines_ig is None:
                lines_ig = lines_ig.splitlines()

        if not lines_eg is None:
            for line in lines_eg:
                protocol, cidr, port = self.parseFlow(line)
                ports[uuid]["egress"].append([protocol, cidr, port])

        if not lines_ig is None:
            for line in lines_ig:
                protocol, cidr, port = self.parseFlow(line)
                ports[uuid]["ingress"].append([protocol, cidr, port])

    def parseFlow(self, line):
        """
        Extracts information from a flow line
        """
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

    def saveData(self, data, snapshot_id):
        """
        Saves data collected into OpenAudit DB
        Returns number of rows inserted
        """
        sql_insert = (
            "INSERT INTO openaudit.snapshot_securitygroups_compute "
            "(port_id, direction, protocol, cidr, port, snapshot_id) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        cursor = self.db_conn.cursor()
        rowcount = 0
        for uuid in data:
            for rule in data[uuid]["ingress"]:
                values = (uuid[3:], "ingress", rule[0], rule[1], rule[2], snapshot_id)
                cursor.execute(sql_insert, values)
                rowcount += cursor.rowcount
            for rule in data[uuid]["egress"]:
                values = (uuid[3:], "egress", rule[0], rule[1], rule[2], snapshot_id)
                cursor.execute(sql_insert, values)
                rowcount += cursor.rowcount
        self.db_conn.commit()
        return rowcount

    def run(self, snapshot_id):
        data = self.getData()
        self.saveData(data, snapshot_id)


class RoutesComputeCollector(ComputeCollector):
    
    def getData(self):
        """
        Returns a dictionary of routers and their configuration
        """
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
        Returns a dictionary where the key is the router's uuid
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

    def getRoutes(self, routers, uuid, lines = None):
        """
        Gets the routing table of a router
        """
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
    
    def saveData(self, data, snapshot_id):
        """
        Saves data collected into OpenAudit DB
        Returns number of rows inserted
        """
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

    def run(self, snapshot_id):
        data = self.getData()
        self.saveData(data, snapshot_id)

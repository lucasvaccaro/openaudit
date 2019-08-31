from abc import ABCMeta, abstractmethod
import database_connection as db


class ControllerCollector():
    __metaclass__ = ABCMeta

    db_conn_stack = None
    db_conn_local = None

    def __init__(self):
        self.db_conn_stack = db.DatabaseConnection("openstackDB")
        self.db_conn_stack = self.db_conn_stack.getConn();
        self.db_conn_local = db.DatabaseConnection("openauditDB")
        self.db_conn_local = self.db_conn_local.getConn();

    @abstractmethod
    def getData(self, sql):
        db_cursor = self.db_conn_stack.cursor()
        db_cursor.execute(sql)
        return db_cursor.fetchall()

    @abstractmethod
    def saveData(self, sql, data, snapshot_id):
        if not data:
            return 0
        cursor = self.db_conn_local.cursor()
        rowcount = 0
        for values in data:
            _values = list(values)
            _values.append(snapshot_id)
            cursor.execute(sql, _values)
            rowcount += cursor.rowcount
        self.db_conn_local.commit()
        return rowcount


class IsolationControllerCollector(ControllerCollector):
    def getData(self):
        """
        Returns all the instances with their host and project from the OpenStack DB
        """
        sql = (
            "SELECT uuid, host, project_id "
            "FROM nova_cell1.instances "
            "WHERE deleted = 0 "
        )
        return super(IsolationControllerCollector, self).getData(sql)

    def saveData(self, data, snapshot_id):
        """
        Saves instances with their host, project and snapshot into OpenAudit DB
        """
        sql = "INSERT INTO openaudit.snapshot_isolation_controller (uuid, host, project_id, snapshot_id) VALUES (%s, %s, %s, %s)"
        return super(IsolationControllerCollector, self).saveData(sql, data, snapshot_id)

class SecurityGroupsControllerCollector(ControllerCollector):
    def getData(self):
        """
        Returns all the security groups nces with their host and project
        """
        sql = (
            "SELECT "
            "grup.id AS group_id, grup.name AS group_name, rule.direction, rule.ethertype, rule.protocol, "
            "rule.port_range_min, rule.port_range_max, rule.remote_ip_prefix, port.device_id AS instance "
            "FROM "
            "neutron.securitygroups AS grup, "
            "neutron.securitygrouprules AS rule, "
            "neutron.securitygroupportbindings AS bind, "
            "neutron.ports AS port "
            "WHERE "
            "grup.id = rule.security_group_id "
            "AND bind.security_group_id = grup.id "
            "AND bind.port_id = port.id "
            "AND port.device_owner = \"compute:nova\""
        )
        return super(SecurityGroupsControllerCollector, self).getData(sql)

    def saveData(self, data, snapshot_id):
        sql = ""
        return super(SecurityGroupsControllerCollector, self).saveData(sql, data, snapshot_id)


class RoutesControllerCollector(ControllerCollector):
    def getData(self):
        """
        Returns all the security groups nces with their host and project
        """
        sql = (
            "SELECT "
            "router.id AS router_id, router.name, port.id AS port_id, subnet.cidr, subnet.gateway_ip "
            "FROM "
            "neutron.routers AS router, "
            "neutron.ports AS port, "
            "neutron.ml2_port_bindings AS bind, "
            "neutron.networks AS net, "
            "neutron.subnets AS subnet "
            "WHERE "
            "router.status = \"ACTIVE\" "
            "AND router.id = port.device_id "
            "AND port.network_id = net.id "
            "AND subnet.network_id = net.id "
            "AND bind.port_id = port.id "
            "AND subnet.ip_version = 4 "
            "GROUP BY "
            "subnet.id"
        )
        return super(RoutesControllerCollector, self).getData(sql)

    def saveData(self, data, snapshot_id):
        """
        Saves instances with their host, project and snapshot into OpenAudit DB
        """
        sql = "INSERT INTO openaudit.snapshot_routes_controller (router_id, name, port_id, cidr, gateway_ip, snapshot_id) VALUES (%s, %s, %s, %s, %s, %s)"
        return super(RoutesControllerCollector, self).saveData(sql, data, snapshot_id)

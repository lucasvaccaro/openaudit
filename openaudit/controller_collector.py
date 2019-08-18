import database_connection as db


class ControllerCollector:
    db_conn_stack = None
    db_conn_local = None

    def __init__(self):
        self.db_conn_stack = db.DatabaseConnection("openstackDB")
        self.db_conn_stack = self.db_conn_stack.getConn();
        self.db_conn_local = db.DatabaseConnection("localDB")
        self.db_conn_local = self.db_conn_local.getConn();


class IsolationControllerCollector(ControllerCollector):
    def getControllerData(self):
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

    def saveControllerData(self, controller_data, snapshot_id):
        sql_insert = "INSERT INTO openaudit.snapshot_isolation_controller (uuid, host, project_id, snapshot_id) VALUES (%s, %s, %s, %s)"
        cursor = self.db_conn_local.cursor()
        for values in controller_data:
            _values = list(values)
            _values.append(snapshot_id)
            cursor.execute(sql_insert, _values)
        self.db_conn_local.commit()
        return cursor.rowcount
    

class SecurityGroupsControllerCollector(ControllerCollector):
    def getControllerData(self):
        """
        Returns all the security groups nces with their host and project
        """
        db_cursor = self.db_conn_stack.cursor(dictionary=True)
        db_cursor.execute(
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
        return db_cursor.fetchall()

    def saveControllerData(self):
        db_cursor = self.db_conn_local.cursor()


class RoutesControllerCollector(ControllerCollector):
    pass
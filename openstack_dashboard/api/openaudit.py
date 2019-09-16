import MySQLdb as mysql
import logging as log


DATABASE_HOST = "127.0.0.1"
DATABASE_USER = "root"
DATABASE_PASS = "root"
DATABASE_SCHEMA = "openaudit"


class DatabaseConnection:

    conn = None

    def __init__(self):
        try: 
            self.conn = mysql.connect(
                host=DATABASE_HOST,
                user=DATABASE_USER,
                password=DATABASE_PASS,
                db=DATABASE_SCHEMA
            )
        except mysql.Error as e:
            log.error("Could not connect to the database", exc_info=True)

    def close(self):
        self.conn.close()

    def getConn(self):
        return self.conn


class Snapshot:

    db_conn = None

    def setDBConn(self):
        db_conn = DatabaseConnection()
        self.db_conn = db_conn.getConn()

    def setParams(self, id, timestamp, issues):
        self.id = id
        self.timestamp = timestamp
        self.issues = issues

    def fetchAll(self):
        if (self.db_conn is None):
            self.setDBConn()
        sql = "SELECT * FROM snapshots ORDER BY timestamp DESC"
        db_cursor = self.db_conn.cursor()
        db_cursor.execute(sql)
        ls = db_cursor.fetchall()
        self.db_conn.close()
        obj_ls = []
        for row in ls:
            s = Snapshot()
            s.setParams(row[0], row[1], row[2])
            obj_ls.append(s)
        return obj_ls

    def fetchOne(self, snapshot_id):
        if (self.db_conn is None):
            self.setDBConn()
        sql = "SELECT * FROM snapshots WHERE id = %s"
        db_cursor = self.db_conn.cursor()
        db_cursor.execute(sql, (snapshot_id,))
        row = db_cursor.fetchone()
        self.db_conn.close()
        s = Snapshot()
        s.setParams(row[0], row[1], None)
        return s

    def fetchAllIssues(self, snapshot_id):
        if (self.db_conn is None):
            self.setDBConn()
        sql = (
            "SELECT 1 AS layer, IFNULL(host, uuid) AS device, IF(uuid IS NULL, 0, 1) AS issue_type FROM report_isolation WHERE snapshot_id = %s "
            "UNION "
            "SELECT 2 AS layer, port_id AS device, NULL AS issue_type FROM report_securitygroups WHERE snapshot_id = %s"
            "UNION "
            "SELECT 3 AS layer, CONCAT(router_id, \" : \", port_id) AS device, NULL AS issue_type FROM report_routes WHERE snapshot_id = %s "
        )
        db_cursor = self.db_conn.cursor()
        db_cursor.execute(sql, (snapshot_id,)*3)
        ls = db_cursor.fetchall()
        self.db_conn.close()
        obj_ls = []
        id = 0
        for row in ls:
            i = self.SnapshotIssue()
            i.setParams(id, row[0], row[1], row[2])
            obj_ls.append(i)
            id += 1
        return obj_ls

    class SnapshotIssue:
        layer_isolation = 1
        layer_secgroup = 2
        layer_routes = 3
        layers = {
            layer_isolation: "Isolation of VM",
            layer_secgroup: "Security Groups",
            layer_routes: "Routing"
        }

        def setParams(self, id, layer, device, issue_type):
            self.id = id
            self.layer = self.layers[layer]
            self.device = device
            if layer == self.layer_isolation:
                if issue_type == 0:
                    self.issue = "This host is running instances from different tenants"
                else:
                    self.issue = "This instance was not found in the host"
            elif layer == self.layer_secgroup:
                self.issue = "There is an inconsistency in the OpenFlow rules of this port"
            elif layer == self.layer_routes:
                self.issue = "There is an inconsistency in the network configuration of this router:port"
            else:
                self.issue = None


def fetch_all():
    s = Snapshot()
    return s.fetchAll()

def fetch_one(snapshot_id):
    s = Snapshot()
    return s.fetchOne(snapshot_id)

def fetch_all_issues(snapshot_id):
    s = Snapshot()
    return s.fetchAllIssues(snapshot_id)    
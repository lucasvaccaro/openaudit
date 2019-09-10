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


def fetch_all():
    s = Snapshot()
    return s.fetchAll()

def fetch_one(snapshot_id):
    s = Snapshot()
    return s.fetchOne(snapshot_id)

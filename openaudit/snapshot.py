import database_connection as db


class Snapshot:
    db_conn = None
    id = None
    
    def __init__(self):
        self.db_conn = db.DatabaseConnection("openauditDB")
        self.db_conn = self.db_conn.getConn();

    def create(self):
        """
        Creates a new snapshot record in the OpenAuditDB
        Returns the ID generated
        """
        sql = "INSERT INTO openaudit.snapshots (id) VALUES (NULL)"
        cursor = self.db_conn.cursor()
        cursor.execute(sql)
        self.db_conn.commit()
        self.id = cursor.lastrowid
        return self.id

    def getLastId(self):
        """
        Retrieves the ID of the last snapshot created
        """
        sql = "SELECT id FROM openaudit.snapshots ORDER BY timestamp DESC LIMIT 1"
        cursor = self.db_conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        self.id = row[0]
        return self.id

    def getUnverifiedSnapshot(self):
        """
        Retrieves the ID of the oldest unverified snapshot
        """
        sql = "SELECT id FROM openaudit.snapshots WHERE verified = 0 ORDER BY timestamp ASC LIMIT 1"
        cursor = self.db_conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        self.id = row[0]
        return self.id

    def setVerified(self):
        """
        Sets the snapshot as verified
        """
        sql = "UPDATE openaudit.snapshots SET verified = 1 WHERE id = %s"
        cursor = self.db_conn.cursor()
        cursor.execute(sql, (self.id,))
        self.db_conn.commit()

    def updateIssues(self, num):
        """
        Udates (adds) the number of issues of a snapshot
        """
        sql = "UPDATE openaudit.snapshots SET issues = issues + %s WHERE id = %s"
        cursor = self.db_conn.cursor()
        cursor.execute(sql, (num, self.id,))
        self.db_conn.commit()

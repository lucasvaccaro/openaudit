import database_connection as db


class Snapshot:
    db_conn = None
    id = None
    
    def __init__(self):
        self.db_conn = db.DatabaseConnection("openauditDB")
        self.db_conn = self.db_conn.getConn();

    def updateIssues(self, num):
        sql = "UPDATE openaudit.snapshots SET issues = issues + %s WHERE id = %s"
        cursor = self.db_conn.cursor()
        cursor.execute(sql, (num, self.id,))
        self.db_conn.commit()

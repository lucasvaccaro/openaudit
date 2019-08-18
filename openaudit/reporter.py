import database_connection as db


class Reporter:
    db_conn = None
    
    def __init__(self):
        self.db_conn = db.DatabaseConnection("localDB")
        self.db_conn = self.db_conn.getConn();


class IsolationReporter(Reporter):
    def save(self, noncompliant_hosts):
        """
        Saves uncompliant hosts into openaudit DB
        Returns number of rows inserted
        """
        sql_insert = "INSERT INTO openaudit.report_isolation (host) VALUES (%s)"
        cursor = self.db_conn.cursor()
        cursor.executemany(sql_insert, zip(noncompliant_hosts))
        self.db_conn.commit()
        return cursor.rowcount
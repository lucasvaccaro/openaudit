import database_connection as db


class Reporter:
    db_conn = None
    
    def __init__(self):
        self.db_conn = db.DatabaseConnection("openauditDB")
        self.db_conn = self.db_conn.getConn();


class IsolationReporter(Reporter):
    def saveData(self, noncompliant_hosts, missing_instances):
        """
        Saves uncompliant hosts and missing instances into OpenAudit DB
        Returns number of rows inserted
        """
        rowcount = 0

        if noncompliant_hosts:
            sql_insert = "INSERT INTO openaudit.report_isolation (host) VALUES (%s)"
            cursor = self.db_conn.cursor()
            cursor.executemany(sql_insert, zip(noncompliant_hosts))
            self.db_conn.commit()
            rowcount += cursor.rowcount

        if missing_instances:
            sql_insert = "INSERT INTO openaudit.report_isolation (uuid) VALUES (%s)"
            cursor = self.db_conn.cursor()
            cursor.executemany(sql_insert, zip(missing_instances))
            self.db_conn.commit()
            rowcount += cursor.rowcount

        return rowcount
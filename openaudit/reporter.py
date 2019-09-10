import database_connection as db
from abc import ABCMeta, abstractmethod
import snapshot


class Reporter:
    db_conn = None
    snap = None
    
    def __init__(self, snapshot_id):
        self.db_conn = db.DatabaseConnection("openauditDB")
        self.db_conn = self.db_conn.getConn();
        self.snap = snapshot.Snapshot()
        self.snap.id = snapshot_id


class IsolationReporter(Reporter):

    def saveData(self, noncompliant_hosts, missing_instances):
        """
        Saves uncompliant hosts and missing instances into OpenAudit DB
        Returns number of rows inserted
        """
        
        rowcount = 0

        if noncompliant_hosts:
            sql_insert = "INSERT INTO openaudit.report_isolation (snapshot_id, host) VALUES (%s, %s)"
            cursor = self.db_conn.cursor()
            for host in noncompliant_hosts:
                cursor.execute(sql_insert, (self.snap.id, host))
                rowcount += cursor.rowcount
            self.db_conn.commit()
            
        if missing_instances:
            sql_insert = "INSERT INTO openaudit.report_isolation (snapshot_id, uuid) VALUES (%s, %s)"
            cursor = self.db_conn.cursor()
            for inst in missing_instances:
                cursor.execute(sql_insert, (self.snap.id, inst))
                rowcount += cursor.rowcount
            self.db_conn.commit()

        if rowcount > 0:
            self.snap.updateIssues(rowcount)

        return rowcount


class SecurityGroupsReporter(Reporter):

    def saveData(self, inconsistent_ports):
        """
        Saves inconsistent ports into OpenAudit DB
        Returns number of rows inserted
        """
        rowcount = 0
        sql_insert = "INSERT INTO openaudit.report_securitygroups (port_id, snapshot_id) VALUES (%s, %s)"
        cursor = self.db_conn.cursor()
        for port in inconsistent_ports:
            cursor.execute(sql_insert, (port, self.snap.id))
            rowcount += cursor.rowcount
        self.db_conn.commit()
        if rowcount > 0:
            self.snap.updateIssues(rowcount)
        return rowcount


class RoutesReporter(Reporter):
     
    def saveData(self, inconsistent_routes):
        """
        Saves inconsistent routes into OpenAudit DB
        Returns number of rows inserted
        """
        rowcount = 0
        sql_insert = "INSERT INTO openaudit.report_routes (router_id, port_id, snapshot_id) VALUES (%s, %s, %s)"
        cursor = self.db_conn.cursor()
        for routes in inconsistent_routes:
            cursor.execute(sql_insert, routes + (self.snap.id,))
            rowcount += cursor.rowcount
        self.db_conn.commit()
        if rowcount > 0:
            self.snap.updateIssues(rowcount)
        return rowcount
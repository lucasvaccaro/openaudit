import database_connection as db
from abc import ABCMeta, abstractmethod


class Reporter:
    db_conn = None
    
    def __init__(self):
        self.db_conn = db.DatabaseConnection("openauditDB")
        self.db_conn = self.db_conn.getConn();


class IsolationReporter(Reporter):

    """
    Saves uncompliant hosts and missing instances into OpenAudit DB
    Returns number of rows inserted
    """
    def saveData(self, snapshot_id, noncompliant_hosts, missing_instances):
        
        rowcount = 0

        if noncompliant_hosts:
            sql_insert = "INSERT INTO openaudit.report_isolation (snapshot_id, host) VALUES (%s, %s)"
            cursor = self.db_conn.cursor()
            for host in noncompliant_hosts:
                cursor.execute(sql_insert, (snapshot_id, host))
                rowcount += cursor.rowcount
            self.db_conn.commit()
            
        if missing_instances:
            sql_insert = "INSERT INTO openaudit.report_isolation (snapshot_id, uuid) VALUES (%s, %s)"
            cursor = self.db_conn.cursor()
            for inst in missing_instances:
                cursor.execute(sql_insert, (snapshot_id, inst))
                rowcount += cursor.rowcount
            self.db_conn.commit()

        return rowcount


class SecurityGroupsReporter(Reporter):
    def saveData(self):
        pass


class RoutesReporter(Reporter):
    """
    Saves inconsistent routes into OpenAudit DB
    Returns number of rows inserted
    """ 
    def saveData(self, snapshot_id, inconsistent_routes):
        
        rowcount = 0

        sql_insert = "INSERT INTO openaudit.report_routes (router_id, port_id, snapshot_id) VALUES (%s, %s, %s)"
        cursor = self.db_conn.cursor()
        for routes in inconsistent_routes:
            cursor.execute(sql_insert, routes + (snapshot_id,))
            rowcount += cursor.rowcount
        self.db_conn.commit()

        return rowcount
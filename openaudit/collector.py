import database_connection as db

class Collector:
    db_conn_stack = None
    db_conn_local = None

    def __init__(self):
        self.db_conn_stack = db.DatabaseConnection("openstackDB")
        self.db_conn_stack = db_conn_stack.getConn();
        self.db_conn_local = db.DatabaseConnection("localDB")
        self.db_conn_local = db_conn_local.getConn();


class SecurityGroupsCollector(Collector):
    pass

class RoutesCollector(Collector):
    pass

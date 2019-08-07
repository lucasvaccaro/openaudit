import database_connection as db

class Verifier:
    db_conn_stack = None
    db_conn_local = None

    def __init__(self):
        self.db_conn_stack = db.DatabaseConnection("openstackDB")
        self.db_conn_stack = self.db_conn_stack.getConn();
        self.db_conn_local = db.DatabaseConnection("localDB")
        self.db_conn_local = self.db_conn_local.getConn();

class IsolationVerifier(Verifier):

    def listInstances(self):
        db_cursor = self.db_conn_stack.cursor()
        db_cursor.execute(
            "SELECT i.uuid, i.host, i.project_id, p.name AS project_name "
            "FROM nova_cell1.instances AS i, keystone.project AS p "
            "WHERE i.deleted = 0 "
            "AND i.project_id = p.id;"
        )
        instances = db_cursor.fetchall()
        for i in instances:
            print(i)

class SecurityGroupsVerifier(Verifier):
    pass

class RoutesVerifier(Verifier):
    pass

i = IsolationVerifier()
i.listInstances()
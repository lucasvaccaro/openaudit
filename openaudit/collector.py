import database_connection as db

db_conn_local = db.DatabaseConnection("localDB")
db_conn_local = db_conn.getConn();

db_conn_stack = db.DatabaseConnection("openstackDB")
db_conn_stack = db_conn.getConn();

def collectIsolation():
    # SELECT * FROM keystone.project;
    # SELECT * FROM nova_cell1.instances;
    return

def collectSecurityGroups():
    # SELECT * FROM neutron.securitygroup;
    # SELECT * FROM neutron.securitygrouprules;
    return

def collectRoutes():
    return
from abc import ABCMeta, abstractmethod
import database_connection as db


class ComputeCollector():
    __metaclass__ = ABCMeta

    db_conn = None

    def __init__(self):
        self.db_conn = db.DatabaseConnection("openauditDB")
        self.db_conn = self.db_conn.getConn();

    @abstractmethod
    def getData(self):
        pass

    @abstractmethod
    def parseData(self, data):
        pass

    @abstractmethod
    def saveData(self, data, snapshot_id):
        pass


class IsolationComputeCollector(ControllerCollector):
    def getData(self):
        pass

    def parseData(self, data):
        pass

    def saveData(self, data, snapshot_id):
        pass
    

class SecurityGroupsComputeCollector(ControllerCollector):
    def getData(self):
        pass

    def parseData(self, data):
        pass

    def saveData(self, data, snapshot_id):
        pass


class RoutesComputeCollector(ControllerCollector):
    def getData(self):
        pass

    def parseData(self, data):
        pass

    def saveData(self, data, snapshot_id):
        pass


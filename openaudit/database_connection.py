import configparser
import mysql.connector as mysql
from mysql.connector import Error
import logging as log

class DatabaseConnection:

    conn = None

    def __init__(self, dbConfig):
        config = configparser.ConfigParser()
        config.read("config.ini")
        try: 
            self.conn = mysql.connect(
                host=config[dbConfig]["host"],
                user=config[dbConfig]["user"],
                password=config[dbConfig]["pass"]
            )
        except Error as e :
            log.error("Could not connect to the database", exc_info=True)

    def close(self):
        self.conn.close()

    def getConn(self):
        return self.conn

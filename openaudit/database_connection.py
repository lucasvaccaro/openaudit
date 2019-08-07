import configparser
import mysql.connector as mysql
from mysql.connector import Error

class DatabaseConnection:

    conn = None

    def __init__(self, dbConfig):
        config = configparser.ConfigParser()
        config.read('config.ini')
        try: 
            conn = mysql.connect(
                host=config[dbConfig]['host'],
                user=config[dbConfig]['user'],
                password=config[dbConfig]['pass']
            )
            self.conn = conn
        except Error as e :
            print ("Error while connecting to database", e)

    def getConn(self):
        return self.conn

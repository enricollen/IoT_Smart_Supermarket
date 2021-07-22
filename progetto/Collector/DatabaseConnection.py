import mysql.connector
from mysql.connector import errorcode

DATABASE_CONFIG = {
  'user': 'paciollen',
  'password': '',
  'host': '127.0.0.1',
  'database': 'smart_supermarket',
  #'raise_on_warnings': True
}


class DatabaseConnection:
    dbConn = 0
    cursor = 0

    def __init__(self):
        try:
            self.dbConn = mysql.connector.connect(**DATABASE_CONFIG)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        #else:
        #self.cursor = self.dbConn.cursor()
        #self.dbConn.close()



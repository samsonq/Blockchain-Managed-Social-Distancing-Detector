import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode


class OffChain:
    """
    Manages off-chain database storage to insert and select social distancing events.
    """
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(host='localhost',
                                                      database='Maxonrow',
                                                      user='root',
                                                      password='')
            self.cursor = self.connection.cursor()
        except Error as error:
            print("Failed to insert record into table {}".format(error))

    def insert(self, query):
        """
        Inserts event into off-chain database.
        :param query: insert query
        """
        self.cursor.execute(query)
        self.connection.commit()

    def select(self, query):
        """
        Retrieves event from off-chain database.
        :param query: select query
        :return: event records
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close_connection(self):
        """
        Close connection to database.
        """
        self.cursor.close()

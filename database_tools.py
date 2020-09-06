from psycopg2 import *


class DatabaseTools:
    __config_db = {'db': 'ask_mate',
                   'username': 'postgre',
                   'password': 'brzozasr',
                   'host': 'localhost',
                   'port': '5432'}

    def __init__(self):
        self.__db = self.__config_db['db']
        self.__username = self.__config_db['username']
        self.__password = self.__config_db['password']
        self.__host = self.__config_db['host']
        self.__port = self.__config_db['port']
        self.__cursor = None
        self.__connection = None

    def connect_db(self):
        try:
            self.__connection = connect(database=self.__db, username=self.__username, password=self.__password,
                                        host=self.__host, port=self.__port)
            self.__cursor = self.__connection.cursor()
        except Error as e:
            print(f'There is problem with connection: {e}!!!')

    def execute_query(self, query):
        try:
            self.__cursor.execute(query)
            self.__connection.commit()
        except OperationalError as e:
            print(f'There is problem with operation: {e}!!!')

    def close_connection(self):
        try:
            self.__cursor.close()
            self.__connection.close()
        except Error as e:
            print(f'There is with closing data base: {e}!!!')

    def __create_db_tables(self):
        """Creating tables in ask_mate database"""
        pass


db = DatabaseTools()

import psycopg2


class DatabaseTools:
    __config_db = {'db': 'ask_mate',
                   'username': 'postgre',
                   'password': 'brzozasr',
                   'port': '5432'}

    def __init__(self):
        self.__db = self.__config_db['db']
        self.__username = self.__config_db['username']
        self.__password = self.__config_db['password']
        self.__port = self.__config_db['port']
        self.__cursor = None
        self.__connection = None

    def connect_db(self):
        pass

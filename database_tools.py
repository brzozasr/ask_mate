from psycopg2 import *


class DatabaseTools:
    __config_db = {'db': 'ask_mate',
                   'user': 'postgres',
                   'password': '1234',
                   'host': 'localhost',
                   'port': '5432'}

    def __init__(self):
        self.__db = self.__config_db['db']
        self.__username = self.__config_db['user']
        self.__password = self.__config_db['password']
        self.__host = self.__config_db['host']
        self.__port = self.__config_db['port']
        self.__cursor = None
        self.__connection = None

    def execute_sql(self, query, data=None):
        self.__connect_db()
        result = self.__execute_query(query, data)
        self.__close_connection()
        return result

    def __connect_db(self):
        try:
            self.__connection = connect(database=self.__db, user=self.__username, password=self.__password,
                                        host=self.__host, port=self.__port)
            self.__cursor = self.__connection.cursor()
        except Error as e:
            print(f'There is a problem with connection: {e}')

    def __execute_query(self, query, data=None):
        try:
            self.__cursor.execute(query, data)
            if 'SELECT' in str(self.__cursor.query).upper() or 'RETURNING' in str(self.__cursor.query).upper():
                return self.__cursor.fetchall()
        except (Error, OperationalError) as e:
            print(f'There is a problem with operation: {e}')
        finally:
            self.__connection.commit()

    def __close_connection(self):
        try:
            self.__cursor.close()
            self.__connection.close()
        except Error as e:
            print(f'There is a problem with closing database: {e}')

    def __create_db_tables(self):
        """Creating tables in ask_mate database - PostgreSQL.
        Commands to create tables in the IDE terminal:
        % python3
        % from database_tools import *
        % db._DatabaseTools__create_db_tables()
        % exit()"""
        tables = (
            """CREATE TABLE IF NOT EXISTS question (
            id SERIAL PRIMARY KEY,
            submission_time TIMESTAMP NOT NULL DEFAULT NOW(),
            view_number INT NOT NULL DEFAULT 0,
            vote_number INT NOT NULL DEFAULT 0,
            title VARCHAR ( 255 ) NOT NULL,
            message TEXT NOT NULL,
            image VARCHAR ( 255 ) UNIQUE
            )""",

            """CREATE TABLE IF NOT EXISTS answer (
            id SERIAL PRIMARY KEY,
            submission_time TIMESTAMP NOT NULL DEFAULT NOW(),
            vote_number INT NOT NULL DEFAULT 0,
            question_id INT NOT NULL REFERENCES question ( id ) ON DELETE CASCADE,
            message TEXT NOT NULL,
            image VARCHAR ( 255 ) UNIQUE
            )""",

            """CREATE TABLE IF NOT EXISTS comment (
            id SERIAL PRIMARY KEY,
            question_id INT NOT NULL REFERENCES question ( id ) ON DELETE CASCADE,
            answer_id INT NOT NULL REFERENCES answer ( id ) ON DELETE CASCADE,
            message TEXT NOT NULL,
            submission_time TIMESTAMP NOT NULL DEFAULT NOW(),
            edited_number INT NOT NULL DEFAULT 0
            )""",

            """CREATE TABLE IF NOT EXISTS tag (
            id SERIAL PRIMARY KEY,
            title VARCHAR ( 100 ) NOT NULL
            )""",

            """CREATE TABLE IF NOT EXISTS question_tag (
            question_id INT NOT NULL REFERENCES question ( id ) ON DELETE CASCADE,
            tag_id INT NOT NULL REFERENCES tag ( id ) ON DELETE CASCADE
            )"""
        )

        self.__connect_db()
        for table in tables:
            self.__execute_query(table)
        self.__close_connection()


db = DatabaseTools()

from psycopg2 import *
from config_sql import *


class DatabaseTools:
    def __init__(self):
        self.__db = DB_NAME
        self.__username = DB_USER
        self.__password = DB_PASSWORD
        self.__host = DB_HOST
        self.__port = DB_PORT
        self.__cursor = None
        self.__connection = None

    def execute_sql(self, query, data=None):
        self.__connect_db()
        result = self.__execute_query(query, data)
        self.__close_connection()
        return result

    def execute_multi_sql(self, query, data: list):
        """ONLY FOR NOT RETURNING QUERY. DO NOT USE 'SELECT' AND 'RETURNING'\n
        Argument "data" has to be a list of lists or a list of tuples.\n
        Example: [['title1', 'question1'], ['title2', 'question2']]."""
        if 'SELECT' not in query.upper() and 'RETURNING' not in query.upper():
            if all([isinstance(el, (list, tuple)) for el in data] + [len(data) > 0]):
                self.__connect_db()
                for sql_data in data:
                    if len(sql_data) > 0:
                        self.__execute_query(query, sql_data)
                self.__close_connection()
            else:
                print('Required data: a list of lists or a list of tuples!')
        else:
            print('Method "execute_multi_sql" ONLY FOR NOT RETURNING QUERY!')

    def __connect_db(self):
        try:
            self.__connection = connect(database=self.__db, user=self.__username, password=self.__password,
                                        host=self.__host, port=self.__port)
            self.__cursor = self.__connection.cursor()
        except Error as e:
            print(f'There is a problem with connection: {e}')

    def __execute_query(self, query, data=None):
        error = None
        try:
            self.__cursor.execute(query, data)
            if 'SELECT' in str(self.__cursor.query).upper() or 'RETURNING' in str(self.__cursor.query).upper():
                return self.__cursor.fetchall()
        except (Error, OperationalError) as e:
            print(f'There is a problem with operation: {e}')
            error = str(e)
        finally:
            self.__connection.commit()
            if error is not None:
                return f'There is a problem with operation: {error}'

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
            answer_id INT REFERENCES answer ( id ) ON DELETE CASCADE,
            message TEXT NOT NULL,
            submission_time TIMESTAMP NOT NULL DEFAULT NOW(),
            edited_number INT NOT NULL DEFAULT 0
            )""",

            """CREATE TABLE IF NOT EXISTS tag (
            id SERIAL PRIMARY KEY,
            title VARCHAR ( 100 ) NOT NULL UNIQUE
            )""",

            """CREATE TABLE IF NOT EXISTS question_tag (
            id SERIAL PRIMARY KEY,
            question_id INT NOT NULL REFERENCES question ( id ) ON DELETE CASCADE,
            tag_id INT NOT NULL REFERENCES tag ( id ) ON DELETE CASCADE,
            UNIQUE ( question_id, tag_id )
            )"""
        )

        self.__connect_db()
        for table in tables:
            self.__execute_query(table)
        self.__close_connection()


db = DatabaseTools()

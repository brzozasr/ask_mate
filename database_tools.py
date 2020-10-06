from psycopg2 import *
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import *


class DatabaseTools:
    pg_db = PG_DB
    pg_username = PG_USERNAME
    pg_password = PG_PASSWORD
    pg_host = PG_HOST
    pg_port = PG_PORT

    us_db = US_DB
    us_username = US_USERNAME
    us_password = US_PASSWORD

    def __init__(self):
        self.__db_name = DatabaseTools.us_db
        self.__username = DatabaseTools.us_username
        self.__password = DatabaseTools.us_password
        self.__host = DatabaseTools.pg_host
        self.__port = DatabaseTools.pg_port
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

    def __connect_db(self, dbname=us_db, username=us_username, pwd=us_password):
        try:
            self.__connection = connect(database=dbname, user=username, password=pwd,
                                        host=self.__host, port=self.__port)
            self.__cursor = self.__connection.cursor()
        except Error as e:
            print(f'There is a problem with connection: {e}')

    def __execute_query(self, query, data=None):
        """Execute query with a transaction (with commit).
        Use this for INSERT, UPDATE, DELETE."""
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
        """Creating database, tables and a user in PostgreSQL.
        Commands to create database, tables and a user in the IDE terminal:
        % python3
        % from database_tools import *
        % db._DatabaseTools__create_db_tables()
        % exit()"""
        tables = (
            """CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR ( 255 ) NOT NULL UNIQUE,
            pwd VARCHAR ( 255 ) NOT NULL,
            registration_time TIMESTAMP NOT NULL DEFAULT NOW(),
            reputation INT NOT NULL DEFAULT 0
            )""",

            """CREATE TABLE IF NOT EXISTS question (
            id SERIAL PRIMARY KEY,
            submission_time TIMESTAMP NOT NULL DEFAULT NOW(),
            view_number INT NOT NULL DEFAULT 0,
            vote_number INT NOT NULL DEFAULT 0,
            title VARCHAR ( 255 ) NOT NULL,
            message TEXT NOT NULL,
            image VARCHAR ( 255 ) UNIQUE,
            user_id INT NOT NULL REFERENCES users ( id ) ON DELETE CASCADE
            )""",

            """CREATE TABLE IF NOT EXISTS answer (
            id SERIAL PRIMARY KEY,
            submission_time TIMESTAMP NOT NULL DEFAULT NOW(),
            vote_number INT NOT NULL DEFAULT 0,
            question_id INT NOT NULL REFERENCES question ( id ) ON DELETE CASCADE,
            message TEXT NOT NULL,
            image VARCHAR ( 255 ) UNIQUE,
            user_id INT NOT NULL REFERENCES users ( id ) ON DELETE CASCADE,
            acceptance BOOLEAN NOT NULL DEFAULT FALSE
            )""",

            """CREATE TABLE IF NOT EXISTS comment (
            id SERIAL PRIMARY KEY,
            question_id INT NOT NULL REFERENCES question ( id ) ON DELETE CASCADE,
            answer_id INT REFERENCES answer ( id ) ON DELETE CASCADE,
            message TEXT NOT NULL,
            submission_time TIMESTAMP NOT NULL DEFAULT NOW(),
            edited_number INT NOT NULL DEFAULT 0,
            user_id INT NOT NULL REFERENCES users ( id ) ON DELETE CASCADE
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

        create_db = f"""CREATE DATABASE {DatabaseTools.us_db}
                    WITH 
                    OWNER = postgres
                    ENCODING = 'UTF8'
                    CONNECTION LIMIT = -1;"""

        create_user = f"""CREATE ROLE {DatabaseTools.us_username} WITH
                    LOGIN
                    NOSUPERUSER
                    NOCREATEDB
                    NOCREATEROLE
                    NOINHERIT
                    NOREPLICATION
                    CONNECTION LIMIT -1
                    PASSWORD '{DatabaseTools.us_password}';"""

        get_list_db = 'SELECT datname FROM pg_database;'
        self.__connect_db(DatabaseTools.pg_db, DatabaseTools.pg_username, DatabaseTools.pg_password)
        db_list = self.__execute_query(get_list_db)
        self.__close_connection()

        if (DatabaseTools.us_db,) not in db_list:
            self.__connect_db(DatabaseTools.pg_db, DatabaseTools.pg_username, DatabaseTools.pg_password)
            self.__connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.__cursor.execute(create_db)
            self.__close_connection()
        else:
            print(f'The database "{DatabaseTools.us_db}" exists!')

        get_user = f'SELECT rolname FROM pg_roles;'
        self.__connect_db(DatabaseTools.pg_db, DatabaseTools.pg_username, DatabaseTools.pg_password)
        user_list = self.__execute_query(get_user)
        self.__close_connection()

        if (DatabaseTools.us_username,) not in user_list:
            self.__connect_db(DatabaseTools.pg_db, DatabaseTools.pg_username, DatabaseTools.pg_password)
            self.__execute_query(create_user)
            self.__close_connection()
        else:
            print(f'The user "{DatabaseTools.us_username}" exists!')

        self.__connect_db(username=DatabaseTools.pg_username, pwd=DatabaseTools.pg_password)
        for table in tables:
            self.__execute_query(table)
        self.__execute_query(f"GRANT ALL ON SCHEMA public TO {DatabaseTools.us_username}")
        self.__execute_query(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {DatabaseTools.us_username}")
        self.__execute_query(f"GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO {DatabaseTools.us_username}")
        self.__close_connection()


db = DatabaseTools()

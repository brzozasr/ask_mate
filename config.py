from os import urandom

"""Data to login as postgres administrator."""
PG_DB = 'postgres'  # <-- DO NOT CHANGE - database name
PG_USERNAME = 'postgres'
PG_PASSWORD = 'brzozasr'

"""Host and port setting for connection to PostgreSQL."""
PG_HOST = 'localhost'
PG_PORT = '5432'

"""Data to login as postgres user to database named as the variable 'US_BD'.
This data is required to create a user if it does not exist."""
US_DB = 'ask_mate'
US_USERNAME = 'askmate'
US_PASSWORD = 'brzozasr1'

"""Session variables"""
SESSION_SECRET_KEY = urandom(64)
SESSION_USER_ID = 'user_id'
SESSION_USER_EMAIL = 'user_email'

"""Commend to add and revoke privileges to a database for a user."""
# GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO askmate; <-- askmate, it is a username
# REVOKE ALL ON ALL TABLES IN SCHEMA public FROM askmate;


# WORKING QUERY
# 'questions_search':
#         """SELECT DISTINCT q.id, q.submission_time, q.view_number, q.vote_number, q.title, q.message, q.image
#         FROM question q, answer a
#         WHERE q.title ILIKE %(search)s OR q.message ILIKE %(search)s OR (q.id = a.question_id AND a.message ILIKE %(search)s)
#         ORDER BY q.submission_time DESC"""

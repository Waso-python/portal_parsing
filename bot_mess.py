from re import template
import psycopg2
import json
import logging
from psycopg2 import OperationalError
from my_set import PASSWORD_DB, HOST_DB, PORT_DB, DB_NAME, USER_DB, BOT_DB, BOT_HOST_DB, BOT_PASSWORD_DB, BOT_PORT_DB, BOT_USER_DB
from datetime import datetime


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename="log.log", level=logging.INFO, format=FORMAT)


def loger(type, mess):
    if type == 'ERROR':
        logging.error(mess)
    else:
        logging.info(mess)

def create_conn():
    connection = None
    try:
        connection = psycopg2.connect(
            database=BOT_DB,
            user=BOT_USER_DB,
            password=BOT_PASSWORD_DB,
            host=BOT_HOST_DB,
            port=BOT_PORT_DB
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        loger('ERROR',f"MESSAGE_BOT_ERROR '{e}'")
        print(f"The error '{e}' occurred")
    return connection


def execute_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Query executed successfully")
    except OperationalError as e:
        loger('ERROR',e)
        print(f"The error '{e}' occurred")


con = create_conn()

insert_sql = """INSERT INTO public.message(
	text_mess, soft_id, priority)
	VALUES ({})"""

def add_to_table(items):
	sql_q = (insert_sql.format(items)).replace('[','').replace(']','') + ";"
	try:
		execute_query(con,sql_q)
	except Exception as e:
		loger('ERROR',e)
		print(e)




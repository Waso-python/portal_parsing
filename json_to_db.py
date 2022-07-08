from re import template
import psycopg2
import json
from psycopg2 import OperationalError
from my_set import PASSWORD_DB, HOST_DB, PORT_DB, DB_NAME, USER_DB
from datetime import datetime
from bot_mess import add_to_table


def error_bot(rec):
    rec = [rec, 1, 1]
    add_to_table(rec)

def create_connection():
    connection = None
    try:
        connection = psycopg2.connect(
            database=DB_NAME,
            user=USER_DB,
            password=PASSWORD_DB,
            host=HOST_DB,
            port=PORT_DB
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        error_bot(e)
        print(f"The error '{e}' occurred")
    return connection


def execute_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Query executed successfully")
    except OperationalError as e:
        error_bot(e)
        print(f"The error '{e}' occurred")


con = create_connection()

insert_sql = """INSERT INTO public.raw_table(
	num_proc, link_proc, status, type_proc, subj_proc, partner, partner_inn, summ_proc, count_order, region, law_proc, start_date, end_date, proc_comment, complete)
	VALUES ({},0)"""

with open('order.json') as f:
	templates = json.load(f)

def add_to_table(items):
	sql_q = (insert_sql.format(items)).replace('[','').replace(']','') + ";"
	try:
		execute_query(con,sql_q)
	except Exception as e:
		error_bot(e)
		print(e)

lst = []

for numb, commands in templates.items():
	lst.clear()
	lst.append(numb)
	for it in commands.items():
		lst.append(it[1])
	add_to_table(lst)


import hashlib
import os
from sqlite3 import paramstyle
import psycopg2
from configparser import ConfigParser

######### To use: change password in create_database() function and database.ini

def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        print(params)
        for param in params:
            print(param)
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db


#create database
def create_database():
    conn = None
    try:
        conn = psycopg2.connect(
        database="postgres",
        user='postgres',
        #may need to change password
        password='12345678',
        host='localhost',
        port= '5432'
        )

        conn.autocommit = True

        cur = conn.cursor()

        sql = '''CREATE database database_poker'''
        cur.execute(sql)

        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

#create users table
def create_users_table():
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)

        conn.autocommit = True

        cur = conn.cursor()

        sql = '''CREATE TABLE IF NOT EXISTS public.users
                (
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_key BYTEA NOT NULL,
                    password_salt BYTEA NOT NULL,
                    table_id INT,
                    bankroll MONEY NOT NULL DEFAULT 10000,
                    FOREIGN KEY (table_id) REFERENCES tables(table_id)
                )

                TABLESPACE pg_default;

                ALTER TABLE IF EXISTS public.users
                    OWNER to postgres;'''
        cur.execute(sql)

        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

#create tables table
# def create_tables_table():
#     conn = None
#     try:
#         params = config()
#         conn = psycopg2.connect(**params)

#         conn.autocommit = True

#         cur = conn.cursor()

#         sql = '''CREATE TABLE IF NOT EXISTS public.tables
#                 (
#                     table_id SERIAL PRIMARY KEY,
#                     small_blind MONEY NOT NULL,
#                     big_blind MONEY NOT NULL
#                 )

#                 TABLESPACE pg_default;

#                 ALTER TABLE IF EXISTS public.tables
#                     OWNER to postgres;'''
#         cur.execute(sql)

#         conn.close()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#     finally:
#         if conn is not None:
#             conn.close()

def insert_fake_user(username, password):
    salt = os.urandom(32)
    
    key = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt, 
        100000, 
        dklen=128)

    sql = """INSERT INTO public.users(
	username, password_key, password_salt)
	VALUES (%s, %s, %s) RETURNING user_id;"""

    conn = None

    user_id = None

    try:
        params = config()
        conn = psycopg2.connect(**params)

        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (username, key, salt))
        # get the generated id back
        user_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    print(user_id)
    return user_id

#filler users
#filler tables

if __name__ == '__main__':
    create_database()
    create_users_table()
    #fake users (username, password)
    fake_users = [("testuser", "password"), ("Tarek22", "87654321"), ("Stephen11","12345678")]
    for user_info in fake_users:
        username, password = user_info
        insert_fake_user(username, password)
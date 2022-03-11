import psycopg2
from configparser import ConfigParser

def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db


def retrieve_login_info(username):
  conn = None
  print("Trying to Retrieve Login Info")
  try:
        params = config()
        conn = psycopg2.connect(**params)

        conn.autocommit = True

        cur = conn.cursor()

        sql = '''SELECT user_id, username
	            FROM public.users WHERE username=%s;'''

        cur.execute(sql, (username,))
        print(cur)
        login_info = cur.fetchone()
        conn.close()
        print(login_info)
        return login_info
        
  except (Exception, psycopg2.DatabaseError) as error:
      print(error)
  finally:
      if conn is not None:
          conn.close()
username= 'testuser'
retrieve_login_info(username)
import sqlite3
connection_obj = sqlite3.connect('users.db')

cursor_obj = connection_obj.cursor()

table = """ CREATE TABLE IF NOT EXISTS USERS(
            ID INTEGER PRIMARY KEY,
            Username TEXT NOT NULL,
            Email TEXT NOT NULL,
            Password TEXT NOT NULL
            )
"""

sel = """SELECT * FROM USERS"""
delete = """DELETE FROM USERS"""
drop = """DROP TABLE USERS"""
check_user = '''SELECT Username FROM USERS WHERE Username=?'''

cursor_obj.execute(table)
cursor_obj.execute(delete)
print(cursor_obj.execute(check_user, ("jora",)).fetchone())
connection_obj.commit()


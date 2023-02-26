import sqlite3
connection_obj = sqlite3.connect('users.db')

cursor_obj = connection_obj.cursor()

table_users = """ CREATE TABLE IF NOT EXISTS USERS(
            ID INTEGER PRIMARY KEY,
            Username TEXT NOT NULL,
            Email TEXT NOT NULL,
            Password TEXT NOT NULL
            )
"""

table_Quizes = """ CREATE TABLE IF NOT EXISTS QUIZES(
                    Quiz_ID INTEGER PRIMARY KEY,
                    Course INT NOT NULL,
                    Main_Topic INT NOT NULL,
                    Topic INT NOT NULL,
                    Jason_file TEXT NOT NULL
                )
"""

table_scores = """ CREATE TABLE IF NOT EXISTS SCORES(
                Score_ID INTEGER PRIMARY KEY,
                Username TEXT NOT NULL,
                Correct INT NOT NULL,
                Wrong INT NOT NULL,
                Quiz_ID INT,
                FOREIGN KEY (Quiz_ID) references QUIZES(Quiz_ID)
                )
"""

sel = """SELECT * FROM USERS"""
delete_users = """DELETE FROM USERS"""
delete_scores = """DELETE FROM SCORES"""
delete_quizes = """DELETE FROM QUIZES"""
drop = """DROP TABLE SCORES"""
check_user = '''SELECT Username FROM USERS WHERE Username=?'''


cursor_obj.execute(table_users)
cursor_obj.execute(table_Quizes)
cursor_obj.execute(table_scores)
# cursor_obj.execute(delete_quizes)
connection_obj.commit()


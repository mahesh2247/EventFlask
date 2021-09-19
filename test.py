import sqlite3
my_dict = {}

con = sqlite3.connect('mydb.db')
cur = con.cursor()
cur.execute("SELECT * from user_model;")
rows = cur.fetchall()


for i in range(len(rows)):
    print(rows[i][0])


# my_tup = (('mahesh', '123'), ('prakash', '456'))
#
# print(my_tup[0][1])



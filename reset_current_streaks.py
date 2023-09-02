import sqlite3
from datetime import date
from datetime import timedelta
from config import dbpath

connection = sqlite3.connect(dbpath)
cur = connection.cursor()
rows = cur.execute('SELECT * FROM fartstreak').fetchall()

for row in rows:
     print(row)
     print(row[5])
     today = date.today()
     print(today)
     print(row[4])
     print(str(today - timedelta(days = 1)))
     print(str(today - timedelta(days = 2)))
     if(row[4] != str(today) and row[4] != str(today - timedelta(days = 1))):
          print('reset')
          
          cur.execute(f"""UPDATE fartstreak 
          SET currentstreak_length = 0
          WHERE
               userid = {row[0]};""")
          connection.commit()

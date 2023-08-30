import sqlite3
from datetime import date
from datetime import timedelta

connection = sqlite3.connect("/home/pi/projects/fartbot/fartstreak.db")
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
          
          #remove role for general chat. the 0 is a placeholder, replace with the ID of the correct role
          await message.author.remove_roles(get(message.author.guild.roles, id=0))
                
          cur.execute(f"""UPDATE fartstreak 
          SET currentstreak_length = 0
          WHERE
               userid = {row[0]};""")
          connection.commit()

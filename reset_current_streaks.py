import sqlite3
from datetime import date
from datetime import timedelta

cur = sqlite3.connect("/home/pi/projects/fartbot/fartstreak.db").cursor()
rows = cur.execute('SELECT * FROM fartstreak').fetchall()

for row in rows:
     print(row)



# db.execute(f'SELECT * FROM fartstreak WHERE userid = {message.author.id};') as cursor:


# async with aiosqlite.connect("/home/pi/projects/fartbot/fartstreak.db") as db:
#         async with db.execute('SELECT * FROM fartstreak') as cursor:
#             rows = await cursor.fetchall()
#             for row in rows:
#                 user = await client.fetch_user(row[0])
#                 #print(user)
#                 await db.execute(f"""UPDATE fartstreak 
#                                     SET pfp = '{user.display_avatar.url}',
#                                         name = '{user.name}',
#                                         total = {max(row[9],row[5])}
#                                     WHERE
#                                         userid = {row[0]};""")
#                 await db.commit()
#     await interaction.followup.send(content='done', ephemeral = True)
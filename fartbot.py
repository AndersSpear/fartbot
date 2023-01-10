import discord
import re
import aiosqlite
from datetime import date
from datetime import timedelta
from token import TOKEN

class MyClient(discord.Client):
    #db = None
    
    async def on_ready(self):
        #db = await aiosqlite.connect("fartstreak.db")
        print(f'Logged on as {self.user}!')

    async def on_member_join(self, member):
        #print(f'{member} has joined the server')
        await member.edit(nick = 'fart club')

    async def on_message(self, message):
        #print(f'Message from {message.author}: {message.content}')
        if(message.channel.id == 1047644766877270038):
            if(not re.fullmatch(message.content, 'fart club')):
                await message.delete()
            else:
                async with aiosqlite.connect("/home/pi/projects/fartbot/fartstreak.db") as db:
                    async with db.execute(f'SELECT * FROM fartstreak WHERE userid = {message.author.id};') as cursor:
                        row = await cursor.fetchone()
                        today = date.today()
                        if(row == None):
                            await db.execute(f"INSERT INTO fartstreak (userid, longeststreak_start_date, longeststreak_end_date, longeststreak_length, currentstreak_start_date, currentstreak_end_date, currentstreak_length) VALUES ({message.author.id}, '{today}', '{today}', 1, '{today}', '{today}', 1);")
                            await db.commit()
                        else:
                            print(f'row: {row}')
                            print(f"streak end: {row[4]}\nyesterday date: {today - timedelta(days = 1)}")
                            if(row[4] == str(today - timedelta(days = 1))):
                                print('last message was yesterday')
                                if (row[6] + 1 > row[5]):
                                    await db.execute(f"""UPDATE fartstreak 
                                    SET longeststreak_start_date = '{row[3]}',
                                        longeststreak_end_date = '{today}',
                                        longeststreak_length = {row[6] + 1},
                                        currentstreak_end_date = '{today}',
                                        currentstreak_length = {row[6] + 1}
                                    WHERE
                                        userid = {message.author.id};""")
                                    await db.commit()
                                    #print("updated longest streak")
                                else:
                                    await db.execute(f"""UPDATE fartstreak 
                                    SET currentstreak_end_date = '{today}',
                                        currentstreak_length = {row[6] + 1}
                                    WHERE
                                        userid = {message.author.id};""")
                                    await db.commit()
                                    #print("updated only the current streak")
                            else:
                                if(row[4] != str(today)):
                                    await db.execute(f"""UPDATE fartstreak 
                                    SET currentstreak_end_date = '{today}',
                                        currentstreak_start_date = '{today}',
                                        currentstreak_length = 1
                                    WHERE
                                        userid = {message.author.id};""")
                                    await db.commit()
                                    print("reset the current streak")
    
                #print('allowed')


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = MyClient(intents=intents)
client.run(TOKEN)
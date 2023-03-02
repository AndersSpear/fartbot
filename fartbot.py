import discord
import re
import aiosqlite
from datetime import date
from datetime import timedelta
from authtoken import authTOKEN
from discord import app_commands

class MyClient(discord.Client):
    #db = None
    
    async def on_ready(self):
        #db = await aiosqlite.connect("fartstreak.db")
        print(f'Logged on as {self.user}!')
        await tree.sync(guild=discord.Object(id=1047644766311043162))

    async def on_member_join(self, member):
        #print(f'{member} has joined the server')
        await member.edit(nick = 'fart club')

    async def on_raw_message_edit(self, payload):
        #print("EDIT!!!")
        try:
            channel = await client.fetch_channel(1047644766877270038)
            #print(channel)
            message = await channel.fetch_message(payload.message_id)
            #print(message)
            await message.delete()
            #print("success")
        except:
            pass
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
                            
                            await db.execute(f"INSERT INTO fartstreak (userid, longeststreak_start_date, longeststreak_end_date, longeststreak_length, currentstreak_start_date, currentstreak_end_date, currentstreak_length, pfp, name, total) VALUES ({message.author.id}, '{today}', '{today}', 1, '{today}', '{today}', 1, '{message.author.display_avatar.url}', '{message.author.name}', 1);")
                            await db.commit()
                        else:
                            #print(f'row: {row}')
                            #print(f"streak end: {row[4]}\nyesterday date: {today - timedelta(days = 1)}")
                            if(row[4] == str(today - timedelta(days = 1))):
                                #print('last message was yesterday')
                                if (row[6] + 1 > row[5]):
                                    await db.execute(f"""UPDATE fartstreak 
                                    SET longeststreak_start_date = '{row[3]}',
                                        longeststreak_end_date = '{today}',
                                        longeststreak_length = {row[6] + 1},
                                        currentstreak_end_date = '{today}',
                                        currentstreak_length = {row[6] + 1},
                                        total = {row[9] + 1}
                                    WHERE
                                        userid = {message.author.id};""")
                                    await db.commit()
                                    #print("updated longest streak")
                                else:
                                    await db.execute(f"""UPDATE fartstreak 
                                    SET currentstreak_end_date = '{today}',
                                        currentstreak_length = {row[6] + 1},
                                        total = {row[9] + 1}
                                    WHERE
                                        userid = {message.author.id};""")
                                    await db.commit()
                                    #print("updated only the current streak")
                            else: 
                                if(row[4] != str(today)):
                                    await db.execute(f"""UPDATE fartstreak 
                                    SET currentstreak_end_date = '{today}',
                                        currentstreak_start_date = '{today}',
                                        currentstreak_length = 1,
                                        total = {row[9] + 1}
                                    WHERE
                                        userid = {message.author.id};""")
                                    await db.commit()
                                    #print("reset the current streak")
    
                #print('allowed')


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = MyClient(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name = "update", description = "adds pfp links and names to db", guild=discord.Object(id=1047644766311043162)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def update_db(interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    async with aiosqlite.connect("/home/pi/projects/fartbot/fartstreak.db") as db:
        async with db.execute('SELECT * FROM fartstreak') as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                user = await client.fetch_user(row[0])
                #print(user)
                await db.execute(f"""UPDATE fartstreak 
                                    SET pfp = '{user.display_avatar.url}',
                                        name = '{user.name}',
                                        total = {max(row[9],row[5])}
                                    WHERE
                                        userid = {row[0]};""")
                await db.commit()
    await interaction.followup.send(content='done', ephemeral = True)
    


@tree.command(name = "totalupdate", description = "gets total number of days participated and updates", guild=discord.Object(id=1047644766311043162)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def total_update_db(interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)

    channel = await client.fetch_channel(1047644766877270038)
    a = {}
    for message in channel.history:
        dt = message.created_at
        date = (dt.year, dt.month, dt.day)
        a[message.author.id].add(date)

        async with db.execute('SELECT * FROM fartstreak') as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                #print(user)
                await db.execute(f"""UPDATE fartstreak 
                                    SET 
                                        total = {len(a[row[0]])}
                                    WHERE
                                        userid = {row[0]};""")
                await db.commit()
    await interaction.followup.send(content='done', ephemeral = True)

client.run(authTOKEN)

import discord
import aiosqlite
import config
from datetime import date
from datetime import timedelta
from discord.ext import commands
from discord import app_commands
from discord.utils import get

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix='/', intents=intents)

##### Events #####

@bot.event
async def on_ready():
        #db = await aiosqlite.connect("fartstreak.db")
        print(f'Logged on as {bot.user}!')
        await bot.tree.sync(guild=discord.Object(id=config.guild))

@bot.event
async def on_member_join(member):
    #print(f'{member} has joined the server')
    await member.edit(nick = 'fart club')

@bot.event
async def on_raw_message_edit(payload):
    #print("EDIT!!!")
    try:
        channel = await bot.fetch_channel(config.channel)
        #print(channel)
        message = await channel.fetch_message(payload.message_id)
        #print(message)
        await message.delete()
        #print("success")
    except:
        pass

@bot.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')
    print(message.channel.id)
    print(config.channel)
    if(message.channel.id == config.channel):
        #print(message.author),
        print(message.content)
        if(type(message.author) != discord.Member):
            return
        if(message.author.get_role(config.poo_clan) != None and message.content == "poo clan"):
            return
        print("before delete")
        if(message.content != "fart club" or message.stickers != [] or message.author.get_role(config.poo_clan) != None):
            print("in deelete")
            await message.delete()
        else:
            #add role for general chat. the 0 is a placeholder, replace with the ID of the correct role
            await message.author.add_roles(get(message.author.guild.roles, id=config.general))

            async with aiosqlite.connect(config.dbpath) as db:
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

##### Commands #####

@bot.tree.command(description = "adds pfp links and names to db", guild=discord.Object(id=config.guild)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def update(interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    async with aiosqlite.connect(config.dbpath) as db:
        async with db.execute('SELECT * FROM fartstreak') as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                user = await bot.fetch_user(row[0])
                #print(user)
                await db.execute(f"""UPDATE fartstreak 
                                    SET pfp = '{user.display_avatar.url}',
                                        name = '{user.name}',
                                        total = {max(row[9],row[5])}
                                    WHERE
                                        userid = {row[0]};""")
                await db.commit()
    await interaction.followup.send(content='done', ephemeral = True)
    


@bot.tree.command(description = "gets total number of days participated and updates", guild=discord.Object(id=config.guild)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def totalupdate(interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)

    channel = await bot.fetch_channel(config.channel)
    a = {}
    #print( "total messages pulled: " + str(len([message async for message in channel.history(limit = None)])))
    async for message in channel.history(limit = None):
        dt = message.created_at
        date = (dt.year, dt.month, dt.day)
        #print(message.author.id)
        #print(a.keys())
        try:
            a[message.author.id].add(date)
        except:
            a[message.author.id] = {date}
    print("printing final vlaue of A:")
    print(a)
    async with aiosqlite.connect(config.dbpath) as db:
        async with db.execute('SELECT * FROM fartstreak') as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                try:
                    print(row[0])
                    print(a.keys())
                    print(a[row[0]])
                    await db.execute(f"""UPDATE fartstreak 
                                    SET 
                                        total = {len(a[row[0]])}
                                    WHERE
                                        userid = {row[0]};""")
                    await db.commit()
                except:
                    print("broke but idk why")
    await interaction.followup.send(content='done', ephemeral = True)


@bot.tree.command(description = "for now it fixes the current streak", guild=discord.Object(id=config.guild)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def reset_all(interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)

    channel = await bot.fetch_channel(config.channel)
    a = {}
    #print( "total messages pulled: " + str(len([message async for message in channel.history(limit = None)])))
    async for message in channel.history(limit = None):
        dt = message.created_at
        date = dt.date()
        #print(message.author.id)
        #print(a.keys())
        try:
            a[message.author.id].add(date)
        except:
            a[message.author.id] = {date}
    print("printing final vlaue of A:")
    print(a)

    #now need to check for sequential dates

    async with aiosqlite.connect(config.dbpath) as db:
        async with db.execute('SELECT * FROM fartstreak') as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                try:
                    number_consecutive = 0
                    current_date = date.today()
                    print(a[row[0]])
        
                    while(current_date in a[row[0]]):
                        number_consecutive += 1
                        current_date -= timedelta(days = 1)
                        print(current_date)


                    #now calculate longest
                    current_date = date.fromisoformat('2023-01-01')
                    longest_consecutive = 0
                    current_consecutive = 0
                    while(current_date <= date.today()):
                        if(current_date in a[row[0]]):
                            current_consecutive += 1
                        else:
                            longest_consecutive = max(longest_consecutive, current_consecutive)
                            current_consecutive = 0
                        current_date += timedelta(days = 1)

                    longest_consecutive = max(longest_consecutive, current_consecutive)
                    print(row[0], longest_consecutive)
                    
                    print(row[0], number_consecutive)
                    #print(row[0])
                    #print(a.keys())
                    #print(a[row[0]])
                    
                    await db.execute(f"""UPDATE fartstreak 
                                    SET 
                                        currentstreak_length = {number_consecutive}
                                    WHERE
                                        userid = {row[0]};""")
                    await db.commit()
                except:
                    print("broke but idk why")
    await interaction.followup.send(content='done', ephemeral = True)

# crontab

@bot.tree.command(description = "remove fart club role from all", guild=discord.Object(id=config.guild))
async def rm_roles(interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)

    guild = bot.get_guild(config.guild)
    role = get(guild.roles, id=config.general) 
    for member in guild.members:
        await member.remove_roles(role)

    await interaction.followup.send(content='done', ephemeral = True)

@bot.tree.command(description = "sanitize the last n messages in the fart club channel", guild=discord.Object(id=config.guild))
@app_commands.default_permissions()
async def sanitize(interaction, n: int):
    await interaction.response.defer(ephemeral=True)

    def not_fart_club(m):
        return m.content != 'fart club'
    
    channel = bot.get_channel(config.channel)
    await channel.purge(limit=n, check=not_fart_club, reason='fart club')

    await interaction.followup.send(content='done')
    

@bot.tree.context_menu(guild=discord.Object(id=config.guild))
async def get_data(interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True)
    async with aiosqlite.connect(config.dbpath) as db:
        async with db.execute(f'SELECT total, currentstreak_length, longeststreak_length FROM fartstreak WHERE userid = {member.id};') as cursor:
            row = await cursor.fetchone()
            if(row == None):
                await interaction.followup.send(f'hmmm... {member.name} isn\'t in the database')
            else:
                async with db.execute(f'SELECT COUNT(*) FROM fartstreak WHERE longeststreak_length > {row[2]};') as cursor:
                    place = await cursor.fetchone()
                    await interaction.followup.send(f'{member.name} (#{place[0] + 1}):\n{row[0]} days participated\n{row[1]} day streak\n{row[2]} day longest streak')

bot.run(config.token)

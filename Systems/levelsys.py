# Imports
import asyncio

import discord
from discord.ext import commands
from pymongo import MongoClient
from ruamel.yaml import YAML
import vacefron
import os
from dotenv import load_dotenv

# Loads the .env file and gets the required information
load_dotenv()
MONGODB_URI = os.environ['MONGODB_URI']
COLLECTION = os.getenv("COLLECTION")
DB_NAME = os.getenv("DATABASE_NAME")

# Please enter your mongodb details in the .env file.
cluster = MongoClient(MONGODB_URI)
levelling = cluster[COLLECTION][DB_NAME]

# Reads the config file, no need for changing.
yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)
with open("Configs/spamconfig.yml", "r", encoding="utf-8") as file2:
    spamconfig = yaml.load(file2)

# Some config options which need to be stored here, again, no need for altering.
level_roles = config['level_roles']
level_roles_num = config['level_roles_num']

# Vac-API, no need for altering!
vac_api = vacefron.Client()


class levelsys(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, ctx):
        stats = levelling.find_one({"id": ctx.author.id})
        if not ctx.author.bot:
            if stats is None:
                newuser = {"id": ctx.author.id, "tag": ctx.author.mention, "xp": 0, "rank": 1, "background": " ", "circle": False, "xp_colour": "#ffffff", "name": f"{ctx.author}", "pfp": f"{ctx.author.avatar_url}"}
                print(f"User: {ctx.author.id} has been added to the database! ")
                levelling.insert_one(newuser)
            else:
                if config['Prefix'] in ctx.content:
                    stats = levelling.find_one({"id": ctx.author.id})
                    xp = stats["xp"]
                    levelling.update_one({"id": ctx.author.id}, {"$set": {"xp": xp}})
                else:
                    user = ctx.author
                    role = discord.utils.get(ctx.guild.roles, name=config['double_xp'])
                    if role in user.roles:
                        xp = stats["xp"] + config['xp_per_message'] * 2
                        levelling.update_one({"id": ctx.author.id}, {"$set": {"xp": xp}})
                    else:
                        xp = stats["xp"] + config['xp_per_message']
                        levelling.update_one({"id": ctx.author.id}, {"$set": {"xp": xp}})
                levelling.update_one({"id": ctx.author.id}, {'$set': {"pfp": f"{ctx.author.avatar_url}", "name": f"{ctx.author}"}})
                lvl = 0
                while True:
                    if xp < ((config['xp_per_level'] / 2 * (lvl ** 2)) + (config['xp_per_level'] / 2 * lvl)):
                        break
                    lvl += 1
                xp -= ((config['xp_per_level'] / 2 * ((lvl - 1) ** 2)) + (config['xp_per_level'] / 2 * (lvl - 1)))
                if xp == 0:
                    channel = self.client.get_channel(config['level_message_channel'])
                    levelling.update_one({"id": ctx.author.id}, {"$set": {"rank": + config['xp_per_message'] * 2}})
                    embed2 = discord.Embed(title=f":tada: **LEVEL UP!**",
                                           description=f"{ctx.author.mention} just reached Level: **{lvl}**",
                                           colour=config['embed_colour'])
                    xp = stats["xp"]
                    print(f"User: {ctx.author} | Leveled UP To: {lvl}")
                    embed2.add_field(name="Next Level:",
                                     value=f"``{int(config['xp_per_level'] * 2 * ((1 / 2) * lvl))}xp``")
                    embed2.set_thumbnail(url=ctx.author.avatar_url)
                    for i in range(len(level_roles)):
                        if lvl == level_roles_num[i]:
                            await ctx.author.add_roles(
                                discord.utils.get(ctx.author.guild.roles, name=level_roles[i]))
                            embed2.add_field(name="Role Unlocked:", value=f"`{level_roles[i]}`")
                            print(f"User: {ctx.author} | Unlocked Role: {level_roles[i]}")
                            embed2.set_thumbnail(url=ctx.author.avatar_url)
                            await channel.send(embed=embed2)
                        else:
                            await channel.send(embed=embed2)


def setup(client):
    client.add_cog(levelsys(client))

# End Of Level System

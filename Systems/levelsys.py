# Imports
import asyncio

import discord
from discord.ext import commands
from pymongo import MongoClient
from ruamel.yaml import YAML
import vacefron

# MONGODB SETTINGS *YOU MUST FILL THESE OUT OTHERWISE YOU'LL RUN INTO ISSUES!* - Need Help? Join The Discord Support Server, Found at top of repo.
cluster = MongoClient("mongodb link here - dont forget to insert password and database name!! and remove the <>")
levelling = cluster["databasename here"]["collectionsname here"]

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
                    levelling.update_one({"id": ctx.author.id}, {"$set": {"rank": + config['xp_per_message']}})
                    embed2 = discord.Embed(title=f":tada: **LEVEL UP!**",
                                           description=f"{ctx.author.mention} just reached Level: **{lvl}**",
                                           colour=config['embed_colour'])
                    xp = stats["xp"]
                    levelling.update_one({"id": ctx.author.id}, {"$set": {"rank": lvl, "xp": xp + config['xp_per_message'] * 2}})
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

    # Rank Command
    @commands.command(aliases=config['rank_alias'])
    async def rank(self, ctx, member=None):
        if member is None:
            user = f"<@!{ctx.author.id}>"
        else:
            user = member
        userget = user.replace('!', '')
        stats = levelling.find_one({"tag": userget})
        if stats is None:
            embed = discord.Embed(description=":x: No Data Found!",
                                  colour=config['error_embed_colour'])
            await ctx.channel.send(embed=embed)
        else:
            xp = stats["xp"]
            lvl = 0
            rank = 0
            while True:
                if xp < ((config['xp_per_level'] / 2 * (lvl ** 2)) + (config['xp_per_level'] / 2 * lvl)):
                    break
                lvl += 1
            xp -= ((config['xp_per_level'] / 2 * (lvl - 1) ** 2) + (config['xp_per_level'] / 2 * (lvl - 1)))
            rankings = levelling.find().sort("xp", -1)
            for x in rankings:
                rank += 1
                if stats["id"] == x["id"]:
                    break
            background = stats["background"]
            circle = stats["circle"]
            xpcolour = stats["xp_colour"]
            member = ctx.author
            gen_card = await vac_api.rank_card(
                username=str(stats['name']),
                avatar=stats['pfp'],
                level=int(lvl),
                rank=int(rank),
                current_xp=int(xp),
                next_level_xp=int(config['xp_per_level'] * 2 * ((1 / 2) * lvl)),
                previous_level_xp=0,
                xp_color=str(xpcolour),
                custom_background=str(background),
                is_boosting=bool(member.premium_since),
                circle_avatar=circle
            )
            embed = discord.Embed(colour=config['rank_embed_colour'])
            embed.set_image(url=gen_card.url)
            await ctx.send(embed=embed)

    # Leaderboard Command
    @commands.command(aliases=config['leaderboard_alias'])
    async def leaderboard(self, ctx):
        rankings = levelling.find().sort("xp", -1)
        i = 1
        con = config['leaderboard_amount']
        embed = discord.Embed(title=f":trophy: Leaderboard | Top {con}", colour=config['leaderboard_embed_colour'])
        for x in rankings:
            try:
                temp = ctx.guild.get_member(x["id"])
                tempxp = x["xp"]
                templvl = x["rank"]
                embed.add_field(name=f"#{i}: {temp.name}",
                                value=f"Level: `{templvl}`\nTotal XP: `{tempxp}`\n", inline=True)
                embed.set_thumbnail(url=config['leaderboard_image'])
                i += 1
            except:
                pass
            if i == config['leaderboard_amount'] + 1:
                break
        await ctx.channel.send(embed=embed)

    # Reset Command
    @commands.command()
    @commands.has_role(config["admin_role"])
    async def reset(self, ctx, user=None):
        if user:
            userget = user.replace('!', '')
            levelling.update_one({"tag": userget}, {"$set": {"rank": 1, "xp": 0}})
            embed = discord.Embed(title=f":white_check_mark: RESET USER", description=f"Reset User: {user}",
                                  colour=config['success_embed_colour'])
            print(f"{userget} was reset!")
            await ctx.send(embed=embed)
        else:
            prefix = config['Prefix']
            embed2 = discord.Embed(title=f":x: RESET USER FAILED",
                                   description=f"Couldn't Reset! The User: `{user}` doesn't exist or you didn't mention a user!",
                                   colour=config['error_embed_colour'])
            embed2.add_field(name="Example:", value=f"``{prefix}reset`` {ctx.message.author.mention}")
            print("Resetting Failed. A user was either not declared or doesn't exist!")
            await ctx.send(embed=embed2)

    # Help Command
    @commands.command(aliase="h")
    async def help(self, ctx):
        if config['help_command'] is True:
            prefix = config['Prefix']
            top = config['leaderboard_amount']
            embed = discord.Embed(title=":book: Help Journal | Home", description=f"Welcome to the Help Journal. My Prefix here is: `{prefix}`\n\nThe Help Journal will give you information on all available commands and any other information.\n\n***REACT BELOW TO SWITCH PAGES*** ")
            embed2 = discord.Embed(title=":book: Help Journal | Rank", description=f"Command:\n`{prefix}rank or {prefix}rank <@user>`\n\nAbout:\nThe `Rank` command will show the user their current level, server ranking and how much xp you have. Your rank card can be customisable with other commands.\n\n***REACT BELOW TO SWITCH PAGES***")
            embed3 = discord.Embed(title=":book: Help Journal | Leaderboard", description=f"Command:\n`{prefix}leaderboard`\n\nAbout:\nThe `Leaderboard` command displays the Top {top} users in that server, sorted by XP.\n\n***REACT BELOW TO SWITCH PAGES***")
            embed4 = discord.Embed(title=":book: Help Journal | Background", description=f"Command:\n`{prefix}background <link>`\n\nAbout:\nThe `Background` command will allow you to change your rank cards background to the image of your choosing.\n\n*Note: Some links may not work! If this is the case, send the image to discord, then copy the media link!*\n\n***REACT BELOW TO SWITCH PAGES***")
            embed5 = discord.Embed(title=":book: Help Journal | Circle Picture", description=f"Command:\n`{prefix}circlepic <True|False>`\n\nAbout:\nThe `Circlepic` command will allow you to change your rank cards profile picture to be circular if set to `true`.\n\n***REACT BELOW TO SWITCH PAGES***")
            embed6 = discord.Embed(title=":book: Help Journal | XP Colour", description=f"Command:\n`{prefix}xpcolour <hex code>`\n\nAbout:\nThe `XPColour` command will allow you to change your rank cards xp bar colour to any hex code of your choosing.\n\n***REACT BELOW TO SWITCH PAGES***")
            embed7 = discord.Embed(title=":book: Help Journal | Reset | Admin", description=f"Command:\n`{prefix}reset <@user>`\n\nAbout:\nThe `Reset` command will allow you to reset any user back to the bottom level. *Admin Only*\n\n***REACT BELOW TO SWITCH PAGES***", colour=0xc54245)
            embed8 = discord.Embed(title=":book: Help Journal | Update | Admin", description=f"Command:\n`{prefix}update <@user>`\n\nAbout:\nThe `Update` command will try and fix users database fields when going to a newer version. *Admin Only*\n\n*Note: This may not always work due to certain ways the bot has been built. If so, please do this manually.*\n\n***REACT BELOW TO SWITCH PAGES***", colour=0xc54245)
            embed9 = discord.Embed(title=":book: Help Journal | Shutdown | Admin", description=f"Command:\n`{prefix}shutdown`\n\nAbout:\nThe `Shutdown` command will cause the bot to turn off and go offline until turned on again. *Admin Only*\n\n***REACT BELOW TO SWITCH PAGES***", colour=0xc54245)
            contents = [embed, embed2, embed3, embed4, embed5, embed6, embed7, embed8, embed9]
            pages = 9
            cur_page = 1
            message = await ctx.send(embed=contents[cur_page - 1])

            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

            while True:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=30, check=check)

                    if str(reaction.emoji) == "▶️" and cur_page != pages:
                        cur_page += 1
                        await message.edit(embed=contents[cur_page - 1])
                        await message.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "◀️" and cur_page > 1:
                        cur_page -= 1
                        await message.edit(embed=contents[cur_page - 1])
                        await message.remove_reaction(reaction, user)

                    else:
                        await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    await message.delete()
                    break

    @commands.command()
    @commands.has_role(config["admin_role"])
    async def shutdown(self, ctx):
        await ctx.message.delete()
        exit("Shutting Down..")

    @commands.command()
    async def background(self, ctx, link=None):
        await ctx.message.delete()
        if link:
            levelling.update_one({"id": ctx.author.id}, {"$set": {"background": f"{link}"}})
            embed = discord.Embed(title=":white_check_mark: **BACKGROUND CHANGED!**",
                                  description="Your profile background has been set successfully! If your background does not update, please try a new image.")
            embed.set_thumbnail(url=link)
            await ctx.channel.send(embed=embed)
        elif link is None:
            embed3 = discord.Embed(title=":x: **SOMETHING WENT WRONG!**",
                                   description="Please make sure you entered a link.")
            await ctx.channel.send(embed=embed3)

    @commands.command()
    async def circlepic(self, ctx, value=None):
        await ctx.message.delete()
        if value == "True":
            levelling.update_one({"id": ctx.author.id}, {"$set": {"circle": True}})
            embed1 = discord.Embed(title=":white_check_mark: **PROFILE CHANGED!**",
                                   description="Circle Profile Picture set to: `True`. Set to `False` to return to default.")
            await ctx.channel.send(embed=embed1)
        elif value == "False":
            levelling.update_one({"id": ctx.author.id}, {"$set": {"circle": False}})
            embed2 = discord.Embed(title=":white_check_mark: **PROFILE CHANGED!**",
                                   description="Circle Profile Picture set to: `False`. Set to `True` to change it to a circle.")
            await ctx.channel.send(embed=embed2)
        elif value is None:
            embed3 = discord.Embed(title=":x: **SOMETHING WENT WRONG!**",
                                   description="Please make sure you either typed: `True` or `False`.")
            await ctx.channel.send(embed=embed3)

    @commands.command()
    async def xpcolour(self, ctx, colour):
        await ctx.message.delete()
        if colour is None:
            embed = discord.Embed(title=":x: **SOMETHING WENT WRONG!**",
                                  description="Please make sure you typed a hex code in!.")
            await ctx.channel.send(embed=embed)
            return
        levelling.update_one({"id": ctx.author.id}, {"$set": {"xp_colour": f"{colour}"}})
        prefix = config['Prefix']
        embed = discord.Embed(title=":white_check_mark: **XP COLOUR CHANGED!**",
                              description=f"Your xp colour has been changed. If you type `{prefix}rank` and nothing appears, try a new hex code. \n**Example**:\n*#0000FF* = *Blue*")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/812895798496591882/825363205853151252/ML_1.png")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role(config["admin_role"])
    async def update(self, ctx, user=None):
        if user:
            userget = user.replace('!', '')
            levelling.update_one({"tag": userget}, {"$set": {"background": "", "circle": False, "xp_colour": "#ffffff"}})
            embed = discord.Embed(title=f":white_check_mark: UPDATED USER", description=f"Updated User: {user}",
                                  colour=config['success_embed_colour'])
            await ctx.send(embed=embed)
        else:
            prefix = config['Prefix']
            embed2 = discord.Embed(title=f":x: UPDATE USER FAILED",
                                   description=f"Couldn't Update User: ``{user}`` doesn't exist or you didn't mention a user!",
                                   colour=config['error_embed_colour'])
            embed2.add_field(name="Example:", value=f"``{prefix}update`` {ctx.message.author.mention}")
            await ctx.send(embed=embed2)


def setup(client):
    client.add_cog(levelsys(client))

# End Of Level System

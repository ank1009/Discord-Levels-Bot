import asyncio

import discord
from discord.ext import commands
from ruamel.yaml import YAML

# Reads the config file, no need for changing.
yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)
with open("Configs/holidayconfig.yml", "r", encoding="utf-8") as file2:
    holidayconfig = yaml.load(file2)


# Spam system class
class help(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Help Command
    @commands.command(alias="h")
    @commands.guild_only()
    async def help(self, ctx, helptype=None):
        if config['help_command'] is True:
            prefix = config['Prefix']
            top = config['leaderboard_amount']
            if helptype is None:
                embed = discord.Embed(title=f"{self.client.user.name} Command List")
                embed.add_field(name=f":camera: Profile",
                                value=f'`{prefix}help profile`\n[Hover for info](https://www. "Customise your rank cards background, xp colour and your profile pictures shape!")')
                embed.add_field(name=f":smile: Fun", value=f"`{prefix}help fun`\n[Hover for info](https://www. 'Check yours or another persons rank card, or check out the leaderboard')")
                embed.set_footer(text="If you're on mobile, the hover button will not work")
                if ctx.author.id == holidayconfig['bot_owner_id']:
                    embed.add_field(name=f":gear: Config", value=f"`{prefix}help config`\n[Hover for info](https://www. 'Customise the bot to your liking for your server!')")
                    embed.add_field(name=f":calendar: Events", value=f"`{prefix}help events`\n[Hover for info](https://www. 'Only you can see this - Start/Stop events bot wide')")
                    embed.add_field(name=f":octagonal_sign: Admin", value=f"`{prefix}help admin`\n[Hover for info](https://www. 'Perform Admin commands on users, such as resetting')")
                    await ctx.send(embed=embed)
                elif ctx.message.author.guild_permissions.administrator:
                    embed = discord.Embed(title=f"{self.client.user.name} Command List")
                    embed.add_field(name=f":gear: Config", value=f"`{prefix}help config`")
                    embed.add_field(name=f":octagonal_sign: Admin", value=f"`{prefix}help admin`")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(embed=embed)
            if helptype == "profile":
                embed = discord.Embed(title=f":camera: Profile Commands", description="```background, circlepic, xpcolour```")
                embed.add_field(name="Examples", value=f"`{prefix}background <link>`\nworks best with [Imgur](https://www.imgur.com 'Click to go to Imgur')\n\n`{prefix}circlepic <True|False>`\nif you get an error, check capitalisation\n\n`{prefix}xpcolour <hex>`\nclick [here](https://www.color-hex.com/. 'Click to go to color hex') to find hex codes")
                await ctx.send(embed=embed)
            elif helptype == "fun":
                embed = discord.Embed(title=f":smile: Fun Commands",
                                      description="```rank, leaderboard```")
                embed.add_field(name="Examples",
                                value=f"`{prefix}rank `\nyou can also mention users\n\n`{prefix}leaderboard`\nshows top {top} users in guild")
                await ctx.send(embed=embed)
            elif helptype == "events":
                if ctx.author.id == holidayconfig['bot_owner_id']:
                    embed = discord.Embed(title=f":calendar: Event Commands",
                                          description="```event```")
                    embed.add_field(name="Examples",
                                    value=f"`{prefix}event <holiday> <start|stop> `\nbot wide event that only you can set")
                    embed.add_field(name="Holidays", value=":beach: | `Summer`\n:egg: | `Easter`\n:jack_o_lantern: | `Halloween`\n:christmas_tree: | `Christmas`")
                    await ctx.send(embed=embed)
            elif helptype == "admin":
                if ctx.message.author.guild_permissions.administrator:
                    embed = discord.Embed(title=f":octagonal_sign: Admin Commands",
                                          description="```reset, addxp, removexp```")
                    embed.add_field(name="Examples",
                                    value=f"`{prefix}reset <user>`\nfully resets a user\n\n`{prefix}addxp <amount> <user>`\nadds xp to a user\n\n`{prefix}removexp <amount> <user>`\nremoves xp from a user")
                    await ctx.send(embed=embed)
            elif helptype == "config":
                if ctx.message.author.guild_permissions.administrator:
                    embed = discord.Embed(title=f":gear: Config Commands",
                                          description="```antispam, doublexp, ignoredrole, levelchannel, mutedrole, mutemessages, mutetime, role, warningmessages, xppermessage```")
                    embed.add_field(name="Examples",
                                    value=f"`{prefix}antispam <True|False>`\nenables or disabled antispam for your server\n\n`{prefix}doublexp <role>`\nuse the role name rather than the id\n\n`{prefix}ignoredrole <role>`\nthe role that antispam ignores\n\n`{prefix}levelchannel <channelName>`\nthe channel where level up messages get sent to\n\n`{prefix}mutedrole <role>`\nthe role a muted person receives\n\n`{prefix}mutemessages <number>`\nthe amount of messages it takes to be muted in a certain time period\n\n`{prefix}mutetime <seconds>`\nhow long a user is muted for\n\n`{prefix}role <add|remove> <level> <rolename>`\nthe role a user gets when they reach a certain level\n\n`{prefix}warningmessages <number>`\nhow many messages until a user gets warned for spam\n\n`{prefix}xppermessage <int>`\nhow much xp you earn per message")
                    await ctx.send(embed=embed)







# Sets-up the cog for help
def setup(client):
    client.add_cog(help(client))
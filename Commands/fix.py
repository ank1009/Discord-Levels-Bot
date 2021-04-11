import discord
from discord.ext import commands
from ruamel.yaml import YAML
from Systems.levelsys import levelling

# Reads the config file, no need for changing.
yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


# Spam system class
class fix(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_role(config["admin_role"])
    async def fix(self, ctx, user=None):
        if user:
            userget = user.replace('!', '')
            levelling.update_one({"tag": userget}, {"$set": {"background": "", "circle": False, "xp_colour": "#ffffff"}})
            embed = discord.Embed(title=f":white_check_mark: UPDATED USER", description=f"Updated User: {user}",
                                  colour=config['success_embed_colour'])
            await ctx.send(embed=embed)
        elif user is None:
            prefix = config['Prefix']
            embed2 = discord.Embed(title=f":x: FIX USER FAILED",
                                   description=f"Please make sure you @ someone when running this command!",
                                   colour=config['error_embed_colour'])
            embed2.add_field(name="Example:", value=f"``{prefix}fix`` {ctx.message.author.mention}")
            await ctx.send(embed=embed2)


# Sets-up the cog for help
def setup(client):
    client.add_cog(fix(client))
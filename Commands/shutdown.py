from discord.ext import commands
from ruamel.yaml import YAML

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
    async def shutdown(self, ctx):
        await ctx.message.delete()
        exit("Shutting Down..")


# Sets-up the cog for help
def setup(client):
    client.add_cog(fix(client))
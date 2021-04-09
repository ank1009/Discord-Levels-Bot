# Imports
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MissingRequiredArgument, CommandInvokeError, MissingRole
import discord
from ruamel.yaml import YAML
import logging

# Opens the config and reads it, no need for changes unless you'd like to change the library (no need to do so unless having issues with ruamel)
yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


# Command Prefix + Removes the default discord.py help command
client = commands.Bot(command_prefix=config['Prefix'], intents=discord.Intents.all(), case_insensitive=True)
client.remove_command('help')

sends discord logging files which could potentially be useful for catching errors.
FORMAT = '[%(asctime)s]:[%(levelname)s]: %(message)s'
logging.basicConfig(filename='Logs/logs.txt', level=logging.DEBUG, format=FORMAT)
logging.debug('Started Logging')
logging.info('Connecting to Discord.')


@client.event  # On Bot Startup, Will send some details about the bot and sets it's activity and status. Feel free to remove the print messages, but keep everything else.
async def on_ready():
    config_status = config['bot_status_text']
    config_activity = config['bot_activity']
    activity = discord.Game(name=config['bot_status_text'])
    logging.info('Getting Bot Activity from Config')
    print("You're currently running a beta version! -- If you encounter any bugs, let me know.")
    print('------')
    print('Logged In:')
    print(f"Bot Username: {client.user.name}\nBotID: {client.user.id}")
    print('------')
    print(f"Set Status To: {config_status}\nSet Activity To: {config_activity}")
    print("------")
    print("Started System: Levels")
    await client.change_presence(status=config_activity, activity=activity)
    logging.info('Logged In And Set Activity')


# If enabled in config, will send a welcome message + adds a role if a new user joins the guild (if roles are enabled).
@client.event
async def on_member_join(member):
    if config['join_leave_message'] is True:
        logging.info('A user has joined a guild')
        channel = client.get_channel(config['join_leave_channel'])
        embed = discord.Embed(title=f"**:man_raising_hand: WELCOME**", description=f"Welcome **{member.mention}** to **{member.guild.name}**!", colour=discord.Colour.green())
        embed.set_author(name=member.name, icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.guild.icon_url)
        await channel.send(embed=embed)
    if config['add_role'] is True:
        rank = discord.utils.get(member.guild.roles, name=config['on_join_role'])
        await member.add_roles(rank)
        print(f"User: {member} was given the {rank} role.")
        logging.info('A role was sent to a user')


# If enabled in config, will send a leave message if a user leaves the guild
@client.event
async def on_member_remove(member):
    if config['join_leave_message'] is True:
        logging.info('A user left a guild')
        channel = client.get_channel(config['join_leave_channel'])
        embed = discord.Embed(title=f"**:man_raising_hand: GOODBYE**", description=f"**{member.mention}** has left **{member.guild.name}**!", colour=discord.Colour.red())
        embed.set_author(name=member.name, icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.guild.icon_url)
        await channel.send(embed=embed)


@client.event  # Stops Certain errors from being thrown in the console (Don't remove as it'll cause command error messages to not send! - Only remove if adding features and needed for testing (Don't forget to re-add)!)
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        logging.error('Command Not Found')
        return
    if isinstance(error, MissingRequiredArgument):
        logging.error('Argument Error - Missing Arguments')
        return
    if isinstance(error, CommandInvokeError):
        logging.error('Command Invoke Error')
        return
    if isinstance(error, MissingRole):
        logging.error('A user has missing roles!')
        return
    if isinstance(error, AttributeError):
        logging.error('Attribute Error')
        return
    raise error

if config['antispam_system'] is True:
    logging.info('Checking if anti-spam is enabled')
    client.load_extension("Systems.spamsys")
    logging.info('Loaded AntiSpam')
client.load_extension("Systems.levelsys")
logging.info('Loaded Levelsys')


# Uses the bot token to login, so don't remove this.
client.run(config['Bot_Token'])

# End Of Main

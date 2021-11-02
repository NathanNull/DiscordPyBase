# Discord Bot Base
# Author: Nathan Strong
# Date: Nov 1, 2021
# Description: This is not meant to be run in most cases. Instead, it's meant to be imported into other projects (assuming you can even do that) and used to build actual bots that do things that are interesting.

import discord
import sys
import time

# Get the command arguments out of a string, grouping arguments in quotation marks
def get_args(arg_string):
    # Initialize some variables
    possible_arg_list = arg_string.split()
    arg_list = []
    current_arg = ""

    # Go through the list, collecting all arguments in quotation marks into single arguments
    # For instance, hello "world hello" world should become ["hello", "world hello", "world"]
    for possible_arg in possible_arg_list:
        if current_arg != "":
            current_arg = current_arg + " " + possible_arg
            if possible_arg.endswith("\""):
                arg_list.append(current_arg[:-1])
                current_arg = ""
        elif possible_arg.startswith("\""):
            current_arg = possible_arg[1:]
        else:
            arg_list.append(possible_arg)
    
    return arg_list

# Returns timestamp (hour:minute:second)
def timestamp():
    t = time.localtime()
    # time.localtime is off by 5 hours for some reason... guess I need to adjust that...
    return f"{(t.tm_hour+5)%24:02d}:{t.tm_min:02d}:{t.tm_sec:02d}"

class CommandData:
    def __init__(self, fn, desc, syntax, private):
        self.fn = fn
        self.desc = desc
        self.private = private
        self.syntax = syntax

class PermsClass:
    def __init__(self):
        self.none = "anyone"
        self.admin = "a mod"
        self.owner = "the owner of this bot"

    def verify_perms(self, user, perms, channel, owner):
        if perms == self.none or user.id == owner:
            return True
        elif user.permissions_in(channel).administrator:
            if perms == self.admin:
                return True
        return False
Perms = PermsClass()

# Create a decorator that knows which functions are commands in a given object
all_commands = {}
def command(name, description, syntax=None, private=False, perms_needed=Perms.none):
    if syntax == None:
        syntax = "{}"+name
    def command_decorator(func):
        async def wrapper(bot, args, ctx):
            if Perms.verify_perms(ctx.author, perms_needed, ctx.channel, bot.owner):
                await func(bot, args, ctx)
            else:
                await ctx.channel.send(f"Insufficient permissions. You need to be {perms_needed} to run this command.")
        
        if name in all_commands.keys():
            raise Exception(f"The command name '{name}' was used more than once")
        all_commands[name] = CommandData(wrapper, description, syntax, private)

        return wrapper

    return command_decorator

class BaseBot(discord.Client):
    def __init__(self, prefix="!", owner=None, **base_args):
        # Run base class __init__ function using any arguments passed in
        super().__init__(**base_args)

        # Set prefix, commands, owner, last seen message
        self.prefix = prefix
        self.commands = all_commands
        self.owner = owner
        self.last_msg = None
    
    async def on_ready(self):
        # State that the bot has logged on
        print(f"{self.user} connected to discord at {timestamp()}")

        # For each server we have a channel for, get the idks in that channel and store them
        for guild in self.guilds:
            await guild.system_channel.send("I'm online!")
    
    async def on_message(self, message):
        # Log the message in the console
        if self.last_msg == None:
            channel_display = f"{message.guild} (#{message.channel})"
        elif self.last_msg.channel == message.channel:
            channel_display = "same channel"
        elif self.last_msg.guild == message.guild:
            channel_display = f"same guild (#{message.channel})"
        else:
            channel_display = f"{message.guild} (#{message.channel})"
        
        self.last_msg = message

        print(f"{message.author} @{timestamp()} in {channel_display}: {message.content}")
        
        # If the message was sent by the bot itself or if it doesn't have the required prefix, return (since the message is not a command)
        if message.author == self.user:
            return

        if not message.content.startswith(self.prefix):
            return
        
        # Get the necessary command details, then execute the requested command if it is found.
        command = get_args(message.content[len(self.prefix):])
        command_name = command[0]
        command_args = command[1:]

        if command_name in self.commands.keys():
            await self.commands[command_name].fn(self, command_args, message)
        else:
            await message.channel.send(f"Unknown command '{command_name}'. Try '{self.prefix}help' for a list of available commands.")
    
    @command("help", "Sends this message")
    async def list_commands(self, args, ctx):
        msg = ""
        for name, cmd in all_commands.items():
            if not cmd.private:
                msg = msg + f"""{" ".join(name.capitalize().split("_"))}:
  -Description: {cmd.desc}.
  -Syntax: {cmd.syntax.format(self.prefix)}
                
"""
        await ctx.channel.send(msg)
    
    @command("stop", "Takes the bot offline. Only usable by the creator of this bot", private=True, perms_needed=Perms.owner)
    async def end(self, args, ctx):
        # Go offline, end program
        for server in self.guilds:
            await server.system_channel.send("IDKBot is going offline. This will likely be temporary.")
        await ctx.channel.send("Going offline.")
        await self.change_presence(status=discord.Status.offline)
        sys.exit(f"Stop command run by {ctx.author}, bot offline. This is NOT an error.")

# Main function
def main():
    print("Why are you running this? It's a module, not a program.")

if __name__ == "__main__":
    main()
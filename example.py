# DiscordBase library example
# Author: Nathan Strong
# Date: Nov 1, 2021
# Description: This serves as an example of how to use the DiscordBot library.

import os
import discord
import module as discord_base # This would be replaced with whatever replit wants for importing from another repl.

class ExampleBot(discord_base.BaseBot):
    # The [library_name].command decorator is the way in which you declare commands.    You can pass it the following arguments:

    # name (required): The command's name, what you would use to call it

    # description (required): How the command is described when the help command is run

    # syntax: how your command should be written. Should be something like "{}[name] [args]", where name is the command's name and args are the arguments it takes. The {} is required for displaying the prefix at the start.
    # Defaults to {} plus whatever the command's name is.

    # private: True if the command should be hidden in the help menu (ie. if it's an admin-only command). 
    # Defaults to False

    # perms_needed: Should be a Perms variable (like Perms.admin), depending on who should be able to run the command. 
    # Defaults to Perms.none
    @discord_base.command(name="ping", description="Sends \"Pong!\"")
    async def ping(self, args, ctx):
        await ctx.channel.send("Pong!")
    
    # If you're going to use one of the methods listed below, you need to include the line super().[method name](method args) at the start to ensure you don't break anything. You may need to await it.
    # The methods you need this for are: __init__, on_ready, and on_message
    # Then you can do whatever you want with the rest of the method.
    async def on_message(self, message):
        await super().on_message(message)
        
        if message.content.lower().strip("!.?") == "hi":
            await message.channel.send("Hello!")

# Main function
def main():
    # Get environment vars
    TOKEN = os.environ['token']
    ADMIN = int(os.environ['owner'])

    # Set intents
    intents = discord.Intents.default()
    intents.members = True

    # Create and run client
    client = ExampleBot(intents = intents, owner = ADMIN, prefix = "example!")
    client.run(TOKEN)

if __name__ == "__main__":
    main()
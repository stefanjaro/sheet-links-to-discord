# import libraries and objects
import os
import time
import datetime
from zoneinfo import ZoneInfo
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from google_sheet_operations import (
    load_google_sheet, convert_to_pandas_df, 
    get_link_to_post, update_posted_indicator 
)
# load environment variables

# load from dotenv file -- comment out in production
load_dotenv()

# get all env vars
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ALLOWED_CHANNEL_ID = int(os.getenv("ALLOWED_CHANNEL_ID"))
GUILD_NAME = os.getenv("GUILD_NAME")

# define hardcoded variables
PAUSE_TIMER = 3600 # seconds

# create a client instance
client = discord.Client()

def get_sheet_and_links():
    """
    Open our Google Sheet, pop it into a dataframe
    and get the link we need to post
    """
    # load a google sheet
    gsheet = load_google_sheet("GOOGLE_SHEETS_API_KEY", "Resources to Share with SLDE Discord", "Original")

    # turn it into a pandas dataframe and set the right datatypes
    links_df = convert_to_pandas_df(gsheet)

    # get the link that needs to be posted
    rel_link = get_link_to_post(links_df)

    return gsheet, links_df, rel_link

@client.event
async def on_ready():
    """
    The main function that loops after a specified period of time
    and shares a resource or link as an embedded message
    """
    # ensure bot has successfully connected
    guild = discord.utils.get(client.guilds, name=GUILD_NAME)
    print(f"{client.user} is now connected to {guild.name}")

    while True:
        # get current datetime and time in LKA
        current_datetime = datetime.datetime.now(tz=ZoneInfo('Asia/Colombo'))

        # get sheet and links
        print(f"Accessing the Google sheet at {current_datetime}")
        gsheet, links_df, rel_link = get_sheet_and_links()

        # post a message only if there is a link to share
        if rel_link.empty == False:
            print(f"Link to share detected at {current_datetime}")
            # create an embed object and add the link as a separate field
            # and set an image_url as well
            embed = discord.Embed(
                title=rel_link["title"].item(),
                url=rel_link["url"].item(),
                description=rel_link["message"].item(),
                color=discord.Color.green()
            )
            embed.add_field(name="Link", value=rel_link["url"].item())
            embed.set_image(url=rel_link["image_url"].item())

            # create a channel object
            channel = client.get_channel(ALLOWED_CHANNEL_ID)

            # send the embed/message
            await channel.send(embed=embed)

            # update posted indicator so we don't repost it accidentally
            print(f"Updating posted_indicator of link id: {rel_link['id'].item()}")
            update_posted_indicator(gsheet, links_df, rel_link)

        else:
            print(f"No link to share as of {current_datetime}")
            pass

        # pause for the duration specified by the pause timer
        print(f"Pausing the program for {PAUSE_TIMER} seconds")
        time.sleep(PAUSE_TIMER)

client.run(DISCORD_TOKEN)
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import aiohttp
from PIL import Image, ImageSequence
import io

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

'''
todo:
tilde fix
'''

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.emojis = True

bot = commands.Bot(command_prefix="/", intents=intents)
binded_channel = None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    synced = await bot.tree.sync()
    print(f"Slash commands synced: {synced}")

@bot.tree.command(name="bind", description="Bind the bot in the channel you're running this command")
async def bind(interaction: discord.Interaction):
    global binded_channel
    if binded_channel:
        await interaction.response.send_message("Bot is already bounded! To rebind, run /rebind [channel id]", ephemeral=True)
    else:
        binded_channel = interaction.channel.id
        await interaction.response.send_message(f"Bot successfully bound to {interaction.channel.mention}")

@bot.tree.command(name="rebind", description="Rebind the bot to a different channel")
@app_commands.describe(channel_id="ID of the new channel to bind the bot to")
async def rebind(interaction: discord.Interaction, channel_id: int):
    global binded_channel
    channel = bot.get_channel(channel_id)
    if channel:
        binded_channel = channel_id
        await interaction.response.send_message(f"Bot successfully rebound to {channel.mention}")
    else:
        await interaction.response.send_message("Invalid channel ID", ephemeral=True)

@bot.event
async def on_message(message):
    if message.content.startswith("//") or message.author.bot:
        return

    if message.channel.id != binded_channel:
        return
    
    if message.content.lower().startswith("remove ") and len(message.content.split()) > 1:
        emoji_name = message.content[7:].strip()
        
        emoji = discord.utils.get(message.guild.emojis, name=emoji_name)
        if emoji:
            try:
                await emoji.delete()
                await message.channel.send(f"Emoji `:{emoji_name}:` has been removed.")
            except discord.Forbidden:
                await message.channel.send("I don't have permission to delete emojis.")
            except discord.HTTPException as e:
                await message.channel.send(f"An error occurred while removing the emoji: {e}")
        else:
            await message.channel.send(f"Emoji name wasn't found. Try entering only the emoji name, not the actual emoji.")
        return  

    if message.content.lower().startswith("info ") and len(message.content.split()) > 1:
        emoji_name = message.content[5:].strip()
        
        emoji = discord.utils.get(message.guild.emojis, name=emoji_name)
        if emoji:
            creation_date = emoji.created_at.strftime("%m/%d/%y")
            author = emoji.author if hasattr(emoji, 'author') else "Unknown (can be emojibot)"
            emoji_id = emoji.id

            await message.channel.send(
                f"Emoji Info for `:{emoji_name}:` \n"
                f"ID: {emoji_id}\n"
                f"Created on: {creation_date}\n"
                f"Author: {author}"
            )
        else: #
            await message.channel.send(f"Emoji name wasn't found. Try entering only the emoji name, not the actual emoji.")

        return  

    content_parts = message.content.split()
    if len(content_parts) < 1:
        await message.channel.send("Please provide an emoji name and an image (attachment or URL).")
        return

    emoji_name = content_parts[0].strip()
    if not all(c.isalnum() or c == "_" for c in emoji_name):
        await message.channel.send("Invalid characters in emoji name. Please use letters/numbers/underscores.")
        return

    if discord.utils.get(message.guild.emojis, name=emoji_name):
        await message.channel.send("Emoji name already exists!")
        return

    image_data = None

    if message.attachments:
        attachment = message.attachments[0]
        try:
            image_data = await attachment.read()
        except Exception as e:
            await message.channel.send(f"An error occurred while reading the attached image: {e}")
            return

    elif len(content_parts) > 1:
        image_url = content_parts[1]
        if image_url.startswith("http") and (
            image_url.endswith(".png") or image_url.endswith(".jpg") or image_url.endswith(".jpeg") or image_url.endswith(".gif")
        ):
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(image_url) as response:
                        if response.status == 200:
                            image_data = await response.read()
                        else:
                            await message.channel.send("Failed to fetch image from the URL. Please provide a valid image URL.")
                            return
                except Exception as e:
                    await message.channel.send(f"An error occurred while trying to fetch the image: {e}")
                    return

    if not image_data:
        await message.channel.send("No valid image found. Please provide an image attachment or a direct image URL.")
        return

    if len(image_data) > 256 * 1024:
        try:
            image_data = await resize_image(image_data)
        except Exception as e:
            await message.channel.send(f"An error occurred while resizing the image: {e}")
            return

    try:
        emoji = await message.guild.create_custom_emoji(name=emoji_name, image=image_data)
        await message.channel.send(f"Emoji {emoji} (`:{emoji.name}:`) created successfully!")
        await message.add_reaction(emoji)
    except discord.Forbidden:
        await message.channel.send("I don't have permission to manage emojis on this server.")
    except discord.HTTPException as e:
        await message.channel.send(f"An error occurred while creating the emoji: {e}")

    await bot.process_commands(message)

@bot.tree.command(name="help", description="halp!!1")
async def help_command(interaction: discord.Interaction):
    commands_list = [
        "`/bind` - Bind the bot in the channel you're running this command",
        "`/rebind [channel_id]` - Rebind the bot to a different channel.",
        "`remove [emoji name, plaintext]` - Remove a custom emoji.",
        "`info [emoji name, plaintext]` - Get info about a custom emoji.",
    ]
    await interaction.response.send_message("\n".join(commands_list))
#
async def resize_image(image_data):
    max_size_bytes = 256 * 1024
    with Image.open(io.BytesIO(image_data)) as img:
        if img.format.lower() == "gif":
            frames = []
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert("RGBA")
                frame.thumbnail((128, 128))
                frames.append(frame)

            output = io.BytesIO()
            frames[0].save(
                output,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                optimize=True,
                loop=0,
            )

            while output.tell() > max_size_bytes:
                output = io.BytesIO()
                for i in range(len(frames)):
                    frames[i] = frames[i].resize(
                        (int(frames[i].width * 0.9), int(frames[i].height * 0.9)), Image.Resampling.LANCZOS
                    )
                frames[0].save(
                    output,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    optimize=True,
                    loop=0,
                )
            return output.getvalue()

        else:
            img = img.convert("RGBA")
            img.thumbnail((128, 128))
            output = io.BytesIO()
            img.save(output, format="PNG", optimize=True)

            while output.tell() > max_size_bytes:
                output = io.BytesIO()
                img = img.resize(
                    (int(img.width * 0.9), int(img.height * 0.9)), Image.Resampling.LANCZOS
                )
                img.save(output, format="PNG", optimize=True)
            return output.getvalue()

bot.run(TOKEN)

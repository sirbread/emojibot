import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import aiohttp
from PIL import Image, ImageSequence
import io
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

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
@app_commands.checks.has_permissions(administrator=True)
async def bind(interaction: discord.Interaction):
    global binded_channel
    if binded_channel:
        await interaction.response.send_message("Bot is already bounded! To rebind, run /rebind [channel id]", ephemeral=True)
    else:
        binded_channel = interaction.channel.id
        await interaction.response.send_message(f"Bot successfully bound to {interaction.channel.mention}")

@bot.tree.command(name="rebind", description="Rebind the bot to a different channel")
@app_commands.describe(channel_id="ID of the new channel to bind the bot to")
@app_commands.checks.has_permissions(administrator=True)
async def rebind(interaction: discord.Interaction, channel_id: str):
    global binded_channel
    try:
        channel_id_int = int(channel_id)  
        channel = bot.get_channel(channel_id_int)
        if channel:
            binded_channel = channel_id_int
            await interaction.response.send_message(f"Bot successfully rebound to {channel.mention}")
        else:
            await interaction.response.send_message("Invalid channel ID. Make sure the channel exists and the bot can access it.", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("Invalid channel ID format. You really fucked something up.", ephemeral=True)

@bind.error
async def bind_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You must have admin perms to be able to run this.", ephemeral=True)

@rebind.error
async def rebind_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You must have admin perms to be able to run this.", ephemeral=True)

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
        else: 
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
        "`/react [message ID] [emoji name, plaintext]` - React to a specific message with a custom emoji. (Includes animated emojis!)",
        "`/reactabove [emoji name, plaintext]` - React to the message above with a custom emoji. (Includes animated emojis!)"
    ]
    await interaction.response.send_message("\n".join(commands_list))

@bot.tree.command(name="reactabove", description="React to the message above with a custom emoji. (Includes animated emojis!)")
@app_commands.describe(emoji_name="Name of the emoji to react with")
async def reactabove(interaction: discord.Interaction, emoji_name: str):
    if not interaction.channel:
        await interaction.response.send_message("This command can only be used in a text channel.", ephemeral=True)
        return

    channel = interaction.channel
    try:
        emoji = discord.utils.get(interaction.guild.emojis, name=emoji_name)
        if not emoji:
            await interaction.response.send_message(f"Emoji `:{emoji_name}:` not found. Only custom emojis from this server work.", ephemeral=True)
            return

        message_above = None
        async for msg in channel.history(limit=2):  
            if msg.id != interaction.id:  
                message_above = msg
                break

        if not message_above:
            await interaction.response.send_message("No message found above to react to.", ephemeral=True)
            return

        await message_above.add_reaction(emoji)
        await interaction.response.send_message(f"Reacted to the message above with `:{emoji_name}:`.", ephemeral=True)

        def check(reaction, user):
            return reaction.message.id == message_above.id and reaction.emoji == emoji and reaction.count > 1

        try:
            await bot.wait_for("reaction_add", timeout=10, check=check)
            await message_above.remove_reaction(emoji, bot.user)
        except asyncio.TimeoutError:
            pass
        except discord.HTTPException:
            pass

    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

@bot.tree.command(name="react", description="React to a specific message with a custom emoji. (Includes animated emojis!)")
@app_commands.describe(message_id="ID of the message to react to", emoji_name="Name of the emoji to react with")
async def react(interaction: discord.Interaction, message_id: str, emoji_name: str):
    await interaction.response.defer(ephemeral=True)
    try:
        message_id_int = int(message_id)
        channel = interaction.channel
        if not channel:
            await interaction.followup.send("This can't be used here. Server owners suck smh", ephemeral=True)
            return

        target_message = await channel.fetch_message(message_id_int)
        emoji = discord.utils.get(interaction.guild.emojis, name=emoji_name)
        if emoji:
            await target_message.add_reaction(emoji)
            await interaction.followup.send(f"Reacted to the message with ID {message_id} using {emoji}", ephemeral=True)

            def check(reaction, user):
                return (
                    reaction.message.id == target_message.id
                    and reaction.emoji == emoji
                    and reaction.count > 1
                )

            try:
                await bot.wait_for("reaction_add", check=check, timeout=10)
                await target_message.remove_reaction(emoji, bot.user)
            except asyncio.TimeoutError:
                pass
            except discord.HTTPException:
                pass
        else:
            await interaction.followup.send(f"Emoji `:{emoji_name}:` not found. Only custom emojis from this server work.", ephemeral=True)
    except ValueError:
        await interaction.followup.send("Invalid message ID format.", ephemeral=True)
    except discord.NotFound:
        await interaction.followup.send("Message not found. Make sure the ID is correct, and you run this in the same channel as the message.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to access that message.", ephemeral=True)

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

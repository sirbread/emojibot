import discord
from discord.ext import commands
from discord import app_commands

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

@bot.tree.command(name="bind", description="Bind the bot to a specific channel")
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
    if message.channel.id != binded_channel or message.author.bot or not message.attachments:
        return

    if len(message.attachments) > 0:
        attachment = message.attachments[0]
        emoji_name = message.content.strip()

        if not emoji_name.isalnum():
            await message.channel.send("Invalid characters in emoji name. Please use only letters and numbers.")
            return

        if discord.utils.get(message.guild.emojis, name=emoji_name):
            await message.channel.send("Emoji name already exists!")
            return

        try:
            image_data = await attachment.read()
            emoji = await message.guild.create_custom_emoji(name=emoji_name, image=image_data)
            await message.channel.send(f"Emoji {emoji} created successfully!")
        except Exception:
            await message.channel.send("An error occurred.")

bot.run("gonna add dnv soon(tm)")

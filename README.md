# emojibot
a fun custom emoji manager for discord. add, remove, and react with custom/animated emojis the faster (and no nitro) way :D <br>
**not intended for bigger servers. that can be _very_ problematic.**

## add the official bot to your server!
use [this](https://discord.com/oauth2/authorize?client_id=1333281378321694812) link. it may _sometimes_ be down, since it's hosted on @hackclub's nest server.

## features
- emoji managment:
  - add custom emojis by uploading an image or using an image URL, then adding a caption.
  - remove emojis using their names. 
  - fetch info about emojis (e.g., creation date, ID, author).<br>
<br>
- kinda nitro reactions:
  - react to specific messages or the most recent message above with a custom emoji.
  - includes support for animated emojis. (yep, you can react with animated gifs without nitro!)<br>
<br>
- auto-resize: automatically resizes large images/gifs to meet discords's really small emoji size limit. (gifs too :D) <br>
<br>
- binding and rebinding: most features happen in a binded channel so things don't get messy.<br>
<br>
- error handling: there's descriptive error messages for invalid commands or permissions issues.

## commands
### slash commands
- `/bind`  
  [admin] binds the bot to the channel where this command is run. 

- `/rebind [channel_id]`  
  [admin] rebinds the bot to a different channel using its ID. 

- `/react [message_id] [emoji_name]`  
  reacts to a specific message with a custom emoji (only custom emojis in the server are supported).

- `/reactabove [emoji_name]`  
  reacts to the most recent message above with a custom emoji, yknow, efficiency. (only custom emojis in the server are supported).

- `/help`  
  displays a list of all commands.

### text commands (in bound channel)

- `emoji_name [attachment_or_url]`  
  adds a custom emoji using the provided name and image (via attachment or direct URL).

- `remove [emoji_name]`  
  removes a custom emoji by name.

- `info [emoji_name]`  
  retrieves details about a custom emoji, such as creation date, author, and ID.

## acknowledgements
inspiration from @hackclub's emojibot. all credit for the idea goes to the author of emojibot, B Smith, in the slack.
 

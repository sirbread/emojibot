# emojibot
a fun custom emoji manager for discord. add, remove, and react with custom/animated emojis the faster (and no nitro) way :D

## features
- emoji managment:
  - add custom emojis by uploading an image or using an image URL (yknow, if you hate downloading), then adding a caption.
    - the bot will reply by adding the emoji to the server list, telling you the emoji (as a confirmation), then reacting with your emoji to your original message.
  - remove emojis using their names. 
  - fetch info about emojis (e.g., creation date, ID, author).
- kinda discord nitro reactions:
  - react to specific messages or the most recent message above with a custom emoji.
  - includes support for animated emojis. (yep, you can react with animated gifs without nitro!)
- auto-Resize: automatically resizes large images/gifs to meet discords's really small emoji size limit. (gifs too :D)
- binding and rebinding: most features happen in a binded channel so things don't get messy.
- error handling: there's descriptive error messages for invalid commands or permissions issues.

## Commands
### Slash Commands
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
  Adds a custom emoji using the provided name and image (via attachment or direct URL).

- `remove [emoji_name]`  
  removes a custom emoji by name.

- `info [emoji_name]`  
  retrieves details about a custom emoji, such as creation date, author, and ID.

## acknoledgements
inspiration from @hackclub's emojibot. all credit for the idea goes to the creator of emojibot in the slack.
 
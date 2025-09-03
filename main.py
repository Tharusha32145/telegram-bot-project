import os
import asyncio
from telethon import TelegramClient, events
from flask import Flask
from threading import Thread

# --- Replit Secrets වලින් මේවා ගනී ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

# --- ඔයාගේ වීඩියෝ විස්තර මෙතන දාන්න ---
VIDEO_MAP = {
    "video1": {
        "source": "https://sujanch-stream.koyeb.app/238145?hash=AgAD6B",
        "caption": "🎬 මේ වීඩියෝව විනාඩි 30කින් ඉබේම මැකී යනු ඇත."
    },
    "video2": {
        "source": "https://files.example.com/sample2.mp4", 
        "caption": "🎬 මේකත් විනාඩි 30කින් delete වෙනවා."
    }
}

DELETE_AFTER_SECONDS = 30 * 60  # විනාඩි 30

# --- Bot Code එක ---
client = TelegramClient('bot_session', API_ID, API_HASH)

@client.on(events.NewMessage(pattern=r'/start (.*)'))
async def start_handler(event):
    # ... (කලින් code එකේ තිබ්බ start_handler function එකේ ඉතුරු ටික මෙතන තියෙනවා)
    payload = event.pattern_match.group(1)
    video_data = VIDEO_MAP.get(payload)

    if not video_data:
        await event.respond("වීඩියෝව සොයාගත නොහැක. (Video not found.)")
        return
    try:
        await event.respond("වීඩියෝව චැනලයට යවමින් පවතී...")
        msg = await client.send_file(CHANNEL_ID, file=video_data["source"], caption=video_data["caption"])
        await event.respond("✅ වීඩියෝව චැනලයට යවන ලදී. එය විනාඩි 30කින් මැකී යනු ඇත.")
        await asyncio.sleep(DELETE_AFTER_SECONDS)
        await client.delete_messages(CHANNEL_ID, msg.id)
        print(f"Message {msg.id} deleted.")
    except Exception as e:
        await event.respond(f"❌ යම් දෝෂයක් සිදු විය: {e}")
        print(f"Error: {e}")

# --- 24/7 Online තියාගන්න පොඩි Web Server එකක් ---
app = Flask('')
@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Bot ව සහ Server එක Run කරන තැන ---
async def main():
    print("Bot is starting...")
    await client.start(bot_token=BOT_TOKEN)
    print("Bot has started successfully!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    keep_alive()
    # Telethon asyncio loop එක run කරනවා
    with client:
        client.loop.run_until_complete(main())

# main.py (Private Mode + Download Protection සහිත, අවසානම code එක)

import os
import asyncio
from telethon import TelegramClient, events
from flask import Flask
from threading import Thread

# --- 1. CONFIGURATION (සැකසුම්) ---
try:
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
except (ValueError, TypeError):
    print("!!! ERROR: Secrets (API_ID, API_HASH, BOT_TOKEN) හරියටම දාලා නෑ වගේ. Check කරන්න. !!!")
    exit()

VIDEO_MAP = {
    "video1": {
        "source": "https://ඔයාගේ-ඇත්ත-වීඩියෝ-ලින්ක්-එක.mp4",
        "caption": "🎬 මේ වීඩියෝව විනාඩි 30කින් ඉබේම මැකී යනු ඇත."
    }
}
DELETE_AFTER_SECONDS = 30 * 60

# --- 2. FLASK WEB SERVER (24/7 Online තියාගන්න) ---
app = Flask('')
@app.route('/')
def home():
    return "I am alive and running!"
def run_web_server():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

# --- 3. TELEGRAM BOT (ප්‍රධානම කොටස) ---
client = TelegramClient('bot_session', API_ID, API_HASH)

@client.on(events.NewMessage(pattern=r'/start (.*)'))
async def start_handler(event):
    payload = event.pattern_match.group(1).strip()
    if not payload:
        await event.respond("Please use the button from the Blogger post to get a video.")
        return
        
    video_data = VIDEO_MAP.get(payload)
    if not video_data:
        await event.respond(f"Sorry, I couldn't find a video for '{payload}'.")
        return
        
    try:
        await event.respond("Preparing your video, please wait...")
        
        # --- මෙතන තමයි ප්‍රධානම වෙනස්කම් දෙක තියෙන්නේ ---
        video_msg = await client.send_file(
            event.chat_id,  # 1. Channel එකට නෙවෙයි, message එක එවපු කෙනාටම යවනවා
            file=video_data["source"],
            caption=video_data.get("caption", ""),
            noforwards=True  # 2. Forward/Download කරන එක නවත්වනවා
        )
        
        await asyncio.sleep(DELETE_AFTER_SECONDS)
        await client.delete_messages(event.chat_id, video_msg.id)
        print(f"Message {video_msg.id} deleted for user {event.sender_id}")
    except Exception as e:
        await event.respond(f"An error occurred: {e}")
        print(f"!!! ERROR in start_handler: {e} !!!")

async def run_bot():
    await client.start(bot_token=BOT_TOKEN)
    print(">>> Telegram Bot is ONLINE! <<<")
    await client.run_until_disconnected()

# --- 4. PROGRAM එක පටන් ගන්නා තැන ---
if __name__ == "__main__":
    keep_alive()
    with client:
        client.loop.run_until_complete(run_bot())

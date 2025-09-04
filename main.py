# main.py ("Private Viewing Room" ක්‍රමයට අදාළ, අවසානම සහ නිවැරදිම code එක)

import os
import asyncio
import time
from telethon import TelegramClient, events
from flask import Flask
from threading import Thread

# --- 1. CONFIGURATION (සැකසුම්) ---
try:
    API_ID = int(os.environ.get("API_ID"))
    # --- මෙතන තිබ්බ වැරදි වරහන අයින් කරලා තියෙන්නේ ---
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    CHANNEL_ID = int(os.environ.get("-1003018666770")) # අපේ Private Channel එකේ ID එක
except Exception as e:
    print(f"!!! ERROR: Secrets හරියටම දාලා නෑ වගේ: {e} !!!")
    exit()

VIDEO_MAP = {
    "video1": { "source": "https://sujanch-stream.koyeb.app/238145?hash=AgAD6B" }
}
DELETE_AFTER_SECONDS = 30 * 60

# --- 2. FLASK WEB SERVER (වෙනසක් නෑ) ---
app = Flask('')
@app.route('/')
def home():
    return "I am alive and running!"
def run_web_server():
    app.run(host='host.0.0.0.0', port=8080)
def keep_alive():
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

# --- 3. TELEGRAM BOT (සම්පූර්ණයෙන්ම අලුත්) ---
client = TelegramClient('bot_session', API_ID, API_HASH)

posted_videos = {}

@client.on(events.NewMessage(pattern=r'/start (.*)'))
async def start_handler(event):
    try:
        expire_date = int(time.time() + 5 * 60)
        invite_link = await client.export_chat_invite_link(
            CHANNEL_ID,
            expire_date=expire_date,
            usage_limit=1
        )
        await event.respond(
            "වීඩියෝව නැරඹීමට, කරුණාකර පහත තාවකාලික link එකෙන් අපේ නැරඹුම් කාමරයට join වෙන්න. "
            "මෙම link එක විනාඩි 5කින් කල් ඉකුත් වේ.\n\n"
            f"➡️ {invite_link}"
        )
    except Exception as e:
        await event.respond(f"Sorry, an error occurred while creating an invite link: {e}")
        print(f"!!! ERROR in start_handler: {e} !!!")

@client.on(events.ChatAction)
async def join_handler(event):
    if event.user_joined and event.chat_id == CHANNEL_ID:
        user_id = event.user_id
        print(f"User {user_id} joined the channel. Sending video...")
        try:
            video_data = VIDEO_MAP.get("video1")
            if video_data:
                video_msg = await client.send_file(
                    CHANNEL_ID,
                    file=video_data["source"],
                    caption="🎬 මෙම වීඩියෝව විනාඩි 30කින් ඉබේම මැකී යනු ඇත."
                )
                posted_videos[video_msg.id] = time.time()
            else:
                print("Could not find video data for 'video1'")
        except Exception as e:
            print(f"!!! ERROR in join_handler: {e} !!!")

async def cleanup_task():
    while True:
        await asyncio.sleep(60)
        current_time = time.time()
        for msg_id, post_time in list(posted_videos.items()):
            if current_time - post_time > DELETE_AFTER_SECONDS:
                try:
                    print(f"Deleting old video message: {msg_id}")
                    await client.delete_messages(CHANNEL_ID, msg_id)
                    del posted_videos[msg_id]
                except Exception as e:
                    print(f"Could not delete message {msg_id}: {e}")
                    del posted_videos[msg_id]

async def run_bot():
    await client.start(bot_token=BOT_TOKEN)
    print(">>> Telegram Bot is ONLINE! (Private Viewing Room Mode) <<<")
    asyncio.create_task(cleanup_task())
    await client.run_until_disconnected()

# --- 4. PROGRAM එක පටන් ගන්නා තැන (වෙනසක් නෑ) ---
if __name__ == "__main__":
    keep_alive()
    with client:
        client.loop.run_until_complete(run_bot())

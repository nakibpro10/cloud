import os
import shutil
from fastapi import FastAPI, UploadFile, File
from pyrogram import Client
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") # মনে রাখবেন এটি পাবলিক চ্যানেলের ইউজারনেম হলে ভালো হয় (যেমন: @mychannel)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    temp_file = file.filename
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        async with Client("my_bot", api_id=int(API_ID), api_hash=API_HASH, bot_token=BOT_TOKEN) as bot:
            msg = await bot.send_document(
                chat_id=CHAT_ID,
                document=temp_file,
                file_name=file.filename
            )
            
            # ডাউনলোড লিঙ্ক তৈরি করা (যদি চ্যানেল পাবলিক হয়)
            # Private চ্যানেলের ক্ষেত্রে এটি টেলিগ্রাম অ্যাপে নিয়ে যাবে
            channel_name = str(CHAT_ID).replace("-100", "").replace("@", "")
            download_url = f"https://t.me/{channel_name}/{msg.id}"
            if "-" in channel_name: # Private চ্যানেলের জন্য বিশেষ লিঙ্ক
                 download_url = f"https://t.me/c/{channel_name}/{msg.id}"

        os.remove(temp_file)
        return {"ok": True, "download_url": download_url, "file_name": file.filename}
        
    except Exception as e:
        if os.path.exists(temp_file): os.remove(temp_file)
        return {"ok": False, "error": str(e)}

import asyncio
import platform
import time
import psutil
import uptime
from config import OWNER_ID
from AnonXMusic import app  # Or userbot if preferred

def format_bytes(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

def get_report():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    uptime_hrs = round((time.time() - uptime.boottime()) / 3600, 2)
    boot_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(uptime.boottime()))

    return f"""
<b><u>📡 ʜᴏᴜʀʟʏ sᴇʀᴠᴇʀ ʀᴇᴘᴏʀᴛ</u></b>

<b>• ᴏs:</b> {platform.system()} {platform.release()}
<b>• ᴜᴘᴛɪᴍᴇ:</b> {uptime_hrs} hrs
<b>• ʙᴏᴏᴛ ᴛɪᴍᴇ:</b> {boot_time}
<b>• ᴄᴘᴜ:</b> {cpu}%
<b>• ʀᴀᴍ:</b> {format_bytes(ram.used)} / {format_bytes(ram.total)} ({ram.percent}%)
<b>• ᴅɪsᴋ:</b> {format_bytes(disk.used)} / {format_bytes(disk.total)} ({disk.percent}%)
<b>• ᴘʏᴛʜᴏɴ:</b> {platform.python_version()}
""".strip()

async def auto_report():
    while True:
        try:
            text = get_report()
            await app.send_message(chat_id=OWNER_ID, text=text)
        except Exception as e:
            print(f"[!] Error in server report: {e}")
        await asyncio.sleep(3600)  # Wait 1 hour

# ✅ Now async version for main.py
async def run_reporter():
    asyncio.create_task(auto_report())
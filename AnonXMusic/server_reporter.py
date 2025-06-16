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
    cores = psutil.cpu_count()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    load1, load5, load15 = psutil.getloadavg()
    uptime_hrs = round((time.time() - uptime.boottime()) / 3600, 2)
    boot_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(uptime.boottime()))

    return f"""
<b>📡 ʜᴏᴜʀʟʏ sᴇʀᴠᴇʀ ʀᴇᴘᴏʀᴛ</b>
━━━━━━━━━━━━━━━━━━━
<b>• 🖥 OS:</b> {platform.system()} {platform.release()}
<b>• 💻 Arch:</b> {platform.machine()}
<b>• 🔧 CPU:</b> {cpu}% of {cores} cores
<b>• 📈 Load Avg:</b> {load1:.2f}, {load5:.2f}, {load15:.2f}
<b>• 📊 RAM:</b> {format_bytes(ram.used)} / {format_bytes(ram.total)} ({ram.percent}%)
<b>• 💾 Disk:</b> {format_bytes(disk.used)} / {format_bytes(disk.total)} ({disk.percent}%)
<b>• 🌐 Net IO:</b> ↑ {format_bytes(net.bytes_sent)} / ↓ {format_bytes(net.bytes_recv)}
<b>• 🧮 Processes:</b> {len(psutil.pids())}
<b>• ⏱ Uptime:</b> {uptime_hrs} hrs
<b>• 🕒 Boot Time:</b> {boot_time}
<b>• 🐍 Python:</b> {platform.python_version()}
━━━━━━━━━━━━━━━━━━━
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
import asyncio
import platform
import time
import socket
import psutil
import uptime
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from AnonXMusic import app
from config import OWNER_ID


def format_bytes(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


def get_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Unavailable"


def generate_bar(percentage: float, length: int = 10) -> str:
    filled_length = int(length * percentage / 100)
    bar = "█" * filled_length + "░" * (length - filled_length)
    return f"[{bar}] {percentage:.1f}%"


def get_report():
    cpu = psutil.cpu_percent(interval=1)
    cores = psutil.cpu_count(logical=True)
    threads = psutil.cpu_count(logical=False)
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    load1, load5, load15 = psutil.getloadavg()
    users = len(psutil.users())

    boot_time = uptime.boottime()
    uptime_secs = time.time() - boot_time.timestamp()
    uptime_hrs = round(uptime_secs / 3600, 2)
    boot_time_fmt = boot_time.strftime('%Y-%m-%d %H:%M:%S')

    try:
        temps = psutil.sensors_temperatures()
        cpu_temp = temps["coretemp"][0].current if "coretemp" in temps else "N/A"
    except:
        cpu_temp = "Unavailable"

    report = f"""
<b>📡 ʀᴇᴀʟ-ᴛɪᴍᴇ ꜱᴇʀᴠᴇʀ ʀᴇᴘᴏʀᴛ</b>
━━━━━━━━━━━━━━━━━━━━━━
<b>• 🖥 OS:</b> {platform.system()} {platform.release()}
<b>• 🧱 Arch:</b> {platform.machine()}
<b>• 🌐 Hostname:</b> {platform.node()}
<b>• 🌍 IP:</b> {get_ip()}
<b>• 🧮 Users:</b> {users}
━━━━━━━━━━━━━━━━━━━━━━
<b>• 🧠 CPU:</b> {generate_bar(cpu)} ({cpu}% of {cores} cores)
<b>• 🌡 Temp:</b> {cpu_temp}°C
<b>• 📊 Load Avg:</b> {load1:.2f}, {load5:.2f}, {load15:.2f}
━━━━━━━━━━━━━━━━━━━━━━
<b>• 📈 RAM:</b> {generate_bar(ram.percent)} {format_bytes(ram.used)} / {format_bytes(ram.total)}
<b>• 🔁 Swap:</b> {generate_bar(swap.percent)} {format_bytes(swap.used)} / {format_bytes(swap.total)}
<b>• 💽 Disk:</b> {generate_bar(disk.percent)} {format_bytes(disk.used)} / {format_bytes(disk.total)}
<b>• 🌐 Net:</b> ↑ {format_bytes(net.bytes_sent)} / ↓ {format_bytes(net.bytes_recv)}
━━━━━━━━━━━━━━━━━━━━━━
<b>• ⏱ Uptime:</b> {uptime_hrs:.2f} hrs
<b>• 🚀 Boot Time:</b> {boot_time_fmt}
<b>• 🐍 Python:</b> {platform.python_version()}
━━━━━━━━━━━━━━━━━━━━━━
""".strip()

    return report, cpu, ram.percent, disk.percent


async def auto_report():
    while True:
        try:
            report, cpu, ram, disk = get_report()
            await app.send_message(chat_id=OWNER_ID, text=report, parse_mode=ParseMode.HTML)

            alerts = []
            if cpu > 85:
                alerts.append(f"⚠️ <b>High CPU Usage:</b> {cpu:.1f}%")
            if ram > 85:
                alerts.append(f"⚠️ <b>High RAM Usage:</b> {ram:.1f}%")
            if disk > 90:
                alerts.append(f"⚠️ <b>Disk Almost Full:</b> {disk:.1f}%")

            if alerts:
                alert_text = "\n".join(alerts)
                await app.send_message(chat_id=OWNER_ID, text=alert_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            print(f"[!] Error in server report: {e}")

        await asyncio.sleep(300)  # Every 5 minutes


async def run_reporter():
    asyncio.create_task(auto_report())

# ━━━━━━━━━━━━━━━━
# ✅ Manual Commands
# ━━━━━━━━━━━━━━━━

@app.on_message(filters.command(["startreporter"]) & filters.user(OWNER_ID))
async def start_reporter_cmd(_, message: Message):
    await message.reply_text("✅ Server Reporter started (5-min interval)")
    await run_reporter()


@app.on_message(filters.command(["serverstats"]) & filters.user(OWNER_ID))
async def manual_server_stats(_, message: Message):
    try:
        report, _, _, _ = get_report()
        await message.reply_text(report, parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply_text(f"❌ Failed to get server stats.\nError: {e}")
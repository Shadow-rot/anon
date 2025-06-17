import io
import time
import platform
import psutil
import matplotlib.pyplot as plt
from pyrogram import filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)
from AnonXMusic import app
from config import OWNER_ID


def format_bytes(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


def generate_bar(percent: float, width: int = 12) -> str:
    fill = int(width * percent / 100)
    empty = width - fill
    return "│" * fill + "░" * empty


def get_report():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    load1, load5, load15 = psutil.getloadavg()
    boot_time = psutil.boot_time()
    uptime_hr = round((time.time() - boot_time) / 3600, 2)

    alerts = []
    if cpu > 85:
        alerts.append(f"↯ CPU overload: {cpu:.1f}%")
    if ram.percent > 85:
        alerts.append(f"↯ RAM usage high: {ram.percent:.1f}%")
    if disk.percent > 90:
        alerts.append(f"↯ Disk space low: {disk.percent:.1f}%")

    report = f"""
<b>⇨ SYSTEM RESOURCE STATUS</b>
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯
<b>→ OS:</b> <code>{platform.system()} {platform.release()}</code>
<b>→ Arch:</b> <code>{platform.machine()}</code>
<b>→ Uptime:</b> <code>{uptime_hr:.2f} hours</code>
<b>→ Python:</b> <code>{platform.python_version()}</code>
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯
<b>→ CPU:</b> <code>{cpu:.1f}%</code>   {generate_bar(cpu)}
<b>→ RAM:</b> <code>{ram.percent:.1f}%</code>   {generate_bar(ram.percent)}
<b>→ Disk:</b> <code>{disk.percent:.1f}%</code>   {generate_bar(disk.percent)}
<b>→ Load:</b> <code>{load1:.2f}, {load5:.2f}, {load15:.2f}</code>
<b>→ Net:</b> ↑ <code>{format_bytes(net.bytes_sent)}</code> ↓ <code>{format_bytes(net.bytes_recv)}</code>
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯
""".strip()

    return report, alerts, cpu, ram.percent, disk.percent


def generate_graph():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    labels = ["CPU", "RAM", "Disk"]
    values = [cpu, ram, disk]
    colors = ["#5E81AC", "#A3BE8C", "#BF616A"]

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=colors)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Usage (%)")
    ax.set_title("Server Resource Usage")

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 2, f"{val:.1f}%", ha='center')

    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    return buffer


@app.on_message(filters.command("serverstats") & filters.user(OWNER_ID))
async def server_stats_handler(_, message: Message):
    report, alerts, *_ = get_report()
    image = generate_graph()

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("↻ Refresh Stats", callback_data="refresh_server_stats")]]
    )

    await message.reply_photo(photo=image, caption=report, reply_markup=keyboard)

    if alerts:
        await message.reply_text(
            "<b>⚠ SERVER ALERTS</b>\n" + "\n".join(alerts),
            quote=True
        )


@app.on_callback_query(filters.regex("refresh_server_stats") & filters.user(OWNER_ID))
async def refresh_stats_callback(_, query: CallbackQuery):
    await query.answer("Refreshing stats...", show_alert=False)

    report, alerts, *_ = get_report()
    image = generate_graph()

    try:
        await query.message.edit_media(
            media=InputMediaPhoto(media=image),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("↻ Refresh Stats", callback_data="refresh_server_stats")]]
            ),
        )
        await query.message.edit_caption(caption=report)

        if alerts:
            await query.message.reply_text("<b>⚠ SERVER ALERTS</b>\n" + "\n".join(alerts))

    except Exception as e:
        await query.message.reply_text(f"⚠ Failed to refresh stats:\n<code>{e}</code>")
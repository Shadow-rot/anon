import re
from pyrogram.types import InlineKeyboardButton

BTN_URL_REGEX = re.compile(
    r"(([^]+?)buttonurl:(?:/{0,2})(.+?)(:same)?)"
)

def button_markdown_parser(text: str):
    if not text:
        return "", []

    markdown_note = text
    text_data = ""
    buttons = []

    # Safely extract content after command
    if markdown_note.startswith('/'):
        args = markdown_note.split(None, 2)
        if len(args) >= 3:
            markdown_note = args[2]
        else:
            markdown_note = ""

    prev = 0
    for match in BTN_URL_REGEX.finditer(markdown_note):
        # Check if btnurl is escaped
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and markdown_note[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        # If even, not escaped → create button
        if n_escapes % 2 == 0:
            try:
                label = match.group(2)
                url = match.group(3)
                button = InlineKeyboardButton(text=label, url=url)

                if bool(match.group(4)) and buttons:
                    buttons[-1].append(button)
                else:
                    buttons.append([button])

                text_data += markdown_note[prev:match.start(1)]
                prev = match.end(1)
            except Exception:
                continue
        else:
            text_data += markdown_note[prev:to_check]
            prev = match.start(1) - 1

    text_data += markdown_note[prev:]
    return text_data, buttons
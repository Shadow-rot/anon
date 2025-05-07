import asyncio
from AnonXMusic.utils.error_reporter import send_error_to_owner

def global_exception_handler(loop, context):
    exception = context.get("exception")
    if not exception:
        return
    asyncio.create_task(send_error_to_owner(exception))

async def main():
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(global_exception_handler)

    await app.start()
    await idle()
    await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        asyncio.run(send_error_to_owner(e))
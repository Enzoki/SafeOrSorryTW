from main import get_travel_advisory, send_discord_message, generate_message
import datetime as dt
import asyncio
import os
import sys

DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

async def main():
    travel_adv = get_travel_advisory()
    message = generate_message(travel_adv)
    await send_discord_message(DISCORD_WEBHOOK_URL, message)

if __name__ == "__main__":
    asyncio.run(main())

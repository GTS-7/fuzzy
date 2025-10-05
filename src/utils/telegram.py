import asyncio
import aiohttp

BOT_TOKEN = '8404699975:AAFL8Si0qzEa8RH2-o1nwIEyRqiUcpfBYgA'      # Your bot token
CHAT_ID = '-4863042370'          # Your chat ID
MESSAGE = 'Hello from Python!'

async def send_message(text, bot_token="", chat_id=""):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": text
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            result = await response.json()
            return result

# Run the async function
asyncio.run(send_message(MESSAGE, BOT_TOKEN, CHAT_ID))
from utils.imports import *

async def answer(message: Message, text: str = None, photo: bool = False, response: str = None):
    if text:
        await message.reply(text)
    if photo and response:
        await message.reply_photo(photo=response)

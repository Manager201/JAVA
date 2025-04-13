from telethon.sync import TelegramClient

api_id = 5127578  # Replace with your API ID
api_hash = "048b23e17b56163581cefa5131b44bff"  # Replace with your API hash

client = TelegramClient("session_name", api_id, api_hash)

client.start()
print("Login successful!")
client.disconnect()

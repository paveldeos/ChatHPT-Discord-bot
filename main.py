import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")
CHATGPT_API_URL = "https://api.openai.com/v1/chat/completions"

intents = discord.Intents.all()
intents.messages = True

class ChatGPT4Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")
        for guild in self.guilds:
            print(f"Connected to server: {guild.name} (id: {guild.id})")

bot = ChatGPT4Bot(command_prefix=None, intents=intents)

async def load_conversation(channel):
    conversation = []
    async for msg in channel.history(limit=100):
        conversation.append({"role": "system" if msg.author.bot else "user", "content": msg.content})
    return conversation

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"Received message: {message.content}")
    conversation = await load_conversation(message.channel)
    response = generate_response(message.content, conversation)
    print(f"Generated response: {response}")
    await message.channel.send(response)

def generate_response(prompt, conversation):
    headers = {
        "Authorization": f"Bearer {CHATGPT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.4,
        "top_p": 0.9,
        "messages": conversation + [{"role": "user", "content": prompt}],
    }
    response = requests.post(CHATGPT_API_URL, json=data, headers=headers)
    response_json = response.json()

    if response.status_code == 200:
        return response_json["choices"][0]["message"]["content"]
    else:
        print("Error:", response.status_code, response.text)
        return "Sorry, I couldn't generate a response."

def main():
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()

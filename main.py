import discord
import time
import os
from discord.ext import commands
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv('discord_bot_lous.env')
print("Discord Token:", os.getenv('DISCORD_TOKEN'))

# Retrieve Discord token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Variables for managing chat history
explicit_input = ""
chatgpt_output = 'Chat log: /n'
cwd = os.getcwd()
i = 1

# Find a new file name for storing chat history if the previous one already exists
while os.path.exists(os.path.join(cwd, f'chat_history{i}.txt')):
    i += 1

# Create a new file for storing chat history
history_file = os.path.join(cwd, f'chat_history{i}.txt')
with open(history_file, 'w') as f:
    f.write('\n')

# Initialize the chat history string
chat_history = ''

# Retrieve OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuration for the bot's impersonation role
name = 'Assistant Director of Undergraduate Academic Programs, Kristine Nelson'
role = 'The University of Virgina Frank Batten School of Public Policy and Leadership Collage Advisor'

# Read data for the bot to use from a CSV file
with open('Lou_List.csv', 'r') as lou_list_file:
    lou_list_contents = lou_list_file.read()

# Define the impersonated role and instructions for the bot
impersonated_role = f"""
    From now on, you are going to act as {name}. Your role is {role}. By the way, don't say 'As Lou' for every answer.
    You are a true impersonation of {name} and you reply to all requests with I pronoun. You will be informed by the CSV data here: {lou_list_contents}"""

# Function to handle chat input using OpenAI's GPT model
def chatcompletion(user_input, impersonated_role, explicit_input, chat_history):
    # Create a message using OpenAI's Chat Completion
    output = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=1,
        presence_penalty=0,
        frequency_penalty=0,
        messages=[
            {"role": "system", "content": f"{impersonated_role}. Conversation history: {chat_history}"},
            {"role": "user", "content": f"{user_input}. {explicit_input}"},
        ]
    )

    # Extract and return the chat output from the response
    for item in output['choices']:
        chatgpt_output = item['message']['content']
    return chatgpt_output

# Function to handle user chat input and maintain chat history
def chat(user_input):
    global chat_history, name, chatgpt_output
    current_day = time.strftime("%d/%m", time.localtime())
    current_time = time.strftime("%H:%M:%S", time.localtime())

    # Append user input to the chat history
    chat_history += f'\nUser: {user_input}\n'

    # Get response from chatcompletion function and format it
    chatgpt_raw_output = chatcompletion(user_input, impersonated_role, explicit_input, chat_history).replace(f'{name}:', '')
    chatgpt_output = f'{name}: {chatgpt_raw_output}'

    # Update the chat history with the bot's response
    chat_history += chatgpt_output + '\n'
    with open(history_file, 'a') as f:
        f.write('\n' + current_day + ' ' + current_time + ' User: ' + user_input + ' \n' + current_day + ' ' + current_time + ' ' + chatgpt_output + '\n')
        f.close()
    return chatgpt_raw_output

# Initialize Discord client with intents
intents = discord.Intents().all()
client = commands.Bot(command_prefix="!", intents=intents)

# Event triggered when the bot is ready
@client.event
async def on_ready():
    print("Bot is ready")

# Command for users to say hi to the bot
@client.command()
async def hi(ctx):
    await ctx.send("Hello, nothing to see here")

# Command to provide information about Batten Courses
@client.command(brief='Batten Course available as of today...if I implemented it', description='Batten Courses available as of today')
async def record(ctx):
    await ctx.send("Hello, this bot will help answer questions related to the current stats of Batten Courses. you can enter !Record, !Exit or just ask a question")

# Event to handle incoming messages and respond using the chat bot
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Log message details
    print(message.author)
    print(client.user)
    print(message.content)

    # Get response from the chat bot and send it
    answer = chat(message.content)
    await message.channel.send(answer)

# Command to shut down the bot, only accessible to the bot owner
@client.command()
@commands.is_owner()
async def shutdown(context):
    exit()

# Run the bot using the Discord token
client.run(TOKEN)

import os
import telebot
import re
import faiss
import pickle
import json

from dotenv import load_dotenv

from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from ingest import process_link
from structure import requestJson, structure, formatJsonResponse

load_dotenv()

template = """You have YouTube video transcripts. When a conversation is initiated, greet the user humanely and summarize the video - all based on the transcripts that you have. Summarize in bullet points, don't exceed more than 75 words.

Add questions for users to ponder upon and learn from the videos better. Add 3 questions at max.

Use conversation history for context (delimited by <hs></hs>)

<hs>
{history}
</hs>

{context}
Human: {question}
AI:
"""
llm = OpenAI(temperature=0)
memory = ConversationBufferMemory(memory_key="history", input_key="question")
prompt = PromptTemplate(
    input_variables=["context", "question", "history"], template=template
)


def refresh_data():
    index = faiss.read_index("docs.index")

    with open("faiss_store.pkl", "rb") as f:
        store = pickle.load(f)

    store.index = index
    # chain_type_kwargs = {"prompt": prompt, "memory": memory}
    conversation = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=store.as_retriever(),
        # chain_type_kwargs=chain_type_kwargs,
    )
    return conversation


# Getting Bot Token From Secrets
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Creating Telebot Object
bot = telebot.TeleBot(BOT_TOKEN)


welcome_message = """Hello! I am CheckmateAI. I can summarize YouTube videos and help you learn better by asking and answering questions.

To get started, do the following:

1. Send me a YouTube video link and wait for me to watch it.
2. Ask questions!
"""


# Whenever Starting Bot
@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    # welcome_res = conversation({"question": template})["answer"]
    bot.reply_to(message, welcome_message)


# Reply To All Messages (excluding YouTube links)
@bot.message_handler(
    func=lambda msg: not re.match(r".*(youtube\.com|youtu\.be).*", msg.text)
)
def all(message):
    formatted_message = requestJson(message.text, json.dumps(structure()))
    received_json = refresh_data().run(formatted_message)
    text = formatJsonResponse(received_json)
    bot.reply_to(message, text)
    print(f"Message received - {message.text}\n")


# YT Link Handler
@bot.message_handler(
    regexp="^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
)
def yt_link(message):
    bot.reply_to(
        message,
        "I am watching the YouTube video for you, friend. Please wait.",
    )
    process_link(message.text)
    refresh_data()
    bot.reply_to(message, "I finished watching the video. Ask questions!")


print("Bot Started And Waiting For New Messages\n")

# Waiting For New Messages
bot.infinity_polling()

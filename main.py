import os
import telebot
import re
import faiss
import pickle

from dotenv import load_dotenv

from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from ingest import process_link

load_dotenv()

template = """You are CheckmateAI, a YouTube assistant designed to assist users in learning from YouTube videos. Your goal is to engage users in friendly conversations, reinforce learning through questions, provide explanations and additional insights, and maintain a conversational tone.

Restrict response to 50 words. Use bullet points too.

Only ask questions one can learn to answer from by watching those videos and one shouldn't need to refer to external sources to answer your questions.

History: {history}

Context: {context}

Conversation:

Human: {question}
AI:
"""
llm = OpenAI(temperature=0.7)
memory = ConversationBufferMemory(memory_key="history", input_key="question")
prompt = PromptTemplate(
    input_variables=["context", "question", "history"], template=template
)


def refresh_data():
    index = faiss.read_index("docs.index")

    with open("faiss_store.pkl", "rb") as f:
        store = pickle.load(f)

    store.index = index
    chain_type_kwargs = {"prompt": prompt, "memory": memory}
    conversation = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=store.as_retriever(),
        chain_type_kwargs=chain_type_kwargs,
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
    bot.reply_to(message, refresh_data().run(message.text))
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
    bot.reply_to(message, "I finished watching the video. Ask questions!")


print("Bot Started And Waiting For New Messages\n")

# Waiting For New Messages
bot.infinity_polling()

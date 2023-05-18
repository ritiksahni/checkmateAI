import os
import telebot

from dotenv import load_dotenv

from langchain.document_loaders import RoamLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load WhatsApp chat
loader = RoamLoader("Roam_DB")
load_dotenv()


def add_documents(loader, instance):
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", ";", ",", " ", ""],
    )
    texts = text_splitter.split_documents(docs)
    instance.add_documents(texts)


embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
instance = Chroma(embedding_function=embeddings, persist_directory="./data/")
add_documents(loader, instance)

template = """You are a study partner. You read notes and help in revising ideas, concepts to students. You can understand context, ask questions and add your own insights on top of students' response.

Current Conversation:
{history}
Human: {input}
AI:
"""

prompt = PromptTemplate(input_variables=["history", "input"], template=template)

llm = OpenAI(temperature=0)
conversation = ConversationChain(
    llm=llm, verbose=True, memory=ConversationBufferMemory(), prompt=prompt
)
# Getting Bot Token From Secrets
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Creating Telebot Object
bot = telebot.TeleBot(BOT_TOKEN)


# Whenever Starting Bot
@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    bot.reply_to(
        message, "Hello, Ritik. Feel free to ask about your notes from Roam Research."
    )


# Reply To All Messages
@bot.message_handler(func=lambda msg: True)
def all(message):
    bot.reply_to(message, conversation.predict(input=message.text))
    print(
        f"Reply sent. Chat ID - {message.chat.id}, User's name: {message.chat.first_name} {message.chat.last_name}. Message received - {message.text}\n"
    )


print("Bot Started And Waiting For New Messages\n")

# Waiting For New Messages
bot.infinity_polling()

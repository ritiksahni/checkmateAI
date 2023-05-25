import os
import telebot
import zipfile
import shutil

from dotenv import load_dotenv

from langchain.document_loaders import RoamLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import (
    ConversationChain,
    ConversationalRetrievalChain,
    RetrievalQA,
)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

load_dotenv()


def loadContent():
    loader = RoamLoader("./Roam_DB")

    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", ";", ",", " ", ""],
    )
    texts = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    instance = Chroma.from_documents(texts, embeddings, persist_directory="./data")
    template = """You are an AI study partner, you have access to concepts, notes, books, etc. You must ask 3 questions one-by-one in turns. Ask a question, wait for response and respond to that answer with your feedback and the next question. Stop asking questions when 3 are complete but make sure to give feedback to every response based on the notes that you have access to.

    Feel free to give words of encouragement to behave like a good study partner.

    Every message should be related on one random topic exclusively, don't move the conversation to different directions. Just stick to that and ask/answer based on that. But remember, only talk about ideas from the Roam Research notes given to you.
    
    With every question, add a "status marker" at the end. Add "expecting information" if you're expecting a response from human on that particular question. Add "concluded" if you've received a response on that question and are just trying to give feedback.

    Don't continue talking for a long time. Ask 3 questions and conclude the chat session. Don't do anything else other than ask questions, add insights on the same topic.
    {context}
    Human: {question}
    AI:
    """

    llm = OpenAI(temperature=0)

    prompt = PromptTemplate(input_variables=["context", "question"], template=template)

    chain_type_kwards = {"prompt": prompt}
    conversation = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=instance.as_retriever(),
        chain_type_kwargs=chain_type_kwards,
    )
    return conversation


# Getting Bot Token From Secrets
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Creating Telebot Object
bot = telebot.TeleBot(BOT_TOKEN)


def extractRoamContent():
    with zipfile.ZipFile("./roam_export.zip", "r") as export:
        export.extractall("./Roam_DB")


welcome_message = """Hello! I am CheckmateAI, I will go through your notes from Roam Research and help you study, revise notes. I hope I prove myself to be a good study partner. Before we begin, I'd like to read your notes. Here's what you need to do:
- Open Roam Research
- Click on "Export" on top-right bar.
- Export as "Markdown"
- Send the downloaded ZIP file to me, your study partner!

It's as simple as that. I'll read your notes and initiate conversations based on that.
"""


# Whenever Starting Bot
@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    # welcome_res = conversation({"question": template})["answer"]
    bot.reply_to(message, welcome_message)


# Reply To All Messages
@bot.message_handler(func=lambda msg: True)
def all(message):
    bot.reply_to(message, loadContent().run(message.text))
    # bot.reply_to(message, conversation.predict(input=message.text))
    print(
        f"Reply sent. Chat ID - {message.chat.id}, User's name: {message.chat.first_name} {message.chat.last_name}. Message received - {message.text}\n"
    )


@bot.message_handler(content_types=["document"])
def saveZip(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("roam_export.zip", "wb") as f:
        f.write(downloaded_file)
    if os.path.exists("./Roam_DB"):
        shutil.rmtree("./Roam_DB", ignore_errors=True)
        extractRoamContent()
        os.remove("./roam_export.zip")
    else:
        extractRoamContent()
        os.remove("./roam_export.zip")
        bot.reply_to(message, "Content extracted, bot is ready to roll...")


print("Bot Started And Waiting For New Messages\n")

# Waiting For New Messages
bot.infinity_polling()

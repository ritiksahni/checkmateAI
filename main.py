import os
import telebot
import zipfile
import shutil
import re

from dotenv import load_dotenv

from langchain.document_loaders import RoamLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

import transcription

load_dotenv()


loader = RoamLoader("./Roam_DB")

docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", ";", ",", " ", ""],
)

texts = text_splitter.split_documents(docs)  # For document loaders such as RoamLoader

embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
instance = Chroma.from_documents(texts, embeddings, persist_directory="./data")
template = """You have YouTube video transcripts. When a conversation is initiated, greet the user humanely and ask 3 questions at max regarding the video. Summarize the video also if asked to do so - all based on the transcripts that you have.

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

chain_type_kwards = {"prompt": prompt, "memory": memory}
conversation = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=instance.as_retriever(),
    chain_type_kwargs=chain_type_kwards,
)

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


# Reply To All Messages (excluding YouTube links)
@bot.message_handler(
    func=lambda msg: not re.match(r".*(youtube\.com|youtu\.be).*", msg.text)
)
def all(message):
    bot.reply_to(message, conversation.run(message.text))
    print(
        f"Reply sent. Chat ID - {message.chat.id}. Message received - {message.text}\n"
    )


# YT Link Handler
@bot.message_handler(
    regexp="^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
)
def yt_link(message):
    bot.reply_to(
        message.text,
        "I am watching the YouTube video for you, friend. Please wait.",
    )
    yt_result = transcription.main(message.text)
    # Run text splitting function
    yt_texts = text_splitter.create_documents(yt_result)
    chain_type_kwards = {"prompt": prompt, "memory": memory}
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    instance = Chroma.from_documents(yt_texts, embeddings, persist_directory="./data")
    conversation = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=instance.as_retriever(),
        chain_type_kwargs=chain_type_kwards,
    )

    bot.reply_to(message, "I finished watching the video. Ask questions!")


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

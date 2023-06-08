import faiss
import os
import pickle

from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

import transcription

load_dotenv()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", ";", ",", " ", ""],
)


def process_link(youtube_link):
    transcription.main(youtube_link)
    with open("transcript.txt", "r") as f:
        yt_transcription = f.readlines()

    # Text Splitting
    yt_texts = text_splitter.create_documents([yt_transcription])
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    instance = FAISS.from_documents(yt_texts, embeddings)
    faiss.write_index(instance.index, "docs.index")
    instance.index = None
    with open("faiss_store.pkl", "wb") as f:
        pickle.dump(instance, f)
    return True

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

loader=TextLoader("data/docs.txt")
documents=loader.load()

text_splitter=RecursiveCharacterTextSplitter(chunk_size=300,chunk_overlap=50)
docs=text_splitter.split_documents(documents)

embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db=Chroma.from_documents(docs,embeddings,persist_directory="db")

print("Ingestion complete!")
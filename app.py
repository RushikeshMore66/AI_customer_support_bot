import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from groq import Groq
import os

client=Groq(api_key=os.getenv("GROQ_API_KEY"))

embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db=Chroma(persist_directory="db",embedding_function=embeddings)

st.title("Customer Support Bot")

query=st.text_input("Ask a question: ")

if query:
    docs=db.similarity_search(query, k=3)
    context="\n".join([doc.page_content for doc in docs])

    # Prompt
    prompt = f"""
    You are a helpful customer support assistant.
    Answer based only on the context below.

    Context:
    {context}

    Question:
    {query}

    Answer:
    """
    response=client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role":"user","content":prompt}]
    )
    answer = response.choices[0].message.content
    st.write("### 🤖 Answer:")
    st.write(answer)

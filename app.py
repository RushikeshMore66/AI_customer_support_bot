import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from groq import Groq
import os
from dotenv import load_dotenv
import time

load_dotenv()
st.markdown("""
<style>
.chat-message {
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

client=Groq(api_key=os.getenv("GROQ_API_KEY"))

embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db=Chroma(persist_directory="db",embedding_function=embeddings)
if "messages" not in st.session_state:
    st.session_state.messages=[]

st.title("🤖 AI Customer Support Bot")
st.caption("24/7 Customer Support")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_query=st.chat_input("Ask a question: ")

if user_query:
    st.session_state.messages.append({"role":"user","content":user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        st.markdown("Thinking...")

    docs=db.similarity_search(user_query, k=3)
    context="\n".join([doc.page_content for doc in docs])

    # Prompt
    prompt = f"""
You are a top-tier customer support agent similar to Amazon.

Behavior:
- Always be polite and professional
- Give clear step-by-step solutions
- Keep answers short but helpful
- If question is about refund/returns → explain process step-by-step
- If question is unclear → ask a follow-up question
- Never make up information outside context

Context:
{context}

User Question:
{user_query}

Answer in a helpful and human tone:
"""
    response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are an expert customer support agent."},
        {"role": "user", "content": prompt}
    ]
)

answer = response.choices[0].message.content

# Save full answer
st.session_state.messages.append({"role": "assistant", "content": answer})

# Typing effect
with st.chat_message("assistant"):
    message_placeholder = st.empty()
    full_text = ""

    for word in answer.split():
        full_text += word + " "
        message_placeholder.markdown(full_text)
        time.sleep(0.03)  # speed control

    message_placeholder.markdown(full_text)
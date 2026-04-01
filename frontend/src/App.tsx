import { useState, useRef, useEffect } from "react";
import "./index.css";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const sendMessage = async (customMsg?: string) => {
    const messageToSend = customMsg || input;
    if (!messageToSend.trim()) return;

    const newMessages: Message[] = [...messages, { role: "user", content: messageToSend }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: messageToSend, history: messages }),
      });

      if (!res.ok) throw new Error("Server error");
      const data = await res.json();

      setMessages([...newMessages, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setMessages([...newMessages, { role: "assistant", content: "Error connecting to server. Please try again later." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="chat-card">
        <header className="chat-header">
          <div className="header-info">
            <h1>🤖 AI Support</h1>
            <p>24/7 Customer Assistant</p>
          </div>
        </header>

        <div className="quick-actions">
          <button className="action-btn" onClick={() => sendMessage("How can I track my order?")}>
            📦 Track Order
          </button>
          <button className="action-btn" onClick={() => sendMessage("How can I request a refund?")}>
            💸 Refund
          </button>
        </div>

        <div className="chat-area" ref={scrollRef}>
          {messages.length === 0 && (
            <div className="empty-state">
              <p>Hi there! 👋 How can I assist you today?</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`message-wrapper ${msg.role}`}>
              <div className="message-content">
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="message-wrapper assistant">
              <div className="message-content typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
        </div>

        <div className="input-area">
          <input
            type="text"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button className="send-btn" onClick={() => sendMessage()}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

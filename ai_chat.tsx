import { useState } from "react";
// Assuming you have shadcn/ui installed at these paths
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";

// Define message type to solve TypeScript missing type errors
type Message = {
    role: "user" | "assistant";
    content: string;
};

export default function ChatApp() {
    // Add type annotations
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);

    // Properly type the parameter
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

            if (!res.ok) throw new Error("Network response was not ok");
            const data = await res.json();

            setMessages([
                ...newMessages,
                { role: "assistant", content: data.reply },
            ]);
        } catch (err) {
            setMessages([
                ...newMessages,
                { role: "assistant", content: "Error connecting to server" },
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
            <Card className="w-full max-w-md shadow-2xl rounded-2xl">
                <CardContent className="p-4 flex flex-col h-[600px]">
                    {/* Header */}
                    <div className="mb-3">
                        <h2 className="text-xl font-bold">🤖 AI Support</h2>
                        <p className="text-sm text-gray-500">24/7 Customer Assistant</p>
                    </div>

                    {/* Quick Actions */}
                    <div className="flex gap-2 mb-3">
                        <Button variant="outline" onClick={() => sendMessage("How can I track my order?")}>
                            📦 Track Order
                        </Button>
                        <Button variant="outline" onClick={() => sendMessage("How can I request a refund?")}>
                            💸 Refund
                        </Button>
                    </div>

                    {/* Chat Area */}
                    <div className="flex-1 overflow-y-auto space-y-2 mb-3">
                        {messages.length === 0 && (
                            <div className="text-center text-gray-400 mt-10">
                                <p>Hi! How can I help you today?</p>
                            </div>
                        )}
                        {messages.map((msg, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`p-2 rounded-xl max-w-[80%] ${
                                    msg.role === "user"
                                        ? "bg-blue-500 text-white ml-auto"
                                        : "bg-gray-200 text-black"
                                }`}
                            >
                                {msg.content}
                            </motion.div>
                        ))}

                        {loading && (
                            <div className="text-sm text-gray-400">Typing...</div>
                        )}
                    </div>

                    {/* Input */}
                    <div className="flex gap-2">
                        <Input
                            value={input}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
                            placeholder="Type your message..."
                            onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === "Enter" && sendMessage()}
                        />
                        <Button onClick={() => sendMessage()}>Send</Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

"use client";
import { useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Ask me anything about Ali's projects — I'll search across his repos and cite what I find." }
  ]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages([...messages, { role: "user", text: input }]);
    setInput("");
    // Backend wiring comes later — this just proves the UI works for now
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar: repo list placeholder */}
      <aside className="w-64 border-r border-[var(--border)] p-4 hidden md:block">
        <h2 className="font-mono-display text-sm text-[var(--text-muted)] mb-3">REPOSITORIES</h2>
        <ul className="space-y-2 text-sm text-[var(--text-muted)]">
          <li>NeuralLens</li>
          <li>Picassify</li>
          <li>DiabetesDetector</li>
        </ul>
      </aside>

      {/* Main chat area */}
      <main className="flex-1 flex flex-col">
        <header className="border-b border-[var(--border)] p-4">
          <h1 className="font-mono-display text-lg">CodexQuery</h1>
          <p className="text-xs text-[var(--text-muted)]">grep your own code, with an LLM attached</p>
        </header>

        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`max-w-2xl ${msg.role === "user" ? "ml-auto" : ""}`}>
              <div className={`rounded-lg p-3 text-sm ${
                msg.role === "user"
                  ? "bg-[var(--accent-blue)] text-[#0D1117]"
                  : "bg-[#161B22] border border-[var(--border)]"
              }`}>
                {msg.text}
              </div>
            </div>
          ))}
        </div>

        <div className="border-t border-[var(--border)] p-4 flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask about a project..."
            className="flex-1 bg-[#161B22] border border-[var(--border)] rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-[var(--accent-blue)]"
          />
          <button
            onClick={handleSend}
            className="bg-[var(--accent-green)] text-[#0D1117] px-4 py-2 rounded-lg text-sm font-medium"
          >
            Send
          </button>
        </div>
      </main>
    </div>
  );
}
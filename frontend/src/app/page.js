"use client";
import { useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Ask me anything about Ali's projects - I'll search across his repos and cite what I find.", sources: [] }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    const question = input;
    setMessages(prev => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", text: data.answer, sources: data.sources }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", text: "Something went wrong reaching the backend. Is it running?", sources: [] }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      <aside className="w-64 border-r border-[var(--border)] p-4 hidden md:block">
        <h2 className="font-mono-display text-sm text-[var(--text-muted)] mb-3">REPOSITORIES</h2>
        <ul className="space-y-2 text-sm text-[var(--text-muted)]">
          <li>NeuralLens</li>
          <li>Picassify</li>
          <li>DiabetesDetector</li>
        </ul>
      </aside>

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
              {msg.sources && msg.sources.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {msg.sources.map((src, j) => (
                    <span key={j} className="font-mono-display text-xs text-[var(--accent-green)] bg-[#161B22] border border-[var(--border)] rounded px-2 py-1">
                      {src}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="max-w-2xl">
              <div className="rounded-lg p-3 text-sm bg-[#161B22] border border-[var(--border)] text-[var(--text-muted)]">
                Searching repos and generating an answer...
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-[var(--border)] p-4 flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !loading && handleSend()}
            placeholder="Ask about a project..."
            disabled={loading}
            className="flex-1 bg-[#161B22] border border-[var(--border)] rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-[var(--accent-blue)] disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="bg-[var(--accent-green)] text-[#0D1117] px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
          >
            {loading ? "..." : "Send"}
          </button>
        </div>
      </main>
    </div>
  );
}
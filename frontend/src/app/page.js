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
    <div className="flex h-screen bg-[var(--bg)]">
      <aside className="w-64 border-r border-[var(--border)] p-5 hidden md:block">
        <h2 className="font-display text-xs font-medium tracking-wide text-[var(--text-muted)] mb-4 uppercase">Repositories</h2>
        <ul className="space-y-3 text-sm text-[var(--text)]">
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-blue)]" />NeuralLens</li>
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-blue)]" />Picassify</li>
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-blue)]" />DiabetesDetector</li>
        </ul>
      </aside>

      <main className="flex-1 flex flex-col">
        <header className="border-b border-[var(--border)] px-6 py-4">
          <h1 className="font-display text-xl font-medium">CodexQuery</h1>
          <p className="text-xs text-[var(--text-muted)] mt-0.5">Ask questions about Ali's projects, grounded in the actual code</p>
        </header>

        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
          {messages.map((msg, i) => (
            <div key={i} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
              <div className={`max-w-xl rounded-xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-[var(--accent-blue-soft)] text-[var(--text)] border border-[var(--accent-blue)]/20"
                  : "bg-[var(--surface)] border border-[var(--border)]"
              }`}>
                {msg.text}
              </div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="relative mt-2 max-w-xl">
                  <div className="absolute -top-2 left-4 w-px h-2 bg-[var(--accent-amber)]" />
                  <div className="flex flex-wrap gap-2">
                    {msg.sources.map((src, j) => (
                      <span key={j} className="font-mono text-xs text-[var(--accent-amber)] bg-[var(--surface)] border border-[var(--accent-amber)]/30 rounded-md px-2.5 py-1">
                        {src}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex items-start">
              <div className="max-w-xl rounded-xl px-4 py-3 text-sm bg-[var(--surface)] border border-[var(--border)] text-[var(--text-muted)]">
                Searching repos and generating an answer...
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-[var(--border)] px-6 py-4 flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !loading && handleSend()}
            placeholder="Ask about a project..."
            disabled={loading}
            className="flex-1 bg-[var(--surface)] border border-[var(--border)] rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-[var(--accent-blue)] disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="bg-[var(--accent-blue)] text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:opacity-90 disabled:opacity-50"
          >
            {loading ? "..." : "Send"}
          </button>
        </div>
      </main>
    </div>
  );
}
"use client";
import { useState } from "react";

const REPOS = [
  { name: "NeuralLens", tech: "PyTorch" },
  { name: "Picassify", tech: "TensorFlow" },
  { name: "DiabetesDetector", tech: "scikit-learn" },
  { name: "AetherQuant", tech: "XGBoost" },
  { name: "deepfake-detector", tech: "PyTorch" },
  { name: "SentimentSense", tech: "NLP" },
  { name: "PersonalFinanceTracker", tech: "Python" },
  { name: "python-weather-app", tech: "Python" },
  { name: "Python-CurrencyConverter", tech: "Python" },
];

export default function Home() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Ask me anything about Ali's projects - I'll search across his repos and cite what I find.", sources: [] }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeRepos, setActiveRepos] = useState([]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const question = input;
    setMessages(prev => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);
    setActiveRepos([]);

    try {
      const res = await fetch("http://127.0.0.1:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", text: data.answer, sources: data.sources }]);

      const hitRepos = [...new Set(data.sources.map(s => s.split("/")[0]))];
      setActiveRepos(hitRepos);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", text: "Something went wrong reaching the backend. Is it running?", sources: [] }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      <aside className="w-72 border-r border-[var(--border)] bg-[var(--surface)]/60 backdrop-blur-sm p-6 hidden lg:block overflow-y-auto">
        <h2 className="font-display text-xs font-semibold tracking-widest text-[var(--text-muted)] mb-5 uppercase">Indexed Repositories</h2>
        <div className="space-y-2">
          {REPOS.map((repo) => {
            const isActive = activeRepos.includes(repo.name);
            return (
              <div
                key={repo.name}
                className={`relative border rounded-lg px-3 py-2.5 transition-all duration-300 ${
                  isActive
                    ? "border-[var(--accent-amber)] bg-[#FDF3EC]"
                    : "border-[var(--border)] bg-[var(--surface)]"
                }`}
              >
                <span className={`absolute top-0 left-0 w-2 h-2 border-t border-l ${isActive ? "border-[var(--accent-amber)]" : "border-[var(--accent-blue)]/40"}`} />
                <span className={`absolute bottom-0 right-0 w-2 h-2 border-b border-r ${isActive ? "border-[var(--accent-amber)]" : "border-[var(--accent-blue)]/40"}`} />
                <div className="text-sm font-medium text-[var(--text)] flex items-center justify-between">
                  {repo.name}
                  {isActive && <span className="font-mono text-[10px] text-[var(--accent-amber)]">● hit</span>}
                </div>
                <div className="font-mono text-[11px] text-[var(--accent-blue)] mt-0.5">{repo.tech}</div>
              </div>
            );
          })}
        </div>
      </aside>

      <main className="flex-1 flex flex-col min-w-0">
        <header className="border-b border-[var(--border)] bg-[var(--surface)]/60 backdrop-blur-sm px-8 py-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-display text-2xl font-semibold tracking-tight">CodexQuery</h1>
            <p className="text-sm text-[var(--text-muted)] mt-1 font-mono">
              9 repos indexed · 87 chunks · grep-and-generate
            </p>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto px-8 py-8">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((msg, i) => (
              <div key={i} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
                <div className={`max-w-xl rounded-2xl px-5 py-3.5 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-[var(--accent-blue)] text-white"
                    : "bg-[var(--surface)] border border-[var(--border)] shadow-sm"
                }`}>
                  {msg.text}
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="relative mt-2.5 max-w-xl">
                    <div className="absolute -top-2.5 left-5 w-px h-2.5 bg-[var(--accent-amber)]" />
                    <div className="flex flex-wrap gap-2">
                      {msg.sources.map((src, j) => (
                        <span key={j} className="font-mono text-[11px] text-[var(--accent-amber)] bg-[#FDF3EC] border border-[var(--accent-amber)]/25 rounded-md px-2.5 py-1">
                          {src.replace(" (lines ", ":").replace(")", "")}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex items-start">
                <div className="max-w-xl rounded-2xl px-5 py-3.5 text-sm bg-[var(--surface)] border border-[var(--border)] shadow-sm text-[var(--text-muted)]">
                  Searching repos and generating an answer...
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="border-t border-[var(--border)] bg-[var(--surface)]/60 backdrop-blur-sm px-8 py-5">
          <div className="max-w-3xl mx-auto flex gap-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && handleSend()}
              placeholder="Ask about a project..."
              disabled={loading}
              className="flex-1 bg-[var(--surface)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm font-mono focus:outline-none focus:border-[var(--accent-blue)] disabled:opacity-50"
            />
            <button
              onClick={handleSend}
              disabled={loading}
              className="bg-[var(--accent-blue)] text-white px-6 py-3 rounded-xl text-sm font-medium hover:opacity-90 disabled:opacity-50"
            >
              {loading ? "..." : "Send"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
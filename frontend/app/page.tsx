"use client";

import { FormEvent, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [provider, setProvider] = useState("auto");
  const [loading, setLoading] = useState(false);

  async function sendMessage(event: FormEvent) {
    event.preventDefault();
    if (!message.trim() || loading) return;
    setLoading(true);
    setReply("");
    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, provider }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Request failed");
      setReply(`[${data.provider}] ${data.reply}`);
    } catch (error) {
      setReply(error instanceof Error ? error.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 32 }}>
      <h1>21STUDIO AI Agent</h1>
      <p>Multi-provider agent powered by Mistral, Groq, and Cerebras.</p>
      <form onSubmit={sendMessage} style={{ display: "grid", gap: 12, marginTop: 24 }}>
        <select value={provider} onChange={(e) => setProvider(e.target.value)} style={{ padding: 12 }}>
          <option value="auto">Auto</option>
          <option value="mistral">Mistral</option>
          <option value="groq">Groq</option>
          <option value="cerebras">Cerebras</option>
        </select>
        <textarea value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Ask your agent..." rows={7} style={{ padding: 14, resize: "vertical" }} />
        <button type="submit" disabled={loading} style={{ padding: 12 }}>
          {loading ? "Thinking..." : "Send"}
        </button>
      </form>
      {reply && <pre style={{ whiteSpace: "pre-wrap", marginTop: 24, padding: 16, background: "white", border: "1px solid #ddd" }}>{reply}</pre>}
    </main>
  );
}

"use client";

import { FormEvent, useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const CONVERSATION_KEY = "21studio-conversation-id";

export default function Home() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [provider, setProvider] = useState("auto");
  const [conversationId, setConversationId] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const saved = window.localStorage.getItem(CONVERSATION_KEY);
    if (saved) setConversationId(saved);
  }, []);

  async function sendMessage(event: FormEvent) {
    event.preventDefault();
    if (!message.trim() || loading) return;
    setLoading(true);
    setReply("");
    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, provider, conversation_id: conversationId || null }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Request failed");
      setConversationId(data.conversation_id);
      window.localStorage.setItem(CONVERSATION_KEY, data.conversation_id);
      setReply(`[${data.provider}] ${data.reply}`);
      setMessage("");
    } catch (error) {
      setReply(error instanceof Error ? error.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function newConversation() {
    window.localStorage.removeItem(CONVERSATION_KEY);
    setConversationId("");
    setReply("");
    setMessage("");
  }

  async function clearConversation() {
    if (!conversationId) return newConversation();
    try {
      await fetch(`${API_URL}/api/memory/${conversationId}`, { method: "DELETE" });
    } finally {
      newConversation();
    }
  }

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 32 }}>
      <h1>21STUDIO AI Agent</h1>
      <p>Multi-provider agent powered by Mistral, Groq, and Cerebras.</p>
      <p style={{ fontSize: 13, color: "#6b7280" }}>Memory is enabled for this conversation.</p>
      <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <button type="button" onClick={newConversation} style={{ padding: 10 }}>New chat</button>
        <button type="button" onClick={clearConversation} style={{ padding: 10 }} disabled={!conversationId}>Clear memory</button>
      </div>
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

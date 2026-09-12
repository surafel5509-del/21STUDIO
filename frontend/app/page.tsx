"use client";

import { FormEvent, useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const CONVERSATION_KEY = "21studio-conversation-id";

type StreamEvent = {
  type: "token" | "done" | "error";
  content?: string;
  provider?: string;
  conversation_id?: string;
  error?: string;
};

export default function Home() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [provider, setProvider] = useState("auto");
  const [activeProvider, setActiveProvider] = useState("");
  const [conversationId, setConversationId] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const saved = window.localStorage.getItem(CONVERSATION_KEY);
    if (saved) setConversationId(saved);
  }, []);

  async function sendMessage(event: FormEvent) {
    event.preventDefault();
    if (!message.trim() || loading) return;

    const currentMessage = message.trim();
    setLoading(true);
    setReply("");
    setActiveProvider("");

    try {
      const response = await fetch(`${API_URL}/api/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify({
          message: currentMessage,
          provider,
          conversation_id: conversationId || null,
        }),
      });

      if (!response.ok || !response.body) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail ?? "Streaming request failed");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";

        for (const rawEvent of events) {
          const line = rawEvent.split("\n").find((item) => item.startsWith("data: "));
          if (!line) continue;

          const event: StreamEvent = JSON.parse(line.slice(6));
          if (event.type === "token") {
            setReply((current) => current + (event.content ?? ""));
            if (event.provider) setActiveProvider(event.provider);
            if (event.conversation_id) {
              setConversationId(event.conversation_id);
              window.localStorage.setItem(CONVERSATION_KEY, event.conversation_id);
            }
          } else if (event.type === "error") {
            throw new Error(event.error ?? "Agent streaming failed");
          }
        }
      }

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
    setActiveProvider("");
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
      <p style={{ fontSize: 13, color: "#6b7280" }}>
        Memory is enabled for this conversation.
      </p>

      <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <button type="button" onClick={newConversation} style={{ padding: 10 }}>
          New chat
        </button>
        <button type="button" onClick={clearConversation} style={{ padding: 10 }} disabled={!conversationId || loading}>
          Clear memory
        </button>
      </div>

      <form onSubmit={sendMessage} style={{ display: "grid", gap: 12, marginTop: 24 }}>
        <select value={provider} onChange={(e) => setProvider(e.target.value)} style={{ padding: 12 }} disabled={loading}>
          <option value="auto">Auto</option>
          <option value="mistral">Mistral</option>
          <option value="groq">Groq</option>
          <option value="cerebras">Cerebras</option>
        </select>

        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask your agent..."
          rows={7}
          style={{ padding: 14, resize: "vertical" }}
          disabled={loading}
        />

        <button type="submit" disabled={loading || !message.trim()} style={{ padding: 12 }}>
          {loading ? "Streaming..." : "Send"}
        </button>
      </form>

      {(reply || loading) && (
        <section style={{ marginTop: 24, padding: 16, background: "white", border: "1px solid #ddd" }}>
          <div style={{ fontSize: 12, color: "#6b7280", marginBottom: 8 }}>
            {activeProvider ? `Provider: ${activeProvider}` : "Agent"}
            {loading ? " · streaming" : ""}
          </div>
          <pre style={{ whiteSpace: "pre-wrap", margin: 0, fontFamily: "inherit" }}>
            {reply || "Thinking…"}
            {loading && <span aria-hidden="true">▌</span>}
          </pre>
        </section>
      )}
    </main>
  );
}

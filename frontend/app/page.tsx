"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const CONVERSATION_KEY = "21studio-conversation-id";

type StreamEvent = { type: "token" | "done" | "error"; content?: string; provider?: string; conversation_id?: string; error?: string };
type ChatMessage = { role: "user" | "assistant"; content: string; provider?: string };

const providers = [
  { id: "auto", name: "Auto", description: "Smart routing", mark: "✦" },
  { id: "mistral", name: "Mistral", description: "Fast & capable", mark: "M" },
  { id: "groq", name: "Groq", description: "Ultra low latency", mark: "G" },
  { id: "cerebras", name: "Cerebras", description: "High throughput", mark: "C" },
];

const Sparkle = () => <span className="sparkle" aria-hidden="true">✦</span>;

export default function Home() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [provider, setProvider] = useState("auto");
  const [activeProvider, setActiveProvider] = useState("");
  const [conversationId, setConversationId] = useState("");
  const [loading, setLoading] = useState(false);
  const [showProviders, setShowProviders] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const saved = window.localStorage.getItem(CONVERSATION_KEY);
    if (saved) setConversationId(saved);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  function updateDraft(value: string) {
    setMessage(value);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(Math.max(textareaRef.current.scrollHeight, 62), 190)}px`;
    }
  }

  async function sendMessage(event?: FormEvent) {
    event?.preventDefault();
    if (!message.trim() || loading) return;
    const currentMessage = message.trim();
    setLoading(true); setMessage(""); setActiveProvider("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
    setMessages((current) => [...current, { role: "user", content: currentMessage }, { role: "assistant", content: "" }]);

    try {
      const response = await fetch(`${API_URL}/api/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify({ message: currentMessage, provider, conversation_id: conversationId || null }),
      });
      if (!response.ok || !response.body) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail ?? "Streaming request failed");
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      const handleEvent = (raw: string) => {
        const line = raw.split("\n").find((item) => item.startsWith("data: "));
        if (!line) return;
        const event: StreamEvent = JSON.parse(line.slice(6));
        if (event.type === "token") {
          setMessages((current) => {
            const next = [...current]; const last = next[next.length - 1];
            if (last?.role === "assistant") next[next.length - 1] = { ...last, content: last.content + (event.content ?? ""), provider: event.provider };
            return next;
          });
          if (event.provider) setActiveProvider(event.provider);
          if (event.conversation_id) { setConversationId(event.conversation_id); window.localStorage.setItem(CONVERSATION_KEY, event.conversation_id); }
        } else if (event.type === "error") throw new Error(event.error ?? "Agent streaming failed");
      };
      while (true) {
        const { value, done } = await reader.read(); if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n"); buffer = events.pop() ?? "";
        events.forEach(handleEvent);
      }
      if (buffer.trim()) handleEvent(buffer);
    } catch (error) {
      const text = error instanceof Error ? error.message : "Something went wrong";
      setMessages((current) => { const next = [...current]; const last = next[next.length - 1]; if (last?.role === "assistant") next[next.length - 1] = { ...last, content: `Unable to complete the request. ${text}` }; return next; });
    } finally { setLoading(false); }
  }

  function newConversation() {
    window.localStorage.removeItem(CONVERSATION_KEY); setConversationId(""); setMessages([]); setMessage(""); setActiveProvider("");
    requestAnimationFrame(() => textareaRef.current?.focus());
  }

  async function clearConversation() {
    if (!conversationId) return newConversation();
    try { await fetch(`${API_URL}/api/memory/${conversationId}`, { method: "DELETE" }); } finally { newConversation(); }
  }

  const selected = providers.find((item) => item.id === provider) ?? providers[0];

  return (
    <main className="app-shell">
      <div className="ambient ambient-one" /><div className="ambient ambient-two" />
      <header className="topbar">
        <button className="brand" type="button" onClick={newConversation} aria-label="21STUDIO home">
          <span className="brand-mark"><Sparkle /></span><span>21<span className="brand-light">STUDIO</span></span>
        </button>
        <div className="topbar-actions"><span className="status-pill"><span className="status-dot" /> AI online</span><button className="icon-button" type="button" onClick={newConversation} aria-label="New conversation">＋</button></div>
      </header>

      <section className={`workspace ${messages.length ? "has-chat" : ""}`}>
        {messages.length === 0 ? (
          <div className="hero">
            <div className="hero-badge"><Sparkle /> Your intelligent workspace</div>
            <h1>Think bigger.<br /><span>Build with AI.</span></h1>
            <p>One beautiful workspace for research, reasoning, calculation, and getting things done.</p>
            <div className="quick-grid">
              {["Research the web", "Explain a complex idea", "Calculate anything", "Build something new"].map((item, index) => (
                <button key={item} type="button" className="quick-card" onClick={() => updateDraft(item)}><span className={`quick-icon q${index}`}>{["⌁", "◈", "∑", "↗"][index]}</span><span>{item}</span><span className="arrow">↗</span></button>
              ))}
            </div>
          </div>
        ) : (
          <div className="conversation">
            {messages.map((item, index) => (
              <article key={`${index}-${item.role}`} className={`message ${item.role}`}>
                <div className="message-avatar">{item.role === "user" ? "Y" : <Sparkle />}</div>
                <div className="message-body">
                  <div className="message-meta"><span>{item.role === "user" ? "You" : "21STUDIO"}</span>{item.provider && <span className="provider-tag">{item.provider}</span>}</div>
                  <div className="message-content">{item.content || (loading && index === messages.length - 1 ? <span className="thinking"><i /><i /><i /></span> : "")}</div>
                  {item.role === "assistant" && loading && index === messages.length - 1 && <span className="stream-cursor" />}
                </div>
              </article>
            ))}
            <div ref={bottomRef} />
          </div>
        )}

        <div className="composer-wrap">
          <form className="composer" onSubmit={sendMessage}>
            <div className="composer-top"><textarea ref={textareaRef} value={message} onChange={(e) => updateDraft(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); void sendMessage(); } }} placeholder="Ask 21STUDIO anything..." rows={1} disabled={loading} aria-label="Message 21STUDIO" /></div>
            <div className="composer-bottom">
              <div className="composer-tools">
                <div className="provider-picker">
                  <button type="button" className="provider-button" onClick={() => setShowProviders((value) => !value)} disabled={loading}><span className="provider-mark">{selected.mark}</span><span>{selected.name}</span><span className="chevron">⌄</span></button>
                  {showProviders && <div className="provider-menu">{providers.map((item) => <button key={item.id} type="button" className={`provider-option ${provider === item.id ? "selected" : ""}`} onClick={() => { setProvider(item.id); setShowProviders(false); }}><span className="provider-mark">{item.mark}</span><span><strong>{item.name}</strong><small>{item.description}</small></span>{provider === item.id && <span className="check">✓</span>}</button>)}</div>}
                </div>
                <button type="button" className="tool-button" title="Web search is available to the agent">⌁ <span>Web</span></button>
              </div>
              <button className="send-button" type="submit" disabled={loading || !message.trim()} aria-label="Send message">{loading ? <span className="loader" /> : <span>↑</span>}</button>
            </div>
          </form>
          <div className="composer-note"><span>{activeProvider ? `Powered by ${activeProvider}` : "AI can make mistakes. Check important information."}</span>{messages.length > 0 && <button type="button" onClick={clearConversation} disabled={loading}>Clear memory</button>}</div>
        </div>
      </section>
      <footer className="footer"><span>21STUDIO</span><span>Intelligence, beautifully designed.</span></footer>
    </main>
  );
}

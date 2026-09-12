"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "/api";
const CONVERSATION_KEY = "21studio-conversation-id";

type Mode = "chat" | "agent" | "research";
type StreamEvent = { type: "token" | "done" | "error" | "status"; content?: string; provider?: string; conversation_id?: string; error?: string; status?: string; label?: string };
type ChatMessage = { role: "user" | "assistant"; content: string; provider?: string };
type Source = { title: string; url: string };

const providers = [
  { id: "auto", name: "Auto", description: "Smart routing", mark: "✦" },
  { id: "mistral", name: "Mistral", description: "Fast & capable", mark: "M" },
  { id: "groq", name: "Groq", description: "Ultra low latency", mark: "G" },
  { id: "cerebras", name: "Cerebras", description: "High throughput", mark: "C" },
];

const quickTools = [
  ["⌁", "Research", "Compare sources and summarize the latest findings", "research"],
  ["</>", "Code", "Build complete, copy-ready code", "agent"],
  ["◈", "Analyze", "Break down a complex idea clearly", "chat"],
  ["↗", "Create", "Plan and build something from scratch", "agent"],
];

const Sparkle = () => <span className="sparkle" aria-hidden="true">✦</span>;

function extractSources(text: string): Source[] {
  const matches = [...text.matchAll(/(?:\[[^\]]*\]\()?(https?:\/\/[^\s)]+)(?:\))?/g)];
  const seen = new Set<string>();
  return matches.map((m) => m[1].replace(/[.,;]+$/, "")).filter((url) => {
    if (seen.has(url)) return false;
    seen.add(url);
    return true;
  }).slice(0, 6).map((url) => ({ title: new URL(url).hostname.replace(/^www\./, ""), url }));
}

function InlineText({ text }: { text: string }) {
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g);
  return <>{parts.map((part, index) => part.startsWith("**") && part.endsWith("**") ? <strong key={index}>{part.slice(2, -2)}</strong> : part.startsWith("`") && part.endsWith("`") ? <code key={index}>{part.slice(1, -1)}</code> : <span key={index}>{part}</span>)}</>;
}

function MarkdownMessage({ content }: { content: string }) {
  const blocks = content.split(/```([\w+-]*)\n?([\s\S]*?)```/g);
  const nodes: React.ReactNode[] = [];
  for (let i = 0; i < blocks.length; i++) {
    if (i % 3 === 1) {
      const language = blocks[i] || "code";
      const code = blocks[i + 1] ?? "";
      nodes.push(
        <div className="code-card" key={`code-${i}`}>
          <div className="code-head"><span>{language}</span><button type="button" onClick={() => void navigator.clipboard.writeText(code)}><span>□</span> Copy</button></div>
          <pre><code>{code}</code></pre>
        </div>
      );
      i++;
      continue;
    }
    const lines = blocks[i].split("\n");
    let listItems: string[] = [];
    const flushList = (key: string) => { if (listItems.length) { nodes.push(<ul key={key}>{listItems.map((item, j) => <li key={j}><InlineText text={item} /></li>)}</ul>); listItems = []; } };
    lines.forEach((line, j) => {
      if (/^[-*]\s+/.test(line)) { listItems.push(line.replace(/^[-*]\s+/, "")); return; }
      flushList(`list-${i}-${j}`);
      if (/^#{1,3}\s+/.test(line)) nodes.push(<h3 key={`${i}-h-${j}`}>{line.replace(/^#{1,3}\s+/, "")}</h3>);
      else if (/^\d+\.\s+/.test(line)) nodes.push(<p className="numbered" key={`${i}-n-${j}`}><span>{line.match(/^\d+/)?.[0]}.</span><InlineText text={line.replace(/^\d+\.\s+/, "")} /></p>);
      else if (line.trim()) nodes.push(<p key={`${i}-p-${j}`}><InlineText text={line}</InlineText></p>);
    });
    flushList(`list-${i}-end`);
  }
  return <div className="rich-text">{nodes}</div>;
}

export default function Home() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [provider, setProvider] = useState("auto");
  const [activeProvider, setActiveProvider] = useState("");
  const [conversationId, setConversationId] = useState("");
  const [mode, setMode] = useState<Mode>("chat");
  const [thinking, setThinking] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [showProviders, setShowProviders] = useState(false);
  const [showTools, setShowTools] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { const saved = window.localStorage.getItem(CONVERSATION_KEY); if (saved) setConversationId(saved); }, []);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" }); }, [messages, loading]);

  const sources = useMemo(() => extractSources(messages.filter((m) => m.role === "assistant").at(-1)?.content ?? ""), [messages]);
  const selected = providers.find((item) => item.id === provider) ?? providers[0];

  function updateDraft(value: string) {
    setMessage(value);
    if (textareaRef.current) { textareaRef.current.style.height = "auto"; textareaRef.current.style.height = `${Math.min(Math.max(textareaRef.current.scrollHeight, 62), 190)}px`; }
  }

  async function sendMessage(event?: FormEvent) {
    event?.preventDefault();
    if (!message.trim() || loading) return;
    const currentMessage = message.trim();
    setLoading(true); setMessage(""); setActiveProvider(""); setStatus(thinking ? "Thinking carefully…" : mode === "research" ? "Searching sources…" : "Generating…");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
    setMessages((current) => [...current, { role: "user", content: currentMessage }, { role: "assistant", content: "" }]);
    try {
      const response = await fetch(`${API_URL}/chat/stream`, { method: "POST", headers: { "Content-Type": "application/json", Accept: "text/event-stream" }, body: JSON.stringify({ message: currentMessage, provider, conversation_id: conversationId || null, mode, thinking_mode: thinking }) });
      if (!response.ok || !response.body) { const data = await response.json().catch(() => ({})); throw new Error(data.detail ?? "Streaming request failed"); }
      const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = "";
      const handleEvent = (raw: string) => {
        const line = raw.split("\n").find((item) => item.startsWith("data: ")); if (!line) return;
        const event: StreamEvent = JSON.parse(line.slice(6));
        if (event.type === "status") { setStatus(event.label ?? (event.status === "thinking" ? "Thinking…" : "Working…")); return; }
        if (event.type === "token") {
          setMessages((current) => { const next = [...current]; const last = next[next.length - 1]; if (last?.role === "assistant") next[next.length - 1] = { ...last, content: last.content + (event.content ?? ""), provider: event.provider }; return next; });
          if (event.provider) setActiveProvider(event.provider);
          if (event.conversation_id) { setConversationId(event.conversation_id); window.localStorage.setItem(CONVERSATION_KEY, event.conversation_id); }
          setStatus(mode === "research" ? "Analyzing findings…" : "Writing…");
        } else if (event.type === "error") throw new Error(event.error ?? "Agent streaming failed");
      };
      while (true) { const { value, done } = await reader.read(); if (done) break; buffer += decoder.decode(value, { stream: true }); const events = buffer.split("\n\n"); buffer = events.pop() ?? ""; events.forEach(handleEvent); }
      if (buffer.trim()) handleEvent(buffer);
    } catch (error) {
      const text = error instanceof Error ? error.message : "Something went wrong";
      setMessages((current) => { const next = [...current]; const last = next[next.length - 1]; if (last?.role === "assistant") next[next.length - 1] = { ...last, content: `Unable to complete the request. ${text}` }; return next; });
    } finally { setLoading(false); setStatus(""); }
  }

  function newConversation() { window.localStorage.removeItem(CONVERSATION_KEY); setConversationId(""); setMessages([]); setMessage(""); setActiveProvider(""); setStatus(""); requestAnimationFrame(() => textareaRef.current?.focus()); }
  async function clearConversation() { if (!conversationId) return newConversation(); try { await fetch(`${API_URL}/memory/${conversationId}`, { method: "DELETE" }); } finally { newConversation(); } }

  return (
    <main className="app-shell">
      <div className="ambient ambient-one" /><div className="ambient ambient-two" />
      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="side-brand"><span className="brand-mark"><Sparkle /></span><b>21<span>STUDIO</span></b></div>
        <button className="new-chat" type="button" onClick={newConversation}>＋ <span>New workspace</span></button>
        <div className="side-section"><small>WORKSPACE</small><button className={mode === "chat" ? "active" : ""} onClick={() => setMode("chat")}>◌ <span>Chat</span></button><button className={mode === "agent" ? "active" : ""} onClick={() => setMode("agent")}>✦ <span>Agent</span></button><button className={mode === "research" ? "active" : ""} onClick={() => setMode("research")}>⌁ <span>Research</span></button></div>
        <div className="side-section"><small>TOOLS</small><button onClick={() => { setMode("research"); updateDraft("Research the latest information about "); }}>⌕ <span>Web research</span></button><button onClick={() => { setMode("agent"); updateDraft("Build this for me: "); }}>▣ <span>Build & code</span></button><button onClick={() => updateDraft("Analyze this: ")}>◈ <span>Analyze</span></button></div>
        <div className="side-bottom"><button onClick={clearConversation}>⌫ <span>Clear memory</span></button><div className="side-user"><span>SS</span><div><b>21STUDIO</b><small>AI workspace</small></div></div></div>
      </aside>
      <button className="mobile-menu" onClick={() => setSidebarOpen((v) => !v)} aria-label="Open menu">☰</button>
      <section className="main-panel">
        <header className="topbar">
          <button className="brand" type="button" onClick={newConversation}><span className="brand-mark"><Sparkle /></span><span>21<span className="brand-light">STUDIO</span></span></button>
          <div className="mode-switch">{(["chat", "agent", "research"] as Mode[]).map((item) => <button key={item} className={mode === item ? "selected" : ""} onClick={() => setMode(item)}>{item === "chat" ? "Chat" : item === "agent" ? "Agent" : "Research"}</button>)}</div>
          <div className="topbar-actions"><span className="status-pill"><span className="status-dot" /> AI online</span><button className="icon-button" type="button" onClick={newConversation}>＋</button></div>
        </header>

        <section className={`workspace ${messages.length ? "has-chat" : ""}`}>
          {messages.length === 0 ? <div className="hero">
            <div className="hero-badge"><Sparkle /> Professional AI workspace</div>
            <h1>Think clearly.<br /><span>Build boldly.</span></h1>
            <p>Research, reason, code, analyze, and create from one intelligent workspace.</p>
            <div className="quick-grid">{quickTools.map(([icon, title, desc, nextMode]) => <button key={title} type="button" className="quick-card" onClick={() => { setMode(nextMode as Mode); updateDraft(title === "Code" ? "Build this for me: " : title === "Research" ? "Research the latest information about " : `${title}: `); }}><span className="quick-icon">{icon}</span><span><b>{title}</b><small>{desc}</small></span><span className="arrow">↗</span></button>)}</div>
          </div> : <div className="conversation">
            {messages.map((item, index) => <article key={`${index}-${item.role}`} className={`message ${item.role}`}>
              <div className="message-avatar">{item.role === "user" ? "SS" : <Sparkle />}</div>
              <div className="message-body"><div className="message-meta"><span>{item.role === "user" ? "You" : "21STUDIO"}</span>{item.provider && <span className="provider-tag">{item.provider}</span>}</div>
                <div className="message-content">{item.content ? item.role === "assistant" ? <MarkdownMessage content={item.content} /> : <p>{item.content}</p> : loading && index === messages.length - 1 ? <div className="thinking-box"><span className="thinking-orb">✦</span><div><b>{status || "Thinking…"}</b><small>{mode === "research" ? "Searching, comparing and synthesizing sources" : thinking ? "Reasoning carefully before responding" : "Generating a clear response"}</small></div></div> : ""}</div>
                {item.role === "assistant" && loading && index === messages.length - 1 && <span className="stream-cursor" />}
              </div>
            </article>)}
            {mode === "research" && !loading && sources.length > 0 && <div className="sources-panel"><div className="sources-title"><span>⌁</span><div><b>Sources</b><small>References used in this response</small></div></div><div className="source-grid">{sources.map((source) => <a key={source.url} href={source.url} target="_blank" rel="noreferrer"><span className="favicon">{source.title.slice(0, 1).toUpperCase()}</span><span><b>{source.title}</b><small>{source.url}</small></span><span>↗</span></a>)}</div></div>}
            <div ref={bottomRef} />
          </div>}

          <div className="composer-wrap"><form className="composer" onSubmit={sendMessage}>
            <div className="composer-top"><textarea ref={textareaRef} value={message} onChange={(e) => updateDraft(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); void sendMessage(); } }} placeholder={mode === "research" ? "What should I research?" : mode === "agent" ? "Tell the agent what to build or do…" : "Ask 21STUDIO anything…"} rows={1} disabled={loading} />
            </div>
            <div className="composer-bottom"><div className="composer-tools">
              <div className="provider-picker"><button type="button" className="provider-button" onClick={() => setShowProviders((v) => !v)} disabled={loading}><span className="provider-mark">{selected.mark}</span><span>{selected.name}</span><span className="chevron">⌄</span></button>{showProviders && <div className="provider-menu">{providers.map((item) => <button key={item.id} type="button" className={`provider-option ${provider === item.id ? "selected" : ""}`} onClick={() => { setProvider(item.id); setShowProviders(false); }}><span className="provider-mark">{item.mark}</span><span><strong>{item.name}</strong><small>{item.description}</small></span>{provider === item.id && <span className="check">✓</span>}</button>)}</div>}</div>
              <button type="button" className={`tool-button ${mode === "research" ? "on" : ""}`} onClick={() => setMode("research")}>⌁ <span>Research</span></button>
              <button type="button" className={`tool-button ${thinking ? "on" : ""}`} onClick={() => setThinking((v) => !v)}>◈ <span>Thinking</span></button>
              <button type="button" className="tool-button more-tools" onClick={() => setShowTools((v) => !v)}>＋ <span>Tools</span></button>
              {showTools && <div className="tools-pop"><button onClick={() => { setMode("agent"); updateDraft("Build a complete solution for: "); setShowTools(false); }}>▣ Code builder</button><button onClick={() => { updateDraft("Analyze and compare: "); setShowTools(false); }}>◈ Deep analyze</button><button onClick={() => { setMode("research"); updateDraft("Research and cite sources for: "); setShowTools(false); }}>⌕ Source finder</button></div>}
            </div><button className="send-button" type="submit" disabled={loading || !message.trim()} aria-label="Send">{loading ? <span className="loader" /> : <span>↑</span>}</button></div>
          </form><div className="composer-note"><span>{activeProvider ? `Powered by ${activeProvider}` : `${mode[0].toUpperCase()}${mode.slice(1)} mode${thinking ? " · Thinking enabled" : ""}`}</span>{messages.length > 0 && <button type="button" onClick={clearConversation} disabled={loading}>Clear memory</button>}</div></div>
        </section>
        <footer className="footer"><span>21STUDIO</span><span>Intelligence, beautifully designed.</span></footer>
      </section>
    </main>
  );
}

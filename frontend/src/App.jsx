import { useState, useRef, useEffect } from "react";
import MessageBubble from "./components/MessageBubble";
import TypingIndicator from "./components/TypingIndicator";
import "./App.css";

// Where our FastAPI backend lives. Read from a Vite env var so we can change
// it for production without editing code; fall back to the local dev server.
const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

// A few example prompts shown on the empty screen.
const SUGGESTIONS = [
  "Explain recursion like I'm 10",
  "Give me 3 FastAPI tips",
  "Write a haiku about the ocean",
];

export default function App() {
  // messages = the full conversation, each { role, text }.
  const [messages, setMessages] = useState([]);
  // input = whatever the user is currently typing.
  const [input, setInput] = useState("");
  // loading = true while we wait for the backend to answer.
  const [loading, setLoading] = useState(false);
  // sessionId ties all our messages into ONE conversation on the backend so it
  // can remember context. We generate it once (lazy initializer) when the app
  // loads; "New Chat" replaces it with a fresh id to start a clean conversation.
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID());

  // A ref to the bottom of the message list so we can auto-scroll to it.
  const bottomRef = useRef(null);

  // Every time messages change (or loading toggles), scroll to the newest one.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // sendMessage does the actual work: show the user's message, call the API,
  // then show the assistant's reply (or an error).
  async function sendMessage(text) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    // 1. Immediately add the user's message to the screen.
    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setInput("");
    setLoading(true);

    try {
      // 2. POST the message AND the session id, so the backend knows which
      //    conversation this belongs to and can include its history.
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, session_id: sessionId }),
      });

      if (!res.ok) {
        // The server responded, but with an error status (e.g. 502, 422).
        throw new Error(`Server responded with ${res.status}`);
      }

      // 3. Parse the JSON { "response": "..." } and show it.
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.response },
      ]);
    } catch (err) {
      // Network failure, backend down, or the error thrown above.
      setMessages((prev) => [
        ...prev,
        {
          role: "error",
          text:
            "Couldn't reach the assistant. Is the backend running? " +
            `(${err.message})`,
        },
      ]);
    } finally {
      // 4. Whatever happened, stop the loading indicator.
      setLoading(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault(); // stop the browser from reloading the page on submit
    sendMessage(input);
  }

  // Start a fresh conversation: clear the screen AND get a new session id, so
  // the backend treats the next message as a brand-new chat with no memory.
  function startNewChat() {
    setMessages([]);
    setSessionId(crypto.randomUUID());
  }

  const isEmpty = messages.length === 0;

  return (
    <div className="app">
      <div className="chat">
        {/* Header / brand */}
        <header className="chat-header">
          <div className="brand-mark">✦</div>
          <div className="brand-text">
            <h1>AURUM AI</h1>
            <div className="subtitle">
              <span className="status-dot"></span>
              Powered by Google Gemini
            </div>
          </div>
          {/* New Chat resets the conversation (and its memory) */}
          <button
            className="new-chat-btn"
            onClick={startNewChat}
            disabled={loading || messages.length === 0}
          >
            New Chat
          </button>
        </header>

        {/* Message list */}
        <div className="messages">
          {isEmpty ? (
            <div className="welcome">
              <div className="big-mark">✦</div>
              <h2>How can I help you today?</h2>
              <p>Ask anything — AURUM is powered by Google Gemini.</p>
              <div className="suggestions">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    className="chip"
                    onClick={() => sendMessage(s)}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((m, i) => (
              <MessageBubble key={i} role={m.role} text={m.text} />
            ))
          )}

          {/* Show the typing dots while waiting for a reply */}
          {loading && <TypingIndicator />}

          {/* Invisible anchor we scroll to */}
          <div ref={bottomRef} />
        </div>

        {/* Input bar */}
        <form className="composer" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Type your message…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="send-btn"
            disabled={loading || !input.trim()}
            aria-label="Send message"
          >
            {/* Simple paper-plane arrow */}
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M3 20l18-8L3 4v6l12 2-12 2v6z"
                fill="currentColor"
              />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}

/**
 * MessageBubble — renders a single chat message.
 *
 * Props:
 *   role: "user" | "assistant" | "error"
 *   text: the message content
 *
 * The `role` decides the styling (alignment, colour, avatar) via CSS classes.
 */
export default function MessageBubble({ role, text }) {
  // Pick the little avatar glyph based on who is speaking.
  const avatar = role === "user" ? "You" : role === "error" ? "!" : "✦";

  return (
    <div className={`msg ${role}`}>
      <div className="avatar">{avatar}</div>
      <div className="bubble">{text}</div>
    </div>
  );
}

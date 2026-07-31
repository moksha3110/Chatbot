/**
 * TypingIndicator — the three bouncing gold dots shown inside an assistant
 * bubble while we wait for Gemini to respond. Purely visual (no props).
 */
export default function TypingIndicator() {
  return (
    <div className="msg assistant">
      <div className="avatar">✦</div>
      <div className="bubble">
        <div className="typing">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
}

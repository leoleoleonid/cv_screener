import React from 'react';

type ChatEntry = {
  role: 'user' | 'assistant';
  text: string;
};

type ChatPanelProps = {
  chatInput: string;
  chatHistory: ChatEntry[];
  chatStatus: 'idle' | 'sending' | 'error';
  chatError: string | null;
  onInputChange: (value: string) => void;
  onSubmit: (event: React.FormEvent) => void;
};

export function ChatPanel({
  chatInput,
  chatHistory,
  chatStatus,
  chatError,
  onInputChange,
  onSubmit,
}: ChatPanelProps) {
  return (
    <section className="card chat-card">
      <div className="card-header">
        <h2>Chat with RAG</h2>
        <p>Ask questions answered using the indexed CV corpus.</p>
      </div>
      <form className="chat-form" onSubmit={onSubmit}>
        <input
          type="text"
          value={chatInput}
          onChange={(e) => onInputChange(e.target.value)}
          placeholder="Ask about skills, experience, availability…"
        />
        <button
          type="submit"
          className="btn btn-primary"
          disabled={chatStatus === 'sending'}
        >
          {chatStatus === 'sending' ? 'Sending…' : 'Send'}
        </button>
      </form>
      {chatError && <span className="status-text error">{chatError}</span>}
      <div className="chat-history">
        {chatHistory.length === 0 ? (
          <p className="status-text muted">No messages yet.</p>
        ) : (
          chatHistory.map((entry, index) => (
            <div
              key={`${entry.role}-${index}`}
              className={`chat-message ${entry.role}`}
            >
              <strong>{entry.role === 'user' ? 'You' : 'Assistant'}</strong>
              <p>{entry.text}</p>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

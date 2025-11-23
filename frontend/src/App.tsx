import React, { useEffect, useState } from 'react';
import './App.css';

const App: React.FC = () => {
  const [backendStatus, setBackendStatus] = useState<string>('Checking backend…');
  const [files, setFiles] = useState<string[]>([]);
  const [filesStatus, setFilesStatus] = useState<
    'idle' | 'loading' | 'loaded' | 'error'
  >('idle');
  const [filesError, setFilesError] = useState<string | null>(null);
  const [chatInput, setChatInput] = useState<string>('');
  const [chatHistory, setChatHistory] = useState<
    { role: 'user' | 'assistant'; text: string }[]
  >([]);
  const [chatStatus, setChatStatus] = useState<'idle' | 'sending' | 'error'>(
    'idle'
  );
  const [chatError, setChatError] = useState<string | null>(null);
  const [generateStatus, setGenerateStatus] = useState<
    'idle' | 'loading' | 'error' | 'success'
  >('idle');
  const [generateMessage, setGenerateMessage] = useState<string | null>(null);
  const [mockGenerateStatus, setMockGenerateStatus] = useState<
    'idle' | 'loading' | 'error' | 'success'
  >('idle');
  const [mockGenerateMessage, setMockGenerateMessage] = useState<string | null>(
    null
  );
  const [ingestStatus, setIngestStatus] = useState<
    'idle' | 'loading' | 'error' | 'success'
  >('idle');
  const [ingestMessage, setIngestMessage] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then((res) => res.json())
      .then((data) => setBackendStatus(data.message ?? 'Backend online'))
      .catch((err) => setBackendStatus('Backend unavailable: ' + err.message));
  }, []);

  useEffect(() => {
    fetchCvFiles();
  }, []);

  const fetchCvFiles = () => {
    setFilesStatus('loading');
    setFilesError(null);
    fetch('http://localhost:8000/cv')
      .then((res) => {
        if (!res.ok) {
          throw new Error('Failed to load CV files');
        }
        return res.json();
      })
      .then((data) => {
        setFiles(data.files ?? []);
        setFilesStatus('loaded');
      })
      .catch((err) => {
        setFilesStatus('error');
        setFilesError(err.message);
      });
  };

  const handleChatSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!chatInput.trim()) {
      return;
    }

    const userMessage = chatInput.trim();
    setChatHistory((prev) => [...prev, { role: 'user', text: userMessage }]);
    setChatInput('');
    setChatStatus('sending');
    setChatError(null);

    fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: userMessage }),
    })
      .then((res) => {
        if (!res.ok) {
          return res
            .json()
            .catch(() => ({}))
            .then((body) => {
              const detail =
                typeof body?.detail === 'string'
                  ? body.detail
                  : 'Failed to send chat message';
              throw new Error(detail);
            });
        }
        return res.json();
      })
      .then((data) => {
        setChatHistory((prev) => [
          ...prev,
          { role: 'assistant', text: data.response ?? 'No response' },
        ]);
        setChatStatus('idle');
      })
      .catch((err) => {
        setChatStatus('error');
        setChatError(err.message);
      });
  };

  const generateCvFile = () => {
    setGenerateStatus('loading');
    setGenerateMessage(null);
    fetch('http://localhost:8000/cv/generate', {
      method: 'POST',
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error('Failed to generate CV');
        }
        return res.json();
      })
      .then((data) => {
        setGenerateStatus('success');
        setGenerateMessage(data.message ?? 'Generated new CV');
        fetchCvFiles();
      })
      .catch((err) => {
        setGenerateStatus('error');
        setGenerateMessage(err.message);
      });
  };

  const generateMockCvFile = () => {
    setMockGenerateStatus('loading');
    setMockGenerateMessage(null);
    fetch('http://localhost:8000/cv/generate-mock', {
      method: 'POST',
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error('Failed to generate mock CV');
        }
        return res.json();
      })
      .then((data) => {
        setMockGenerateStatus('success');
        setMockGenerateMessage(data.message ?? 'Generated mock CV');
        fetchCvFiles();
      })
      .catch((err) => {
        setMockGenerateStatus('error');
        setMockGenerateMessage(err.message);
      });
  };

  const ingestRagIndex = () => {
    setIngestStatus('loading');
    setIngestMessage(null);
    fetch('http://localhost:8000/rag/ingest', { method: 'POST' })
      .then((res) => {
        if (!res.ok) {
          return res
            .json()
            .catch(() => ({}))
            .then((body) => {
              const detail =
                typeof body?.detail === 'string'
                  ? body.detail
                  : 'Failed to ingest CVs';
              throw new Error(detail);
            });
        }
        return res.json();
      })
      .then((data) => {
        const count =
          typeof data?.documents === 'number' ? data.documents : undefined;
        setIngestStatus('success');
        setIngestMessage(
          count !== undefined
            ? `Ingested ${count} CV${count === 1 ? '' : 's'} into RAG index.`
            : 'RAG index rebuilt.'
        );
      })
      .catch((err) => {
        setIngestStatus('error');
        setIngestMessage(err.message);
      });
  };

  return (
    <div className="app-shell">
      <header className="app-hero">
        <p className="hero-pill">AI CV Screener</p>
        <h1>Generate polished CVs & chat with your candidate corpus</h1>
        <p className="hero-subtitle">
          {backendStatus || 'Backend status unavailable'}
        </p>
        <div className="hero-actions">
          <button
            className="btn btn-primary"
            onClick={generateCvFile}
            disabled={generateStatus === 'loading'}
          >
            {generateStatus === 'loading' ? 'Generating…' : 'Generate CV'}
          </button>
          <button
            className="btn btn-secondary"
            onClick={generateMockCvFile}
            disabled={mockGenerateStatus === 'loading'}
          >
            {mockGenerateStatus === 'loading' ? 'Mocking…' : 'Mock CV'}
          </button>
        </div>
        {(generateMessage || mockGenerateMessage) && (
          <div className="hero-feedback">
            {generateMessage && (
              <span
                className={`status-text ${
                  generateStatus === 'error' ? 'error' : 'success'
                }`}
              >
                {generateMessage}
              </span>
            )}
            {mockGenerateMessage && (
              <span
                className={`status-text ${
                  mockGenerateStatus === 'error' ? 'error' : 'success'
                }`}
              >
                {mockGenerateMessage}
              </span>
            )}
          </div>
        )}
      </header>

      <main className="content-stack">
        <div className="chat-stack">
          <section className="card rag-card">
            <div>
              <p className="rag-label">RAG Maintenance</p>
              <p className="rag-description">
                Rebuild the FAISS index when CVs change so chat stays in sync.
              </p>
            </div>
            <div className="rag-actions">
              <button
                className="btn btn-secondary"
                onClick={ingestRagIndex}
                disabled={ingestStatus === 'loading'}
              >
                {ingestStatus === 'loading' ? 'Ingesting…' : 'Ingest CV PDFs'}
              </button>
              {ingestMessage && (
                <span
                  className={`status-text ${
                    ingestStatus === 'error' ? 'error' : 'success'
                  }`}
                >
                  {ingestMessage}
                </span>
              )}
            </div>
          </section>

          <section className="card chat-card">
            <div className="card-header">
              <h2>Chat with RAG</h2>
              <p>Ask questions answered using the indexed CV corpus.</p>
            </div>
            <form className="chat-form" onSubmit={handleChatSubmit}>
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
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
        </div>

        <section className="card cv-card">
          <div className="card-header">
            <h2>CV Library</h2>
            <p>Browse generated PDFs and open them directly from storage.</p>
          </div>
          <div className="card-actions">
            <button
              className="btn btn-ghost"
              onClick={fetchCvFiles}
              disabled={filesStatus === 'loading'}
            >
              {filesStatus === 'loading' ? 'Refreshing…' : 'Refresh list'}
            </button>
            {filesStatus === 'error' && filesError && (
              <span className="status-text error">{filesError}</span>
            )}
            {filesStatus === 'loaded' && files.length === 0 && (
              <span className="status-text muted">
                No static CVs were found. Generate one above.
              </span>
            )}
          </div>
          {files.length > 0 && (
            <ul className="file-grid">
              {files.map((file) => (
                <li key={file}>
                  <a
                    href={`http://localhost:8000/static/${encodeURIComponent(file)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {file}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
};

export default App;

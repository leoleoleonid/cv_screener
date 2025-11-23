import React, { useEffect, useState } from 'react';

const App: React.FC = () => {
  const [text, setText] = useState<string>('Loading...');
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
  const [cvTexts, setCvTexts] = useState<Record<string, string>>({});
  const [cvTextsStatus, setCvTextsStatus] = useState<
    'idle' | 'loading' | 'loaded' | 'error'
  >('idle');
  const [cvTextsError, setCvTextsError] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then((res) => res.json())
      .then((data) => setText(data.message))
      .catch((err) => setText('Error: ' + err.message));
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

  const fetchCvTexts = () => {
    setCvTextsStatus('loading');
    setCvTextsError(null);
    fetch('http://localhost:8000/cv/texts')
      .then((res) => {
        if (!res.ok) {
          throw new Error('Failed to fetch CV texts');
        }
        return res.json();
      })
      .then((data) => {
        const sanitized: Record<string, string> = {};
        if (data && typeof data === 'object') {
          Object.entries(data as Record<string, unknown>).forEach(
            ([filename, value]) => {
              sanitized[filename] = typeof value === 'string' ? value : '';
            }
          );
        }
        setCvTexts(sanitized);
        setCvTextsStatus('loaded');
      })
      .catch((err) => {
        setCvTextsStatus('error');
        setCvTextsError(err.message);
      });
  };

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '2rem' }}>
      <h1>AI CV Screener – Smoke Test</h1>
      <p>Backend says:</p>
      <pre>{text}</pre>
      <div style={{ marginTop: '2rem' }}>
        <button onClick={fetchCvFiles} disabled={filesStatus === 'loading'}>
          {filesStatus === 'loading' ? 'Loading…' : 'Load CV files'}
        </button>
        {filesStatus === 'error' && filesError && (
          <p style={{ color: 'red' }}>Error: {filesError}</p>
        )}
        {filesStatus === 'loaded' && files.length === 0 && (
          <p>No static files were found.</p>
        )}
        {files.length > 0 && (
          <ul>
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
        <div style={{ marginTop: '1rem' }}>
          <button onClick={generateCvFile} disabled={generateStatus === 'loading'}>
            {generateStatus === 'loading' ? 'Generating…' : 'Generate new CV'}
          </button>
          {generateMessage && (
            <p
              style={{
                color: generateStatus === 'error' ? 'red' : 'green',
                marginTop: '0.5rem',
              }}
            >
              {generateMessage}
            </p>
          )}
        </div>
        <div style={{ marginTop: '0.5rem' }}>
          <button
            onClick={generateMockCvFile}
            disabled={mockGenerateStatus === 'loading'}
          >
            {mockGenerateStatus === 'loading'
              ? 'Generating mock…'
              : 'Generate mock CV'}
          </button>
          {mockGenerateMessage && (
            <p
              style={{
                color: mockGenerateStatus === 'error' ? 'red' : 'green',
                marginTop: '0.5rem',
              }}
            >
              {mockGenerateMessage}
            </p>
          )}
        </div>
      </div>
      <div style={{ marginTop: '2rem' }}>
        <h2>Chat Demo</h2>
        <form onSubmit={handleChatSubmit} style={{ marginBottom: '1rem' }}>
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="Type your message"
            style={{ width: '60%', marginRight: '0.5rem' }}
          />
          <button type="submit" disabled={chatStatus === 'sending'}>
            {chatStatus === 'sending' ? 'Sending…' : 'Send'}
          </button>
        </form>
        {chatError && <p style={{ color: 'red' }}>Error: {chatError}</p>}
        {chatHistory.length === 0 ? (
          <p>No messages yet.</p>
        ) : (
          <ul>
            {chatHistory.map((entry, index) => (
              <li key={`${entry.role}-${index}`}>
                <strong>{entry.role === 'user' ? 'You' : 'Assistant'}:</strong>{' '}
                {entry.text}
              </li>
            ))}
          </ul>
        )}
      </div>
      <div style={{ marginTop: '2rem' }}>
        <h2>RAG Controls</h2>
        <button onClick={ingestRagIndex} disabled={ingestStatus === 'loading'}>
          {ingestStatus === 'loading' ? 'Ingesting…' : 'Ingest CV PDFs'}
        </button>
        {ingestMessage && (
          <p
            style={{
              color: ingestStatus === 'error' ? 'red' : 'green',
              marginTop: '0.5rem',
            }}
          >
            {ingestMessage}
          </p>
        )}
      </div>
      <div style={{ marginTop: '2rem' }}>
        <h2>CV Text Extraction</h2>
        <button onClick={fetchCvTexts} disabled={cvTextsStatus === 'loading'}>
          {cvTextsStatus === 'loading' ? 'Fetching…' : 'Get text from CV PDFs'}
        </button>
        {cvTextsStatus === 'error' && cvTextsError && (
          <p style={{ color: 'red' }}>Error: {cvTextsError}</p>
        )}
        {cvTextsStatus === 'loaded' && Object.keys(cvTexts).length === 0 && (
          <p>No PDF files with extractable text were found.</p>
        )}
        {Object.keys(cvTexts).length > 0 && (
          <div style={{ marginTop: '1rem' }}>
            {Object.entries(cvTexts).map(([filename, content]) => (
              <details key={filename} style={{ marginBottom: '0.5rem' }}>
                <summary>{filename}</summary>
                <pre
                  style={{
                    whiteSpace: 'pre-wrap',
                    background: '#f5f5f5',
                    padding: '0.5rem',
                  }}
                >
                  {content || '[No text extracted]'}
                </pre>
              </details>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;

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

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then((res) => res.json())
      .then((data) => setText(data.message))
      .catch((err) => setText('Error: ' + err.message));
  }, []);

  const fetchStaticFiles = () => {
    setFilesStatus('loading');
    setFilesError(null);
    fetch('http://localhost:8000/static-files')
      .then((res) => {
        if (!res.ok) {
          throw new Error('Failed to load static files');
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
          throw new Error('Failed to send chat message');
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

  const generateStaticFile = () => {
    setGenerateStatus('loading');
    setGenerateMessage(null);
    fetch('http://localhost:8000/static-files/generate', {
      method: 'POST',
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error('Failed to generate file');
        }
        return res.json();
      })
      .then((data) => {
        setGenerateStatus('success');
        setGenerateMessage(data.message ?? 'Generated new file');
        fetchStaticFiles();
      })
      .catch((err) => {
        setGenerateStatus('error');
        setGenerateMessage(err.message);
      });
  };

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '2rem' }}>
      <h1>AI CV Screener – Smoke Test</h1>
      <p>Backend says:</p>
      <pre>{text}</pre>
      <div style={{ marginTop: '2rem' }}>
        <button onClick={fetchStaticFiles} disabled={filesStatus === 'loading'}>
          {filesStatus === 'loading' ? 'Loading…' : 'Load static files'}
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
          <button onClick={generateStaticFile} disabled={generateStatus === 'loading'}>
            {generateStatus === 'loading' ? 'Generating…' : 'Generate new PDF'}
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
    </div>
  );
};

export default App;

import React, { useEffect, useState } from 'react';
import './App.css';
import { HeroSection } from './components/HeroSection';
import { RagControls } from './components/RagControls';
import { ChatPanel } from './components/ChatPanel';
import { CvLibrary } from './components/CvLibrary';
import { apiGet, apiPost } from './lib/api';

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
    apiGet<{ message?: string }>('/health')
      .then((data) => setBackendStatus(data.message ?? 'Backend online'))
      .catch((err) => setBackendStatus('Backend unavailable: ' + err.message));
  }, []);

  useEffect(() => {
    fetchCvFiles();
  }, []);

  const fetchCvFiles = () => {
    setFilesStatus('loading');
    setFilesError(null);
    apiGet<{ files?: string[] }>('/cv')
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

    apiPost<{ response?: string }>('/chat', { message: userMessage })
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
    apiPost<{ message?: string }>('/cv/generate')
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
    apiPost<{ message?: string }>('/cv/generate-mock')
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
    apiPost<{ documents?: number }>('/rag/ingest')
      .then((data) => {
        const count = typeof data?.documents === 'number' ? data.documents : undefined;
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
      <HeroSection
        backendStatus={backendStatus}
        generateStatus={generateStatus}
        generateMessage={generateMessage}
        mockStatus={mockGenerateStatus}
        mockMessage={mockGenerateMessage}
        onGenerateCv={generateCvFile}
        onGenerateMock={generateMockCvFile}
      />

      <main className="content-stack">
        <div className="chat-stack">
          <RagControls
            ingestStatus={ingestStatus}
            ingestMessage={ingestMessage}
            onIngest={ingestRagIndex}
          />

          <ChatPanel
            chatInput={chatInput}
            chatHistory={chatHistory}
            chatStatus={chatStatus}
            chatError={chatError}
            onInputChange={setChatInput}
            onSubmit={handleChatSubmit}
          />
        </div>

        <CvLibrary
          files={files}
          status={filesStatus}
          error={filesError}
          onRefresh={fetchCvFiles}
        />
      </main>
    </div>
  );
};

export default App;

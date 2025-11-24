import React, { useEffect, useState } from 'react';
import './App.css';
import { HeroSection } from './components/HeroSection';
import { RagControls } from './components/RagControls';
import { ChatPanel } from './components/ChatPanel';
import { CvLibrary } from './components/CvLibrary';
import { apiGet, apiPost } from './lib/api';

type TaskStatus = {
  task_id: string;
  status: string;
  result?: Record<string, unknown>;
  error?: string | null;
};

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
    apiPost<{ task_id: string; status: string }>('/cv/generate')
      .then((data) => {
        setGenerateMessage('CV generation queued…');
        pollTask(data.task_id, (result) => {
          setGenerateStatus('success');
          const message =
            typeof result?.message === 'string'
              ? result.message
              : 'Generated new CV';
          setGenerateMessage(message);
          fetchCvFiles();
        }, (errorMessage) => {
          setGenerateStatus('error');
          setGenerateMessage(errorMessage);
        });
      })
      .catch((err) => {
        setGenerateStatus('error');
        setGenerateMessage(err.message);
      });
  };

  const generateMockCvFile = () => {
    setMockGenerateStatus('loading');
    setMockGenerateMessage(null);
    apiPost<{ task_id: string; status: string }>('/cv/generate-mock')
      .then((data) => {
        setMockGenerateMessage('Mock CV generation queued…');
        pollTask(data.task_id, (result) => {
          setMockGenerateStatus('success');
          const message =
            typeof result?.message === 'string'
              ? result.message
              : 'Generated mock CV';
          setMockGenerateMessage(message);
          fetchCvFiles();
        }, (errorMessage) => {
          setMockGenerateStatus('error');
          setMockGenerateMessage(errorMessage);
        });
      })
      .catch((err) => {
        setMockGenerateStatus('error');
        setMockGenerateMessage(err.message);
      });
  };

  const ingestRagIndex = () => {
    setIngestStatus('loading');
    setIngestMessage(null);
    apiPost<{ task_id: string; status: string }>('/rag/ingest')
      .then((data) => {
        setIngestMessage('Ingestion queued…');
        pollTask(
          data.task_id,
          (result) => {
            const count =
              typeof result?.documents === 'number'
                ? result.documents
                : undefined;
            setIngestStatus('success');
            setIngestMessage(
              count !== undefined
                ? `Ingested ${count} CV${count === 1 ? '' : 's'} into RAG index.`
                : 'RAG index rebuilt.'
            );
          },
          (errorMessage) => {
            setIngestStatus('error');
            setIngestMessage(errorMessage);
          }
        );
      })
      .catch((err) => {
        setIngestStatus('error');
        setIngestMessage(err.message);
      });
  };

  const pollTask = (
    taskId: string,
    onSuccess: (result: Record<string, unknown>) => void,
    onError: (message: string) => void,
    attempt = 0
  ) => {
    const MAX_ATTEMPTS = 40;
    const RETRY_MS = 1500;

    apiGet<TaskStatus>(`/tasks/${taskId}`)
      .then((data) => {
        const status = (data.status || '').toUpperCase();
        if (status === 'SUCCESS') {
          onSuccess((data.result as Record<string, unknown>) || {});
          return;
        }
        if (status === 'FAILURE') {
          onError(data.error || 'Task failed');
          return;
        }
        if (attempt >= MAX_ATTEMPTS) {
          onError('Task timed out. Please try again.');
          return;
        }
        setTimeout(
          () => pollTask(taskId, onSuccess, onError, attempt + 1),
          RETRY_MS
        );
      })
      .catch((err) => {
        onError(err.message || 'Task check failed');
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

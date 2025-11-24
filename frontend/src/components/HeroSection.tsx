type HeroSectionProps = {
  backendStatus: string;
  generateStatus: 'idle' | 'loading' | 'error' | 'success';
  generateMessage: string | null;
  mockStatus: 'idle' | 'loading' | 'error' | 'success';
  mockMessage: string | null;
  onGenerateCv: () => void;
  onGenerateMock: () => void;
};

export function HeroSection({
  backendStatus,
  generateStatus,
  generateMessage,
  mockStatus,
  mockMessage,
  onGenerateCv,
  onGenerateMock,
}: HeroSectionProps) {
  return (
    <header className="app-hero">
      <p className="hero-pill">AI CV Screener</p>
      <h1>Generate polished CVs & chat with your candidate corpus</h1>
      <p className="hero-subtitle">
        {backendStatus || 'Backend status unavailable'}
      </p>
      <div className="hero-actions">
        <button
          className="btn btn-primary"
          onClick={onGenerateCv}
          disabled={generateStatus === 'loading'}
        >
          {generateStatus === 'loading' ? 'Generating…' : 'Generate CV'}
        </button>
        <button
          className="btn btn-secondary"
          onClick={onGenerateMock}
          disabled={mockStatus === 'loading'}
        >
          {mockStatus === 'loading' ? 'Mocking…' : 'Generate Mock CV'}
        </button>
      </div>
      {(generateMessage || mockMessage) && (
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
          {mockMessage && (
            <span
              className={`status-text ${
                mockStatus === 'error' ? 'error' : 'success'
              }`}
            >
              {mockMessage}
            </span>
          )}
        </div>
      )}
    </header>
  );
}

type CvLibraryProps = {
  files: string[];
  status: 'idle' | 'loading' | 'loaded' | 'error';
  error: string | null;
  onRefresh: () => void;
};

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL?.replace(/\/$/, '') || 'http://localhost:8000';

export function CvLibrary({ files, status, error, onRefresh }: CvLibraryProps) {
  return (
    <section className="card cv-card">
      <div className="card-header">
        <h2>CV Library</h2>
        <p>Browse generated PDFs and open them directly from storage.</p>
      </div>
      <div className="card-actions">
        <button className="btn btn-ghost" onClick={onRefresh} disabled={status === 'loading'}>
          {status === 'loading' ? 'Refreshing…' : 'Refresh list'}
        </button>
        {status === 'error' && error && <span className="status-text error">{error}</span>}
        {status === 'loaded' && files.length === 0 && (
          <span className="status-text muted">No static CVs were found. Generate one above.</span>
        )}
      </div>
      {files.length > 0 && (
        <ul className="file-grid">
          {files.map((file) => (
            <li key={file}>
              <a
                href={`${API_BASE_URL}/static/${encodeURIComponent(file)}`}
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
  );
}

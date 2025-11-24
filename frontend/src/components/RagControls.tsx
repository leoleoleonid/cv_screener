type RagControlsProps = {
  ingestStatus: 'idle' | 'loading' | 'error' | 'success';
  ingestMessage: string | null;
  onIngest: () => void;
};

export function RagControls({
  ingestStatus,
  ingestMessage,
  onIngest,
}: RagControlsProps) {
  return (
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
          onClick={onIngest}
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
  );
}

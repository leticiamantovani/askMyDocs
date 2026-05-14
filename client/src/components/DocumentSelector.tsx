import type { Document } from "../types"

interface Props {
  documents: Document[]
  activeId: string | null
  onSelect: (id: string) => void
}

function FileIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  )
}

export function DocumentSelector({ documents, activeId, onSelect }: Props) {
  if (documents.length === 0) return null

  return (
    <div className="doc-selector">
      <span className="doc-selector__label">Documents</span>
      <div className="doc-selector__list">
        {documents.map((doc) => (
          <button
            key={doc.id}
            className={`doc-selector__item ${activeId === doc.id ? "doc-selector__item--active" : ""}`}
            onClick={() => onSelect(doc.id)}
            title={doc.filename}
          >
            <span className="doc-selector__icon"><FileIcon /></span>
            <span className="doc-selector__name">{doc.filename}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

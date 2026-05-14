import type { Document } from "../types"

interface Props {
  documents: Document[]
  activeId: string | null
  onSelect: (id: string) => void
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
            <span className="doc-selector__icon">📄</span>
            <span className="doc-selector__name">{doc.filename}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

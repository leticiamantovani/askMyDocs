import { useNavigate } from "react-router-dom"
import type { Conversation } from "../types"

interface Props {
  conversations: Conversation[]
  activeId: string | null
  isNewSession: boolean
  onSelect: (id: string, documentId: string | null) => void
  onNew: () => void
  loading: boolean
  userName?: string | null
}

export function ConversationSidebar({ conversations, activeId, isNewSession, onSelect, onNew, loading, userName }: Props) {
  const navigate = useNavigate()
  const initials = userName ? userName.charAt(0).toUpperCase() : "?"

  return (
    <aside className="sidebar">
      <div className="sidebar__header">
        <span className="sidebar__brand">RAG Chatbot</span>
        <button className="sidebar__new" onClick={onNew} title="New conversation">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 5v14M5 12h14" />
          </svg>
        </button>
      </div>

      <div className="sidebar__list">
        {isNewSession && (
          <button className="sidebar__item sidebar__item--active sidebar__item--new">
            <span className="sidebar__item-title">New conversation</span>
          </button>
        )}

        {loading && conversations.length === 0 && (
          <p className="sidebar__empty">Loading...</p>
        )}
        {!loading && conversations.length === 0 && !isNewSession && (
          <p className="sidebar__empty">No conversations yet</p>
        )}

        {conversations.map((conv) => (
          <button
            key={conv.id}
            className={`sidebar__item${conv.id === activeId ? " sidebar__item--active" : ""}`}
            onClick={() => onSelect(conv.id, conv.document_id)}
          >
            <span className="sidebar__item-title">
              {conv.title ?? "New conversation"}
            </span>
          </button>
        ))}
      </div>

      <button className="sidebar__profile" onClick={() => navigate("/profile")}>
        <span className="sidebar__avatar">{initials}</span>
        <span className="sidebar__profile-name">{userName ?? "Account"}</span>
      </button>
    </aside>
  )
}

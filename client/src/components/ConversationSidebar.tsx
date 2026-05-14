import { useState } from "react"
import { useNavigate } from "react-router-dom"
import type { Conversation } from "../types"
import { BugReportButton } from "./BugReportButton"
import { ConfirmModal } from "./ConfirmModal"

interface Props {
  conversations: Conversation[]
  activeId: string | null
  isNewSession: boolean
  onSelect: (id: string, documentId: string | null) => void
  onNew: () => void
  onDelete: (id: string) => void
  loading: boolean
  userName?: string | null
}

export function ConversationSidebar({ conversations, activeId, isNewSession, onSelect, onNew, onDelete, loading, userName }: Props) {
  const navigate = useNavigate()
  const initials = userName ? userName.charAt(0).toUpperCase() : "?"
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null)

  const pendingConv = conversations.find((c) => c.id === pendingDeleteId)

  function handleConfirmDelete() {
    if (pendingDeleteId) onDelete(pendingDeleteId)
    setPendingDeleteId(null)
  }

  return (
    <>
      <aside className="sidebar">
        <div className="sidebar__header">
          <span className="sidebar__brand">AskMyDocs</span>
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
              <span
                className="sidebar__item-delete"
                role="button"
                onClick={(e) => { e.stopPropagation(); setPendingDeleteId(conv.id) }}
                title="Delete conversation"
              >
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </span>
            </button>
          ))}
        </div>

        <div className="sidebar__footer">
          <button className="sidebar__profile" onClick={() => navigate("/profile")}>
            <span className="sidebar__avatar">{initials}</span>
            <span className="sidebar__profile-name">{userName ?? "Account"}</span>
          </button>
          <BugReportButton trigger={(open) => (
            <button className="sidebar__bug" onClick={open} aria-label="Report a bug">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M8 2l1.5 1.5"/>
                <path d="M14.5 3.5L16 2"/>
                <path d="M9 7H5l-2 3h2"/>
                <path d="M15 7h4l2 3h-2"/>
                <path d="M9 7a3 3 0 0 0-3 3v5a6 6 0 0 0 12 0v-5a3 3 0 0 0-3-3H9z"/>
                <path d="M6 13H3"/>
                <path d="M21 13h-3"/>
                <path d="M12 20v2"/>
              </svg>
              <span className="sidebar__bug-tooltip">Report a bug</span>
            </button>
          )} />
        </div>
      </aside>

      {pendingDeleteId && (
        <ConfirmModal
          title="Delete conversation"
          description={`"${pendingConv?.title ?? "This conversation"}" will be permanently deleted.`}
          confirmLabel="Delete"
          onConfirm={handleConfirmDelete}
          onCancel={() => setPendingDeleteId(null)}
        />
      )}
    </>
  )
}

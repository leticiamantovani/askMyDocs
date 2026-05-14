import { useNavigate } from "react-router-dom"
import type { Conversation } from "../types"

interface Props {
  conversations: Conversation[]
  activeId: string | null
  onSelect: (id: string) => void
  onNew: () => void
  loading: boolean
  userName?: string | null
}

function formatDate(isoString: string): string {
  const date = new Date(isoString)
  const now = new Date()
  const diffDays = Math.floor((now.getTime() - date.getTime()) / 86_400_000)

  if (diffDays === 0) return "Today"
  if (diffDays === 1) return "Yesterday"
  if (diffDays < 7) return `${diffDays} days ago`
  return date.toLocaleDateString()
}

function groupByDate(conversations: Conversation[]): [string, Conversation[]][] {
  const groups = new Map<string, Conversation[]>()
  for (const conv of conversations) {
    const label = formatDate(conv.created_at)
    const existing = groups.get(label) ?? []
    existing.push(conv)
    groups.set(label, existing)
  }
  return Array.from(groups.entries())
}

export function ConversationSidebar({ conversations, activeId, onSelect, onNew, loading, userName }: Props) {
  const groups = groupByDate(conversations)
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
        {loading && conversations.length === 0 && (
          <p className="sidebar__empty">Loading...</p>
        )}
        {!loading && conversations.length === 0 && (
          <p className="sidebar__empty">No conversations yet</p>
        )}

        {groups.map(([label, items]) => (
          <div key={label} className="sidebar__group">
            <span className="sidebar__group-label">{label}</span>
            {items.map((conv) => (
              <button
                key={conv.id}
                className={`sidebar__item${conv.id === activeId ? " sidebar__item--active" : ""}`}
                onClick={() => onSelect(conv.id)}
              >
                <span className="sidebar__item-title">
                  {conv.title ?? "New conversation"}
                </span>
              </button>
            ))}
          </div>
        ))}
      </div>

      <button className="sidebar__profile" onClick={() => navigate("/profile")}>
        <span className="sidebar__avatar">{initials}</span>
        <span className="sidebar__profile-name">{userName ?? "Account"}</span>
      </button>
    </aside>
  )
}

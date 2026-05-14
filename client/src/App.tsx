import { useCallback, useEffect, useRef, useState } from "react"
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import { ChatInput } from "./components/ChatInput"
import { ConversationSidebar } from "./components/ConversationSidebar"
import { DocumentSelector } from "./components/DocumentSelector"
import { MessageList } from "./components/MessageList"
import { PdfDropzone } from "./components/PdfDropzone"
import { useChat } from "./hooks/useChat"
import "./index.css"
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage"
import { LoginPage } from "./pages/LoginPage"
import { ProfilePage } from "./pages/ProfilePage"
import { ResetPasswordPage } from "./pages/ResetPasswordPage"
import { getMe, isAuthenticated, listConversations, listDocuments, logout } from "./services/api"
import type { Conversation, Document, Message } from "./types"

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!isAuthenticated()) return <Navigate to="/login" replace />
  return <>{children}</>
}

function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [documents, setDocuments] = useState<Document[]>([])
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null)
  const [sidebarLoading, setSidebarLoading] = useState(false)
  const [systemMessages, setSystemMessages] = useState<Message[]>([])
  const [userName, setUserName] = useState<string | null>(null)

  const [sessionKey, setSessionKey] = useState(() => `new-${Date.now()}`)
  const [sessionConversationId, setSessionConversationId] = useState<string | null>(null)

  const { messages, conversationId, loading, historyLoading, sendMessage } = useChat({
    sessionKey,
    conversationId: sessionConversationId,
    documentId: activeDocumentId,
  })

  const lastConvIdRef = useRef<string | null>(null)

  const refreshConversations = useCallback(async () => {
    setSidebarLoading(true)
    try {
      const list = await listConversations()
      setConversations(list)
    } finally {
      setSidebarLoading(false)
    }
  }, [])

  const refreshDocuments = useCallback(async () => {
    const list = await listDocuments()
    setDocuments(list)
  }, [])

  useEffect(() => {
    refreshConversations()
    refreshDocuments()
    getMe().then((u) => setUserName(u.name)).catch(() => null)
  }, [refreshConversations, refreshDocuments])

  useEffect(() => {
    if (conversationId && conversationId !== lastConvIdRef.current) {
      lastConvIdRef.current = conversationId
      refreshConversations()
    }
  }, [conversationId, refreshConversations])

  const handleSelectConversation = useCallback((id: string) => {
    lastConvIdRef.current = id
    setSessionConversationId(id)
    setSessionKey(id)
    setSystemMessages([])
  }, [])

  const handleNewConversation = useCallback(() => {
    lastConvIdRef.current = null
    setSessionConversationId(null)
    setSessionKey(`new-${Date.now()}`)
    setSystemMessages([])
  }, [])

  const handleUploadSuccess = useCallback((doc: Document) => {
    setDocuments((prev) => [doc, ...prev])
    setActiveDocumentId(doc.id)
  }, [])

  const allMessages = [...systemMessages, ...messages]
  const isEmpty = allMessages.length === 0 && !historyLoading

  return (
    <div className="layout">
      <ConversationSidebar
        conversations={conversations}
        activeId={conversationId}
        onSelect={handleSelectConversation}
        onNew={handleNewConversation}
        loading={sidebarLoading}
        userName={userName}
      />

      <div className="main">
        <header className="main__header">
          <PdfDropzone onUploadSuccess={handleUploadSuccess} />
          <button className="app__logout" onClick={logout}>Logout</button>
        </header>

        <DocumentSelector
          documents={documents}
          activeId={activeDocumentId}
          onSelect={setActiveDocumentId}
        />

        <main className="app__chat">
          {historyLoading && (
            <div className="chat__empty">
              <p>Loading messages…</p>
            </div>
          )}
          {isEmpty && (
            <div className="chat__empty">
              <div className="chat__empty-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
              </div>
              <p>{activeDocumentId ? "Ask anything about this document" : "Upload a PDF to get started"}</p>
            </div>
          )}
          <MessageList messages={allMessages} />
          <ChatInput onSend={sendMessage} disabled={loading || historyLoading || !activeDocumentId} />
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <ChatPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

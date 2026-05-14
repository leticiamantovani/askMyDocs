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
      />

      <div className="main">
        <header className="main__header">
          <PdfDropzone onUploadSuccess={handleUploadSuccess} />
          <div className="header__user">
            {userName && <span className="header__name">Hi, {userName}</span>}
            <button className="app__logout" onClick={logout}>Logout</button>
          </div>
        </header>

        <DocumentSelector
          documents={documents}
          activeId={activeDocumentId}
          onSelect={setActiveDocumentId}
        />

        <main className="app__chat">
          {historyLoading && <div className="chat__empty"><p>Loading messages...</p></div>}
          {isEmpty && (
            <div className="chat__empty">
              <p>{activeDocumentId ? "Ask anything about this document" : "Select a document to start"}</p>
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

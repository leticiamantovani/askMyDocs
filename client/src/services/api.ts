import type { Conversation, Document } from "../types"

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

function getToken(): string | null {
  return localStorage.getItem("token")
}

function authHeaders(): HeadersInit {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

function handleUnauthorized(response: Response): void {
  if (response.status === 401) {
    localStorage.removeItem("token")
    window.location.href = "/login"
  }
}

async function assertOk(response: Response, message?: string): Promise<void> {
  if (!response.ok) {
    handleUnauthorized(response)
    throw new Error(message ?? `HTTP ${response.status}`)
  }
}

export async function register(email: string, password: string, name: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? `HTTP ${response.status}`)
  }
}

export async function getMe(): Promise<{ id: string; email: string; name: string | null }> {
  const response = await fetch(`${BASE_URL}/auth/me`, {
    headers: { ...authHeaders() },
  })
  await assertOk(response)
  return response.json()
}

export async function login(email: string, password: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? "Invalid credentials")
  }
  const { access_token } = await response.json()
  localStorage.setItem("token", access_token)
}

export function logout(): void {
  localStorage.removeItem("token")
}

export function isAuthenticated(): boolean {
  return !!getToken()
}

export interface ApiMessage {
  id: string
  role: "user" | "assistant"
  content: string
  created_at: string
}

export async function forgotPassword(email: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? `HTTP ${response.status}`)
  }
}

export async function resetPassword(token: string, new_password: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail ?? `HTTP ${response.status}`)
  }
}

export async function getConversationMessages(conversationId: string): Promise<ApiMessage[]> {
  const response = await fetch(`${BASE_URL}/conversations/${conversationId}/messages`, {
    headers: { ...authHeaders() },
  })
  await assertOk(response)
  return response.json()
}

export async function listConversations(): Promise<Conversation[]> {
  const response = await fetch(`${BASE_URL}/conversations`, {
    headers: { ...authHeaders() },
  })
  await assertOk(response)
  return response.json()
}

export async function createConversation(): Promise<Conversation> {
  const response = await fetch(`${BASE_URL}/conversations`, {
    method: "POST",
    headers: { ...authHeaders() },
  })
  await assertOk(response)
  return response.json()
}

export async function listDocuments(): Promise<Document[]> {
  const response = await fetch(`${BASE_URL}/documents`, {
    headers: { ...authHeaders() },
  })
  await assertOk(response)
  return response.json()
}

export async function streamChat(
  question: string,
  conversationId: string | null,
  documentId: string | null,
  onChunk: (chunk: string) => void,
  onDone: (conversationId: string) => void,
  signal?: AbortSignal
): Promise<void> {
  const url = new URL(`${BASE_URL}/chat`)
  if (conversationId) url.searchParams.set("conversation_id", conversationId)

  const response = await fetch(url.toString(), {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ question, document_id: documentId }),
    signal,
  })

  await assertOk(response)

  const newConversationId = response.headers.get("X-Conversation-ID") ?? conversationId ?? ""

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    onChunk(decoder.decode(value, { stream: true }))
  }

  onDone(newConversationId)
}

export async function uploadPdf(file: File): Promise<Document> {
  const form = new FormData()
  form.append("file", file)

  const response = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    headers: authHeaders(),
    body: form,
  })
  await assertOk(response, `Upload failed: HTTP ${response.status}`)
  return response.json()
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  streaming?: boolean
}

export interface Conversation {
  id: string
  title: string | null
  document_id: string | null
  created_at: string
}

export interface Document {
  id: string
  filename: string
  created_at: string
}

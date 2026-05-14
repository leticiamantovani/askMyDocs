import { useEffect, useRef } from "react"
import ReactMarkdown from "react-markdown"
import type { Message } from "../types"

interface Props {
  messages: Message[]
}

export function MessageList({ messages }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <div className="message-list">
      {messages.map((msg) => (
        <div key={msg.id} className={`message message--${msg.role}`}>
          <span className="message__content">
            <ReactMarkdown>{msg.content}</ReactMarkdown>
            {msg.streaming && <span className="message__cursor" />}
          </span>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}

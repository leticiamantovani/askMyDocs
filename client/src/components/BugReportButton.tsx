import { useState } from "react"
import { reportBug } from "../services/api"

type Step = "idle" | "open" | "sending" | "done"

interface Props {
  trigger?: (open: () => void) => React.ReactNode
}

export function BugReportButton({ trigger }: Props) {
  const [step, setStep] = useState<Step>("idle")
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [error, setError] = useState<string | null>(null)

  function open() {
    setStep("open")
    setTitle("")
    setDescription("")
    setError(null)
  }

  function close() {
    if (step === "sending") return
    setStep("idle")
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim() || !description.trim()) return
    setStep("sending")
    setError(null)
    try {
      await reportBug(title.trim(), description.trim())
      setStep("done")
    } catch {
      setError("Failed to send. Please try again.")
      setStep("open")
    }
  }

  const defaultTrigger = (
    <button className="bug-fab" onClick={open} aria-label="Report a bug">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M8 2l1.5 1.5"/><path d="M14.5 3.5L16 2"/>
        <path d="M9 7H5l-2 3h2"/><path d="M15 7h4l2 3h-2"/>
        <path d="M9 7a3 3 0 0 0-3 3v5a6 6 0 0 0 12 0v-5a3 3 0 0 0-3-3H9z"/>
        <path d="M6 13H3"/><path d="M21 13h-3"/><path d="M12 20v2"/>
      </svg>
      <span className="bug-fab__tooltip">Report a bug</span>
    </button>
  )

  return (
    <>
      {trigger ? trigger(open) : defaultTrigger}

      {step !== "idle" && (
        <div className="modal-backdrop" onClick={close}>
          <div className="modal bug-modal" onClick={(e) => e.stopPropagation()}>
            {step === "done" ? (
              <>
                <div className="bug-modal__success-icon">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                  </svg>
                </div>
                <h2 className="modal__title">Report sent!</h2>
                <p className="modal__description">Thank you, we'll look into it as soon as possible.</p>
                <div className="modal__actions">
                  <button className="modal__confirm" style={{background:"var(--accent)"}} onClick={() => setStep("idle")}>Done</button>
                </div>
              </>
            ) : (
              <>
                <div className="bug-modal__header">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/>
                    <path d="M12 8v4M12 16h.01"/>
                  </svg>
                  <h2 className="modal__title">Report a bug</h2>
                </div>
                <p className="modal__description">Something not working? Let us know and we'll fix it.</p>
                <form className="bug-modal__form" onSubmit={submit}>
                  <label className="auth__label">
                    Title
                    <input
                      className="auth__input"
                      type="text"
                      placeholder="Short description of the issue"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      required
                      autoFocus
                    />
                  </label>
                  <label className="auth__label">
                    Details
                    <textarea
                      className="auth__input bug-modal__textarea"
                      placeholder="Steps to reproduce, what you expected vs what happened…"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      required
                      rows={4}
                    />
                  </label>
                  {error && <p className="auth__error">{error}</p>}
                  <div className="modal__actions">
                    <button type="button" className="modal__cancel" onClick={close}>Cancel</button>
                    <button type="submit" className="modal__confirm" style={{background:"var(--accent)"}} disabled={step === "sending"}>
                      {step === "sending" ? "Sending…" : "Send report"}
                    </button>
                  </div>
                </form>
              </>
            )}
          </div>
        </div>
      )}
    </>
  )
}

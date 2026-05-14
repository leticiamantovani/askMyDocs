import { useState } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import { resetPassword } from "../services/api"

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get("token") ?? ""

  const [password, setPassword] = useState("")
  const [confirm, setConfirm] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (password !== confirm) {
      setError("Passwords do not match.")
      return
    }
    setError(null)
    setLoading(true)
    try {
      await resetPassword(token, password)
      navigate("/login", { state: { message: "Password reset successfully. Please log in." } })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid or expired token.")
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="auth">
        <div className="auth__card">
          <p className="auth__error">Invalid reset link.</p>
          <Link className="auth__link" to="/login">Back to login</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="auth">
      <div className="auth__card">
        <div className="auth__logo">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </div>
        <h1 className="auth__title">RAG Chatbot</h1>
        <p className="auth__subtitle">New password</p>

        <form className="auth__form" onSubmit={handleSubmit}>
          <label className="auth__label">
            New password
            <input
              className="auth__input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoFocus
              minLength={6}
            />
          </label>

          <label className="auth__label">
            Confirm password
            <input
              className="auth__input"
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              minLength={6}
            />
          </label>

          {error && <p className="auth__error">{error}</p>}

          <button className="auth__submit" type="submit" disabled={loading}>
            {loading ? "Saving..." : "Reset password"}
          </button>
        </form>
      </div>
    </div>
  )
}

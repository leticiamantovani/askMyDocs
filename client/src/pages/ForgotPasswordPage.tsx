import { FormEvent, useState } from "react"
import { Link } from "react-router-dom"
import { forgotPassword } from "../services/api"

export function ForgotPasswordPage() {
  const [email, setEmail] = useState("")
  const [sent, setSent] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await forgotPassword(email)
      setSent(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth">
      <div className="auth__card">
        <h1 className="auth__title">RAG Chatbot</h1>
        <h2 className="auth__subtitle">Forgot your password?</h2>

        {sent ? (
          <div className="auth__success">
            <p>If this email is registered, you will receive a reset link shortly.</p>
            <Link className="auth__link" to="/login">Back to login</Link>
          </div>
        ) : (
          <form className="auth__form" onSubmit={handleSubmit}>
            <label className="auth__label">
              Email
              <input
                className="auth__input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
              />
            </label>

            {error && <p className="auth__error">{error}</p>}

            <button className="auth__submit" type="submit" disabled={loading}>
              {loading ? "Sending..." : "Send reset link"}
            </button>

            <Link className="auth__link" to="/login">Back to login</Link>
          </form>
        )}
      </div>
    </div>
  )
}

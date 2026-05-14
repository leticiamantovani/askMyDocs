import { useState } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { login, register } from "../services/api"

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const successMessage = (location.state as { message?: string } | null)?.message
  const [mode, setMode] = useState<"login" | "register">("login")
  const [email, setEmail] = useState("")
  const [name, setName] = useState("")
  const [password, setPassword] = useState("")
  const [confirm, setConfirm] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (mode === "register" && password !== confirm) {
      setError("Passwords do not match.")
      return
    }
    setError(null)
    setLoading(true)
    try {
      if (mode === "register") {
        await register(email, password, name)
        await login(email, password)
      } else {
        await login(email, password)
      }
      navigate("/")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  function switchMode(next: "login" | "register") {
    setMode(next)
    setName("")
    setConfirm("")
    setError(null)
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

        {successMessage && <p className="auth__success-msg">{successMessage}</p>}

        <div className="auth__tabs">
          <button
            className={`auth__tab ${mode === "login" ? "auth__tab--active" : ""}`}
            onClick={() => switchMode("login")}
            type="button"
          >
            Login
          </button>
          <button
            className={`auth__tab ${mode === "register" ? "auth__tab--active" : ""}`}
            onClick={() => switchMode("register")}
            type="button"
          >
            Register
          </button>
        </div>

        <form className="auth__form" onSubmit={handleSubmit}>
          {mode === "register" && (
            <label className="auth__label">
              Name
              <input
                className="auth__input"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                autoFocus
                placeholder="Your name"
              />
            </label>
          )}

          <label className="auth__label">
            Email
            <input
              className="auth__input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus={mode === "login"}
            />
          </label>

          <label className="auth__label">
            Password
            <input
              className="auth__input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>

          {mode === "register" && (
            <label className="auth__label">
              Confirm password
              <input
                className="auth__input"
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
              />
            </label>
          )}

          {error && <p className="auth__error">{error}</p>}

          <button className="auth__submit" type="submit" disabled={loading}>
            {loading ? "Loading..." : mode === "login" ? "Login" : "Create account"}
          </button>

          {mode === "login" && (
            <Link className="auth__link" to="/forgot-password">Forgot your password?</Link>
          )}
        </form>
      </div>
    </div>
  )
}

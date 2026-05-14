import { FormEvent, useState } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { login, register } from "../services/api"

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const successMessage = (location.state as { message?: string } | null)?.message
  const [mode, setMode] = useState<"login" | "register">("login")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirm, setConfirm] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (mode === "register" && password !== confirm) {
      setError("Passwords do not match.")
      return
    }
    setError(null)
    setLoading(true)
    try {
      if (mode === "register") {
        await register(email, password)
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

  return (
    <div className="auth">
      <div className="auth__card">
        <h1 className="auth__title">RAG Chatbot</h1>

        {successMessage && <p className="auth__success-msg">{successMessage}</p>}

        <div className="auth__tabs">
          <button
            className={`auth__tab ${mode === "login" ? "auth__tab--active" : ""}`}
            onClick={() => setMode("login")}
            type="button"
          >
            Login
          </button>
          <button
            className={`auth__tab ${mode === "register" ? "auth__tab--active" : ""}`}
            onClick={() => setMode("register")}
            type="button"
          >
            Register
          </button>
        </div>

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

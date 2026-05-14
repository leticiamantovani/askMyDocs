import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { getMe, updatePassword, updateProfile } from "../services/api"

export function ProfilePage() {
  const navigate = useNavigate()

  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [profileSuccess, setProfileSuccess] = useState(false)
  const [profileError, setProfileError] = useState<string | null>(null)
  const [profileLoading, setProfileLoading] = useState(false)

  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [passwordSuccess, setPasswordSuccess] = useState(false)
  const [passwordError, setPasswordError] = useState<string | null>(null)
  const [passwordLoading, setPasswordLoading] = useState(false)

  useEffect(() => {
    getMe().then((u) => {
      setName(u.name ?? "")
      setEmail(u.email)
    })
  }, [])

  async function handleProfileSubmit(e: React.FormEvent) {
    e.preventDefault()
    setProfileError(null)
    setProfileSuccess(false)
    setProfileLoading(true)
    try {
      await updateProfile(name, email)
      setProfileSuccess(true)
    } catch (err) {
      setProfileError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setProfileLoading(false)
    }
  }

  async function handlePasswordSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (newPassword !== confirmPassword) {
      setPasswordError("Passwords do not match.")
      return
    }
    setPasswordError(null)
    setPasswordSuccess(false)
    setPasswordLoading(true)
    try {
      await updatePassword(currentPassword, newPassword)
      setPasswordSuccess(true)
      setCurrentPassword("")
      setNewPassword("")
      setConfirmPassword("")
    } catch (err) {
      setPasswordError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setPasswordLoading(false)
    }
  }

  return (
    <div className="profile">
      <div className="profile__card">
        <div className="profile__header">
          <button className="profile__back" onClick={() => navigate("/")} type="button">← Back</button>
          <h1 className="profile__title">Account settings</h1>
        </div>

        <section className="profile__section">
          <h2 className="profile__section-title">Profile</h2>
          <form className="auth__form" onSubmit={handleProfileSubmit}>
            <label className="auth__label">
              Name
              <input
                className="auth__input"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </label>
            <label className="auth__label">
              Email
              <input
                className="auth__input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </label>
            {profileError && <p className="auth__error">{profileError}</p>}
            {profileSuccess && <p className="auth__success-msg">Profile updated.</p>}
            <button className="auth__submit" type="submit" disabled={profileLoading}>
              {profileLoading ? "Saving..." : "Save changes"}
            </button>
          </form>
        </section>

        <div className="profile__divider" />

        <section className="profile__section">
          <h2 className="profile__section-title">Change password</h2>
          <form className="auth__form" onSubmit={handlePasswordSubmit}>
            <label className="auth__label">
              Current password
              <input
                className="auth__input"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </label>
            <label className="auth__label">
              New password
              <input
                className="auth__input"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={6}
              />
            </label>
            <label className="auth__label">
              Confirm new password
              <input
                className="auth__input"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={6}
              />
            </label>
            {passwordError && <p className="auth__error">{passwordError}</p>}
            {passwordSuccess && <p className="auth__success-msg">Password updated.</p>}
            <button className="auth__submit" type="submit" disabled={passwordLoading}>
              {passwordLoading ? "Saving..." : "Update password"}
            </button>
          </form>
        </section>
      </div>
    </div>
  )
}

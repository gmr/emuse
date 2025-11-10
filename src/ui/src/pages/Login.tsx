import { useState, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import '@awesome.me/webawesome/dist/components/card/card.js'
import '@awesome.me/webawesome/dist/components/input/input.js'
import '@awesome.me/webawesome/dist/components/button/button.js'
import '@awesome.me/webawesome/dist/components/callout/callout.js'
import '@awesome.me/webawesome/dist/components/icon/icon.js'

// Type for Web Awesome input component with value property
type WaInputElement = HTMLElement & { value: string }

export default function Login() {
  const [error, setError] = useState<string | null>(null)
  const emailRef = useRef<WaInputElement>(null)
  const passwordRef = useRef<WaInputElement>(null)
  const { login, isLoading } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Read values directly from the Web Component elements
    const email = emailRef.current?.value || ''
    const password = passwordRef.current?.value || ''

    try {
      await login(email, password)
      navigate('/')
    } catch {
      setError('Login failed. Please check your credentials and try again.')
    }
  }

  return (
    <div style={{ maxWidth: '400px', margin: '2rem auto', padding: '1rem' }}>
      <wa-card>
        <div slot="header">
          <h1 style={{ margin: 0 }}>Login</h1>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <wa-input
              ref={emailRef}
              type="email"
              label="Email"
              required
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <wa-input
              ref={passwordRef}
              type="password"
              label="Password"
              required
              password-toggle
            />
          </div>

          <wa-button
            type="submit"
            variant="brand"
            size="medium"
            disabled={isLoading}
            style={{ width: '100%', marginBottom: '1rem' }}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </wa-button>

          {error && (
            <wa-callout variant="danger" open>
              <wa-icon slot="icon" name="exclamation-triangle" />
              {error}
            </wa-callout>
          )}
        </form>

        <div slot="footer" style={{ textAlign: 'center' }}>
          <p>
            Don't have an account? <Link to="/signup">Sign up</Link>
          </p>
          <Link to="/">Back to Home</Link>
        </div>
      </wa-card>
    </div>
  )
}

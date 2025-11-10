import { useState, useRef, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import '@awesome.me/webawesome/dist/components/card/card.js'
import '@awesome.me/webawesome/dist/components/input/input.js'
import '@awesome.me/webawesome/dist/components/button/button.js'
import '@awesome.me/webawesome/dist/components/callout/callout.js'
import '@awesome.me/webawesome/dist/components/icon/icon.js'

// Declare Turnstile types
declare global {
  interface Window {
    turnstile?: {
      render: (element: string | HTMLElement, options: {
        sitekey: string
        callback?: (token: string) => void
        size?: 'normal' | 'compact' | 'flexible'
      }) => string
      getResponse: (widgetId: string) => string
      reset: (widgetId: string) => void
    }
  }
}

// Type for Web Awesome input component with value property
type WaInputElement = HTMLElement & { value: string }

export default function Login() {
  const [error, setError] = useState<string | null>(null)
  const [turnstileSiteKey, setTurnstileSiteKey] = useState<string | null>(null)
  const emailRef = useRef<WaInputElement>(null)
  const passwordRef = useRef<WaInputElement>(null)
  const turnstileRef = useRef<HTMLDivElement>(null)
  const turnstileWidgetId = useRef<string | null>(null)
  const { login, isLoading } = useAuth()
  const navigate = useNavigate()

  // Load Turnstile site key
  useEffect(() => {
    fetch('/api/turnstile/config')
      .then(res => res.json())
      .then(data => setTurnstileSiteKey(data.site_key))
      .catch(err => console.error('Failed to load Turnstile config:', err))
  }, [])

  // Load Turnstile script and render widget
  useEffect(() => {
    if (!turnstileSiteKey || !turnstileRef.current) return

    // Load Turnstile script if not already loaded
    if (!window.turnstile) {
      const script = document.createElement('script')
      script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js'
      script.async = true
      script.defer = true
      script.onload = () => {
        // Render widget after script loads
        if (window.turnstile && turnstileRef.current && !turnstileWidgetId.current) {
          turnstileWidgetId.current = window.turnstile.render(turnstileRef.current, {
            sitekey: turnstileSiteKey,
            size: 'flexible',
          })
        }
      }
      document.head.appendChild(script)
    } else if (!turnstileWidgetId.current) {
      // Script already loaded, render widget immediately
      turnstileWidgetId.current = window.turnstile.render(turnstileRef.current, {
        sitekey: turnstileSiteKey,
        size: 'flexible',
      })
    }
  }, [turnstileSiteKey])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Read values directly from the Web Component elements
    const email = emailRef.current?.value || ''
    const password = passwordRef.current?.value || ''

    // Get Turnstile token
    let turnstileToken = ''
    if (window.turnstile && turnstileWidgetId.current) {
      turnstileToken = window.turnstile.getResponse(turnstileWidgetId.current)
    }

    if (!turnstileToken) {
      setError('Please complete the CAPTCHA verification')
      // Reset widget if it's in a solved-but-consumed state
      if (window.turnstile && turnstileWidgetId.current) {
        window.turnstile.reset(turnstileWidgetId.current)
      }
      return
    }

    try {
      await login(email, password, turnstileToken)
      navigate('/')
    } catch {
      setError('Login failed. Please check your credentials and try again.')
      // Reset Turnstile widget so user can retry
      if (window.turnstile && turnstileWidgetId.current) {
        window.turnstile.reset(turnstileWidgetId.current)
      }
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

          {/* Turnstile CAPTCHA Widget */}
          <div style={{ marginBottom: '1rem' }}>
            <div ref={turnstileRef}></div>
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

import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import '@awesome.me/webawesome/dist/components/card/card.js'
import '@awesome.me/webawesome/dist/components/input/input.js'
import '@awesome.me/webawesome/dist/components/button/button.js'
import '@awesome.me/webawesome/dist/components/callout/callout.js'
import '@awesome.me/webawesome/dist/components/icon/icon.js'

interface SignupRequest {
  email: string
  password: string
  first_name: string
  surname: string
  display_name: string
  date_of_birth: string
  locale: string
  timezone: string
}

async function signupUser(data: SignupRequest) {
  const response = await fetch('/api/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
    credentials: 'include',
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Signup failed' }))
    throw new Error(error.detail || 'Signup failed')
  }

  return response.json()
}

function detectLocale(): string {
  // Get browser language and format as locale (e.g., 'en-US' -> 'en_US')
  const lang = navigator.language || 'en-US'
  return lang.replace('-', '_')
}

function detectTimezone(): string {
  // Get browser timezone using Intl API
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone
  } catch {
    return 'UTC'
  }
}

export default function Signup() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [firstName, setFirstName] = useState('')
  const [surname, setSurname] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [dateOfBirth, setDateOfBirth] = useState('')
  const [locale, setLocale] = useState('')
  const [timezone, setTimezone] = useState('')
  const [errors, setErrors] = useState<{
    email?: string
    password?: string
    confirmPassword?: string
    firstName?: string
    surname?: string
    displayName?: string
    dateOfBirth?: string
  }>({})

  const navigate = useNavigate()

  // Auto-detect locale and timezone on mount
  useEffect(() => {
    setLocale(detectLocale())
    setTimezone(detectTimezone())
  }, [])

  // Auto-generate display name from first and surname
  useEffect(() => {
    if (firstName && surname && !displayName) {
      setDisplayName(`${firstName} ${surname}`)
    }
  }, [firstName, surname, displayName])

  // Clear password errors when user types
  useEffect(() => {
    if (password || confirmPassword) {
      setErrors(prev => ({
        ...prev,
        password: undefined,
        confirmPassword: undefined
      }))
    }
  }, [password, confirmPassword])

  const mutation = useMutation({
    mutationFn: signupUser,
    onSuccess: () => {
      navigate('/signup/success')
    },
  })

  const validateEmail = (email: string): string | undefined => {
    if (!email) return 'Email is required'
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) return 'Please enter a valid email address'
    return undefined
  }

  const validatePassword = (password: string): string | undefined => {
    if (!password) return 'Password is required'
    if (password.length < 8) return 'Password must be at least 8 characters'
    return undefined
  }

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {}

    // Email validation
    const emailError = validateEmail(email)
    if (emailError) newErrors.email = emailError

    // Password validation
    const passwordError = validatePassword(password)
    if (passwordError) newErrors.password = passwordError

    // Confirm password validation
    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password'
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }

    // Name validations
    if (!firstName.trim()) newErrors.firstName = 'First name is required'
    if (!surname.trim()) newErrors.surname = 'Surname is required'
    if (!displayName.trim()) newErrors.displayName = 'Display name is required'

    // Date of birth validation
    if (!dateOfBirth) {
      newErrors.dateOfBirth = 'Date of birth is required'
    } else {
      const birthDate = new Date(dateOfBirth)
      const today = new Date()
      const age = today.getFullYear() - birthDate.getFullYear()
      if (age < 13) {
        newErrors.dateOfBirth = 'You must be at least 13 years old to sign up'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    mutation.mutate({
      email,
      password,
      first_name: firstName,
      surname,
      display_name: displayName,
      date_of_birth: dateOfBirth,
      locale,
      timezone,
    })
  }

  const inputStyle = {
    width: '100%',
    padding: '0.75rem',
    fontSize: '1rem',
    border: '1px solid #ccc',
    borderRadius: '4px',
    boxSizing: 'border-box' as const,
  }

  const labelStyle = {
    display: 'block',
    marginBottom: '0.5rem',
    fontWeight: '500',
    color: '#333',
  }

  const helpTextStyle = {
    fontSize: '0.875rem',
    color: '#666',
    marginTop: '0.25rem',
  }

  return (
    <div style={{ maxWidth: '600px', margin: '2rem auto', padding: '1rem' }}>
      <wa-card>
        <div slot="header">
          <h1 style={{ margin: 0 }}>Sign Up</h1>
        </div>

        <form onSubmit={handleSubmit} style={{ padding: '0 1rem' }}>
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={labelStyle}>
              Email*
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={inputStyle}
              />
            </label>
            {errors.email && (
              <div style={{ color: '#d32f2f', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                {errors.email}
              </div>
            )}
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={labelStyle}>
              Password*
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={inputStyle}
              />
            </label>
            <div style={helpTextStyle}>Minimum 8 characters</div>
            {errors.password && (
              <div style={{ color: '#d32f2f', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                {errors.password}
              </div>
            )}
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={labelStyle}>
              Confirm Password*
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                style={inputStyle}
              />
            </label>
            {errors.confirmPassword && (
              <div style={{ color: '#d32f2f', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                {errors.confirmPassword}
              </div>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
            <div>
              <label style={labelStyle}>
                First Name*
                <input
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  required
                  style={inputStyle}
                />
              </label>
              {errors.firstName && (
                <div style={{ color: '#d32f2f', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                  {errors.firstName}
                </div>
              )}
            </div>
            <div>
              <label style={labelStyle}>
                Surname*
                <input
                  type="text"
                  value={surname}
                  onChange={(e) => setSurname(e.target.value)}
                  required
                  style={inputStyle}
                />
              </label>
              {errors.surname && (
                <div style={{ color: '#d32f2f', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                  {errors.surname}
                </div>
              )}
            </div>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={labelStyle}>
              Display Name*
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                required
                style={inputStyle}
              />
            </label>
            <div style={helpTextStyle}>This is how your name will appear to others</div>
            {errors.displayName && (
              <div style={{ color: '#d32f2f', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                {errors.displayName}
              </div>
            )}
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={labelStyle}>
              Date of Birth*
              <input
                type="date"
                value={dateOfBirth}
                onChange={(e) => setDateOfBirth(e.target.value)}
                required
                style={inputStyle}
              />
            </label>
            {errors.dateOfBirth && (
              <div style={{ color: '#d32f2f', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                {errors.dateOfBirth}
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={mutation.isPending}
            style={{
              width: '100%',
              padding: '0.75rem',
              fontSize: '1rem',
              fontWeight: '600',
              color: 'white',
              backgroundColor: '#800020',
              border: 'none',
              borderRadius: '4px',
              cursor: mutation.isPending ? 'not-allowed' : 'pointer',
              opacity: mutation.isPending ? 0.6 : 1,
              marginBottom: '1rem',
            }}
          >
            {mutation.isPending ? 'Creating Account...' : 'Sign Up'}
          </button>

          {mutation.isError && (
            <div style={{
              padding: '1rem',
              backgroundColor: '#fee',
              border: '1px solid #fcc',
              borderRadius: '4px',
              color: '#c33',
            }}>
              {mutation.error instanceof Error ? mutation.error.message : 'Signup failed. Please try again.'}
            </div>
          )}
        </form>

        <div slot="footer" style={{ textAlign: 'center' }}>
          <p>
            Already have an account? <Link to="/login">Log in</Link>
          </p>
          <Link to="/">Back to Home</Link>
        </div>
      </wa-card>
    </div>
  )
}

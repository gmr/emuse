import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import '@awesome.me/webawesome/dist/components/card/card.js'
import '@awesome.me/webawesome/dist/components/input/input.js'
import '@awesome.me/webawesome/dist/components/button/button.js'
import '@awesome.me/webawesome/dist/components/callout/callout.js'
import '@awesome.me/webawesome/dist/components/icon/icon.js'

interface LoginRequest {
  email: string
  password: string
}

async function loginUser(credentials: LoginRequest) {
  const response = await fetch('/api/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  })

  if (!response.ok) {
    throw new Error('Login failed')
  }

  return response.json()
}

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const mutation = useMutation({
    mutationFn: loginUser,
    onSuccess: () => {
      console.log('Login successful!')
      // Handle successful login (e.g., redirect)
    },
    onError: (error) => {
      console.error('Login failed:', error)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({ email, password })
  }

  return (
    <div style={{ maxWidth: '400px', margin: '2rem auto', padding: '1rem' }}>
      <wa-card>
        <div slot="header">
          <h1 style={{ margin: 0 }}>Login to eMuse</h1>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <wa-input
              type="email"
              label="Email"
              value={email}
              onWaInput={(e: CustomEvent) => setEmail((e.target as HTMLInputElement).value)}
              required
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <wa-input
              type="password"
              label="Password"
              value={password}
              onWaInput={(e: CustomEvent) => setPassword((e.target as HTMLInputElement).value)}
              required
              password-toggle
            />
          </div>

          <wa-button
            type="submit"
            variant="brand"
            size="medium"
            disabled={mutation.isPending}
            style={{ width: '100%', marginBottom: '1rem' }}
          >
            {mutation.isPending ? 'Logging in...' : 'Login'}
          </wa-button>

          {mutation.isError && (
            <wa-callout variant="danger" open>
              <wa-icon slot="icon" name="exclamation-triangle" />
              Login failed. Please check your credentials and try again.
            </wa-callout>
          )}
        </form>

        <div slot="footer" style={{ textAlign: 'center' }}>
          <Link to="/">Back to Home</Link>
        </div>
      </wa-card>
    </div>
  )
}

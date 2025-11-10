import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import '@awesome.me/webawesome/dist/components/card/card.js'
import '@awesome.me/webawesome/dist/components/callout/callout.js'
import '@awesome.me/webawesome/dist/components/icon/icon.js'
import '@awesome.me/webawesome/dist/components/button/button.js'
import '@awesome.me/webawesome/dist/components/spinner/spinner.js'

async function verifyEmail(token: string) {
  const response = await fetch(`/api/verify-email/${token}`, {
    credentials: 'include',
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Verification failed' }))
    throw new Error(error.detail || 'Verification failed')
  }

  return response.json()
}

export default function VerifyEmail() {
  const { token } = useParams<{ token: string }>()

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['verify-email', token],
    queryFn: () => verifyEmail(token!),
    enabled: !!token,
    retry: false,
  })

  return (
    <div style={{ maxWidth: '500px', margin: '2rem auto', padding: '1rem' }}>
      <wa-card>
        <div slot="header">
          <h1 style={{ margin: 0 }}>Email Verification</h1>
        </div>

        {isLoading && (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <wa-spinner size="large" />
            <p style={{ marginTop: '1rem' }}>Verifying your email...</p>
          </div>
        )}

        {isError && (
          <>
            <wa-callout variant="danger" open>
              <wa-icon slot="icon" name="exclamation-triangle" />
              <strong>Verification Failed</strong>
              <p style={{ margin: '0.5rem 0 0 0' }}>
                {error instanceof Error ? error.message : 'Unable to verify email. The link may be expired or invalid.'}
              </p>
            </wa-callout>
            <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
              <p>Please try signing up again or contact support if the problem persists.</p>
            </div>
          </>
        )}

        {data?.success && (
          <>
            <wa-callout variant="success" open>
              <wa-icon slot="icon" name="check-circle" />
              <strong>Email Verified!</strong>
              <p style={{ margin: '0.5rem 0 0 0' }}>
                {data.message}
              </p>
            </wa-callout>
            <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
              <p>Your account is now active. You can log in to start using eMuse.</p>
            </div>
          </>
        )}

        <div slot="footer" style={{ textAlign: 'center' }}>
          {data?.success ? (
            <Link to="/login">
              <wa-button variant="primary">
                Go to Login
              </wa-button>
            </Link>
          ) : (
            <Link to="/">
              <wa-button variant="default">
                Back to Home
              </wa-button>
            </Link>
          )}
        </div>
      </wa-card>
    </div>
  )
}

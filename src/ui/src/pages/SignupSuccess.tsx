import { Link } from 'react-router-dom'
import '@awesome.me/webawesome/dist/components/card/card.js'
import '@awesome.me/webawesome/dist/components/callout/callout.js'
import '@awesome.me/webawesome/dist/components/icon/icon.js'
import '@awesome.me/webawesome/dist/components/button/button.js'

export default function SignupSuccess() {
  return (
    <div style={{ maxWidth: '500px', margin: '2rem auto', padding: '1rem' }}>
      <wa-card>
        <div slot="header">
          <h1 style={{ margin: 0 }}>Check Your Email</h1>
        </div>

        <wa-callout variant="success" open>
          <wa-icon slot="icon" name="check-circle" />
          <strong>Account created successfully!</strong>
        </wa-callout>

        <div style={{ marginTop: '1.5rem' }}>
          <p>
            We've sent a verification email to your inbox. Please click the link in the email to verify your account and activate it.
          </p>
          <p>
            The verification link will expire in 24 hours.
          </p>
          <p style={{ color: '#666', fontSize: '0.9rem' }}>
            Didn't receive the email? Check your spam folder or contact support.
          </p>
        </div>

        <div slot="footer" style={{ textAlign: 'center' }}>
          <Link to="/login">
            <wa-button variant="primary">
              Go to Login
            </wa-button>
          </Link>
        </div>
      </wa-card>
    </div>
  )
}

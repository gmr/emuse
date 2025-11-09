import { Link } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faFeatherPointed } from '@fortawesome/pro-solid-svg-icons'
import '@awesome.me/webawesome/dist/components/card/card.js'
import '@awesome.me/webawesome/dist/components/button/button.js'

export default function Home() {
  return (
    <div style={{ maxWidth: '800px', margin: '2rem auto', padding: '1rem' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <FontAwesomeIcon icon={faFeatherPointed} size="3x" style={{ color: '#6366f1' }} />
        <h1 style={{ marginTop: '1rem', fontSize: '2.5rem' }}>eMuse</h1>
        <p style={{ fontSize: '1.2rem', color: '#64748b' }}>
          A poetry sharing platform
        </p>
      </div>

      <wa-card>
        <div slot="header">
          <h2 style={{ margin: 0 }}>Welcome</h2>
        </div>

        <p>
          Share your poetry with the world. Connect with other poets,
          discover new works, and let your creativity flow.
        </p>

        <div slot="footer" style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <Link to="/login" style={{ textDecoration: 'none' }}>
            <wa-button variant="brand" size="medium">
              Login
            </wa-button>
          </Link>
          <wa-button variant="default" size="medium">
            Sign Up
          </wa-button>
        </div>
      </wa-card>
    </div>
  )
}

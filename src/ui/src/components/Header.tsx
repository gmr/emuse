import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const buttonStyle = {
  backgroundColor: 'white',
  color: '#800020',
  border: '1px solid white',
  borderRadius: '4px',
  padding: '0.5rem 1rem',
  fontSize: '0.875rem',
  fontWeight: '500',
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  textDecoration: 'none',
  display: 'inline-block',
}

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <header style={{
      width: '100%',
      padding: '1rem 2rem',
      backgroundColor: '#800020',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      margin: 0
    }}>
      <Link to="/" style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        textDecoration: 'none',
        color: 'white'
      }}>
        <img src="/static/logo.svg" alt="eMuse Logo" style={{ height: '40px', width: 'auto' }} />
      </Link>
      <nav style={{ display: 'flex', gap: '1rem', alignItems: 'center', color: 'white' }}>
        {isAuthenticated ? (
          <>
            <span style={{ color: 'rgba(255, 255, 255, 0.9)' }}>Welcome, {user?.display_name || user?.first_name}</span>
            <button
              onClick={handleLogout}
              style={buttonStyle}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.9)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'white'
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" style={buttonStyle}>
              Login
            </Link>
            <Link to="/signup" style={buttonStyle}>
              Sign Up
            </Link>
          </>
        )}
      </nav>
    </header>
  )
}

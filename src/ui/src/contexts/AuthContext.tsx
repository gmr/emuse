import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

interface User {
  id: string
  signup_at: string
  last_login_at: string | null
  first_name: string
  surname: string
  display_name: string
  email: string
  date_of_birth: string | null
  locale: string
  timezone: string
  activated: boolean
  locked: boolean
  memorial: boolean
  administrator: boolean
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  checkSession: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const queryClient = useQueryClient()

  // Check session on mount and periodically
  const { data: sessionData, isLoading: sessionLoading } = useQuery({
    queryKey: ['session'],
    queryFn: async () => {
      const response = await fetch('/api/me', {
        credentials: 'include',
      })
      if (!response.ok) {
        if (response.status === 401) {
          return null
        }
        throw new Error('Failed to check session')
      }
      return response.json()
    },
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Update user state when session data changes
  useEffect(() => {
    setUser(sessionData || null)
  }, [sessionData])

  const loginMutation = useMutation({
    mutationFn: async (credentials: { email: string; password: string }) => {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
        credentials: 'include',
      })

      if (!response.ok) {
        throw new Error('Login failed')
      }

      return response.json()
    },
    onSuccess: (data) => {
      setUser(data)
      queryClient.setQueryData(['session'], data)
    },
  })

  const logoutMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/logout', {
        credentials: 'include',
      })

      if (!response.ok) {
        throw new Error('Logout failed')
      }
    },
    onSuccess: () => {
      setUser(null)
      queryClient.setQueryData(['session'], null)
      // Clear only session-related queries instead of entire cache
      queryClient.removeQueries({ queryKey: ['session'] })
    },
  })

  const login = async (email: string, password: string) => {
    await loginMutation.mutateAsync({ email, password })
  }

  const logout = async () => {
    await logoutMutation.mutateAsync()
  }

  const checkSession = async () => {
    await queryClient.invalidateQueries({ queryKey: ['session'] })
  }

  const value = {
    user,
    isLoading: sessionLoading || loginMutation.isPending || logoutMutation.isPending,
    isAuthenticated: !!user,
    login,
    logout,
    checkSession,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

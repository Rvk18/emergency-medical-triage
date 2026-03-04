const TOKEN_KEY = 'medtriage_admin_token'
const ROLE_KEY = 'medtriage_admin_role'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(ROLE_KEY)
}

export function getRole(): string {
  return localStorage.getItem(ROLE_KEY) || 'Admin'
}

export function setRole(role: string): void {
  localStorage.setItem(ROLE_KEY, role)
}

export function isLoggedIn(): boolean {
  return !!getToken()
}

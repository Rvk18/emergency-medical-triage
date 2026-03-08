import { Routes, Route, NavLink, useNavigate } from 'react-router-dom'
import { getRole, clearAuth } from '../store/auth'
import { Button } from '@/components/ui/button'
import {
  LayoutDashboard,
  Users,
  Building2,
  FileText,
  Settings,
  LogOut,
  Stethoscope,
} from 'lucide-react'
import Dashboard from './admin/Dashboard'
import UsersPage from './admin/Users'
import Hospitals from './admin/Hospitals'
import Cases from './admin/Cases'
import SettingsPage from './admin/Settings'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/users', label: 'Users', icon: Users },
  { to: '/hospitals', label: 'Hospitals', icon: Building2 },
  { to: '/cases', label: 'Cases / Audit', icon: FileText },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export default function AppShell() {
  const navigate = useNavigate()
  const role = getRole()

  const handleLogout = () => {
    clearAuth()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen flex bg-background">
      <aside className="w-64 border-r bg-card flex flex-col">
        <div className="p-6 border-b">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Stethoscope className="h-5 w-5" />
            </div>
            <span className="font-semibold text-lg tracking-tight">MedTriage</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">Admin</p>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                }`
              }
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t space-y-2">
          <p className="px-3 text-xs text-muted-foreground">{role}</p>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start text-muted-foreground hover:text-destructive"
            onClick={handleLogout}
          >
            <LogOut className="h-4 w-4 mr-2" />
            Log out
          </Button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <div className="container max-w-5xl py-8 px-6">
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/hospitals" element={<Hospitals />} />
            <Route path="/cases" element={<Cases />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}

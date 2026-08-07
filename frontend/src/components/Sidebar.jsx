import { NavLink } from 'react-router-dom'
import { X, LayoutDashboard, Users, Settings, Server, Radio } from 'lucide-react'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/inbounds', label: 'Inbounds', icon: Radio },
  { to: '/users', label: 'Admins', icon: Users },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar({ isOpen, onClose }) {
  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-surface border-r border-slate-700 transform transition-transform duration-300 lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-6 flex items-center justify-between border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
              <Server className="text-white" size={22} />
            </div>
            <span className="text-lg font-bold text-white">AnishtayiN</span>
          </div>
          <button onClick={onClose} className="lg:hidden text-slate-400">
            <X size={20} />
          </button>
        </div>

        <nav className="p-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                  isActive
                    ? 'bg-primary/20 text-primary font-medium'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`
              }
              onClick={onClose}
            >
              <Icon size={20} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-700">
          <div className="bg-gradient-to-r from-primary/10 to-accent/10 rounded-xl p-4">
            <p className="text-xs text-slate-400">Version</p>
            <p className="text-sm font-bold text-white mt-1">1.0.0</p>
          </div>
        </div>
      </aside>
    </>
  )
}

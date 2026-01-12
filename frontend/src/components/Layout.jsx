import { useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Target, Briefcase, FileText, User, Menu, X, LogOut, Sun, Moon, GitCompare } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

const navItems = [
    { path: '/', label: 'Analyze', icon: Target },
    { path: '/jobs', label: 'Jobs', icon: Briefcase },
    { path: '/cover-letters', label: 'Cover Letters', icon: FileText },
    { path: '/profiles', label: 'Profiles', icon: User },
    { path: '/discrepancy', label: 'Discrepancy', icon: GitCompare },
]

export default function Layout() {
    const [mobileOpen, setMobileOpen] = useState(false)
    const location = useLocation()
    const navigate = useNavigate()
    const { logout, user } = useAuth()
    const { theme, toggleTheme } = useTheme()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <div className="min-h-screen transition-colors duration-300">
            {/* Header */}
            <header className="sticky top-0 z-50 h-16 bg-[var(--bg-primary)]/80 backdrop-blur-xl border-b border-[var(--glass-border)] transition-colors duration-300">
                <div className="h-full max-w-7xl mx-auto px-4 lg:px-8 flex items-center justify-between">
                    {/* Logo */}
                    <NavLink to="/" className="flex items-center gap-2">
                        <img src="/logo.png" alt="Wand" className="h-8 w-8" />
                        <span className="text-2xl font-bold gradient-text">
                            Wand
                        </span>
                    </NavLink>

                    {/* Desktop Nav */}
                    <nav className="hidden md:flex items-center gap-6">
                        <div className="flex items-center gap-1">
                            {navItems.map(({ path, label, icon: Icon }) => (
                                <NavLink
                                    key={path}
                                    to={path}
                                    className={({ isActive }) =>
                                        `relative px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${isActive ? 'text-[var(--text-primary)]' : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                                        }`
                                    }
                                >
                                    {({ isActive }) => (
                                        <>
                                            {isActive && (
                                                <motion.div
                                                    layoutId="activeNav"
                                                    className="absolute inset-0 bg-[var(--glass-hover)] rounded-lg"
                                                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                                                />
                                            )}
                                            <Icon className={`w-4 h-4 relative z-10 ${isActive ? 'text-blue-400' : ''}`} />
                                            <span className="relative z-10 text-sm font-medium">{label}</span>
                                        </>
                                    )}
                                </NavLink>
                            ))}
                        </div>

                        {/* Theme Toggle & User */}
                        <div className="flex items-center gap-4 pl-4 border-l border-[var(--glass-border)]">
                            <button
                                onClick={toggleTheme}
                                className="p-2 rounded-lg text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--glass-hover)] transition-colors"
                            >
                                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                            </button>

                            <div className="text-right hidden lg:block">
                                <p className="text-sm font-medium text-[var(--text-primary)]">{user?.name || 'User'}</p>
                                <p className="text-xs text-[var(--text-secondary)]">{user?.email}</p>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="p-2 rounded-lg text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--glass-hover)] transition-colors"
                                title="Sign out"
                            >
                                <LogOut className="w-5 h-5" />
                            </button>
                        </div>
                    </nav>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setMobileOpen(!mobileOpen)}
                        className="md:hidden p-2 rounded-lg hover:bg-[var(--glass-hover)] text-[var(--text-secondary)]"
                    >
                        {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                    </button>
                </div>

                {/* Mobile Nav */}
                <AnimatePresence>
                    {mobileOpen && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="md:hidden absolute top-16 left-0 right-0 bg-[var(--bg-secondary)]/95 backdrop-blur-xl border-b border-[var(--glass-border)] p-4"
                        >
                            {navItems.map(({ path, label, icon: Icon }) => (
                                <NavLink
                                    key={path}
                                    to={path}
                                    onClick={() => setMobileOpen(false)}
                                    className={({ isActive }) =>
                                        `flex items-center gap-3 px-4 py-3 rounded-lg mb-1 ${isActive ? 'bg-[var(--glass-hover)] text-[var(--text-primary)]' : 'text-[var(--text-secondary)] hover:bg-[var(--glass-hover)]'
                                        }`
                                    }
                                >
                                    <Icon className="w-5 h-5" />
                                    <span className="font-medium">{label}</span>
                                </NavLink>
                            ))}

                            <hr className="my-2 border-[var(--glass-border)]" />

                            <button
                                onClick={toggleTheme}
                                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--glass-hover)]"
                            >
                                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                                <span className="font-medium">{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
                            </button>

                            <button
                                onClick={() => {
                                    setMobileOpen(false)
                                    handleLogout()
                                }}
                                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg mt-2 text-red-400 hover:bg-red-500/10"
                            >
                                <LogOut className="w-5 h-5" />
                                <span className="font-medium">Sign Out</span>
                            </button>
                        </motion.div>
                    )}
                </AnimatePresence>
            </header>

            {/* Page Content */}
            <main className="max-w-7xl mx-auto px-4 lg:px-8 py-8 text-[var(--text-primary)]">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={location.pathname}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.2 }}
                    >
                        <Outlet />
                    </motion.div>
                </AnimatePresence>
            </main>
        </div>
    )
}

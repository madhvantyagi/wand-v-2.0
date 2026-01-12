import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'sonner'
import { ThemeProvider } from './context/ThemeContext'
import { AuthProvider } from './context/AuthContext'
import { UploadProvider } from './context/UploadContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import JobDetail from './pages/JobDetail'
import CoverLetters from './pages/CoverLetters'
import Profiles from './pages/Profiles'
import Discrepancy from './pages/Discrepancy'
import Login from './pages/Login'
import Register from './pages/Register'

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <UploadProvider>
          <BrowserRouter>
            <Toaster position="bottom-right" richColors />
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Protected routes */}
              <Route element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }>
                <Route path="/" element={<Dashboard />} />
                <Route path="/jobs" element={<Jobs />} />
                <Route path="/jobs/:id" element={<JobDetail />} />
                <Route path="/cover-letters" element={<CoverLetters />} />
                <Route path="/profiles" element={<Profiles />} />
                <Route path="/discrepancy" element={<Discrepancy />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </UploadProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import { Briefcase, Search, Calendar, ChevronRight, Plus, Trash2, AlertTriangle, Loader2, CheckCircle, Code, StickyNote } from 'lucide-react'
import { toast } from 'sonner'
import { jobApi } from '../api/client'

export default function Jobs() {
    const navigate = useNavigate()
    const [searchTerm, setSearchTerm] = useState('')
    // Initialize filter from localStorage or default to 'all'
    const [statusFilter, setStatusFilter] = useState(() => {
        return localStorage.getItem('jobStatusFilter') || 'all'
    })
    const [jobs, setJobs] = useState([])
    const [loading, setLoading] = useState(true)
    const [deleteJob, setDeleteJob] = useState(null)

    // Update localStorage when filter changes
    useEffect(() => {
        localStorage.setItem('jobStatusFilter', statusFilter)
    }, [statusFilter])

    // Load jobs from API
    useEffect(() => {
        loadJobs()
    }, [])

    const loadJobs = async () => {
        try {
            const jobList = await jobApi.list()
            setJobs(jobList)
        } catch (error) {
            console.error('Failed to load jobs:', error)
            toast.error('Failed to load jobs')
        } finally {
            setLoading(false)
        }
    }

    const filteredJobs = jobs.filter(job => {
        const matchesSearch = job.job_title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            job.company_name?.toLowerCase().includes(searchTerm.toLowerCase())

        if (statusFilter === 'all') return matchesSearch

        const status = job.application_status || 'saved'
        return matchesSearch && status === statusFilter
    })

    const openDeleteDialog = (e, job) => {
        e.stopPropagation()
        setDeleteJob(job)
    }

    const confirmDelete = async () => {
        if (!deleteJob) return

        try {
            await jobApi.delete(deleteJob.id)
            setJobs(jobs.filter(j => j.id !== deleteJob.id))
            toast.success('Job deleted')
        } catch (error) {
            toast.error('Failed to delete job')
        }
        setDeleteJob(null)
    }

    const getScoreStyle = (score) => {
        if (score >= 80) return { background: 'rgba(16, 185, 129, 0.15)', color: '#10b981', borderColor: 'rgba(16, 185, 129, 0.3)' }
        if (score >= 60) return { background: 'rgba(59, 130, 246, 0.15)', color: '#3b82f6', borderColor: 'rgba(59, 130, 246, 0.3)' }
        if (score >= 40) return { background: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b', borderColor: 'rgba(245, 158, 11, 0.3)' }
        return { background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', borderColor: 'rgba(239, 68, 68, 0.3)' }
    }

    const getApplicationStatus = (status) => {
        const statusConfig = {
            applied: { label: 'Applied', color: '#10b981', bg: 'rgba(16, 185, 129, 0.15)', icon: CheckCircle },
            interviewing: { label: 'Interviewing', color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.15)', icon: CheckCircle },
            offer: { label: 'Offer', color: '#06b6d4', bg: 'rgba(6, 182, 212, 0.15)', icon: CheckCircle },
            rejected: { label: 'Rejected', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.15)', icon: null },
            saved: { label: 'Tracked', color: '#6b7280', bg: 'rgba(107, 114, 128, 0.15)', icon: null }
        }
        return statusConfig[status] || null
    }


    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
            </div>
        )
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-1">Saved Jobs</h1>
                    <p className="text-[var(--text-secondary)]">
                        {filteredJobs.length} {filteredJobs.length === 1 ? 'job' : 'jobs'}
                        {statusFilter !== 'all' || searchTerm ? ' found' : ' analyzed'}
                    </p>
                </div>
                <Link to="/" className="btn-primary">
                    <Plus className="w-4 h-4" />
                    Analyze New Job
                </Link>
            </div>

            {/* Search */}
            {/* Search and Filters */}
            <div className="space-y-4">
                <div className="relative max-w-md">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]" />
                    <input
                        type="text"
                        placeholder="Search jobs..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-11 w-full"
                        style={{ paddingLeft: '4rem' }}
                    />
                </div>

                {/* Status Filters */}
                <div className="flex flex-wrap gap-2">
                    {['all', 'saved', 'applied', 'interviewing', 'offer', 'rejected'].map(status => {
                        const isActive = statusFilter === status
                        let label = 'All Jobs'
                        let color = 'var(--text-secondary)'
                        let bg = 'transparent'

                        if (status !== 'all') {
                            const config = getApplicationStatus(status)
                            if (config) {
                                label = config.label
                                color = config.color
                                bg = config.bg
                            }
                        } else {
                            color = 'var(--text-primary)'
                            bg = 'var(--glass-bg)'
                        }

                        return (
                            <button
                                key={status}
                                onClick={() => setStatusFilter(status)}
                                className={`px-4 py-1.5 rounded-full text-xs font-medium border transition-all ${isActive ? '' : 'border-[var(--glass-border)] hover:border-[var(--text-tertiary)]'
                                    }`}
                                style={isActive ? {
                                    backgroundColor: status === 'all' ? 'var(--text-primary)' : bg,
                                    color: status === 'all' ? 'var(--bg-primary)' : color,
                                    borderColor: status === 'all' ? 'transparent' : color
                                } : {
                                    backgroundColor: 'transparent',
                                    color: 'var(--text-secondary)'
                                }}
                            >
                                {label}
                            </button>
                        )
                    })}
                </div>
            </div>

            {/* Jobs List */}
            {filteredJobs.length === 0 ? (
                <div className="text-center py-20">
                    <div className="w-16 h-16 rounded-full bg-[var(--glass-hover)] flex items-center justify-center mx-auto mb-4">
                        <Briefcase className="w-8 h-8 text-[var(--text-tertiary)]" />
                    </div>
                    <h3 className="text-lg font-medium text-[var(--text-secondary)] mb-2">
                        {jobs.length === 0 ? 'No jobs yet' : 'No jobs found'}
                    </h3>
                    <p className="text-[var(--text-tertiary)] mb-6">
                        {jobs.length === 0 ? 'Analyze your first job to get started' : 'Try a different search term'}
                    </p>
                    {jobs.length === 0 && (
                        <Link to="/" className="btn-primary inline-flex">
                            <Plus className="w-4 h-4" />
                            Analyze First Job
                        </Link>
                    )}
                </div>
            ) : (
                <div className="grid gap-4">
                    {filteredJobs.map((job, index) => {
                        const appStatus = getApplicationStatus(job.application_status)
                        const techSkills = job.parsed_data?.technical_skills || []
                        const matchScore = job.match_score

                        return (
                            <motion.div
                                key={job.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.05 }}
                                onClick={() => navigate(`/jobs/${job.id}`)}
                                className="cursor-pointer"
                            >
                                <div className="glass-card group hover:border-blue-500/30 transition-all duration-200">
                                    <div className="flex items-start gap-4">
                                        {/* Icon */}
                                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/20 flex items-center justify-center flex-shrink-0">
                                            <Briefcase className="w-5 h-5 text-blue-400" />
                                        </div>

                                        {/* Main Content */}
                                        <div className="flex-1 min-w-0 space-y-2">
                                            {/* Title Row */}
                                            <div className="flex items-start justify-between gap-3">
                                                <div className="min-w-0">
                                                    <h3 className="font-semibold text-[var(--text-primary)] truncate group-hover:text-blue-400 transition-colors">
                                                        {job.job_title || 'Untitled Position'}
                                                    </h3>
                                                    <p className="text-sm text-[var(--text-secondary)] truncate">{job.company_name || 'Unknown Company'}</p>
                                                </div>

                                                {/* Right side badges */}
                                                <div className="flex items-center gap-2 flex-shrink-0">
                                                    {/* Match Score */}
                                                    {matchScore != null && (
                                                        <div
                                                            className="px-2.5 py-1 rounded-full text-xs font-semibold border"
                                                            style={getScoreStyle(matchScore)}
                                                        >
                                                            {matchScore}% Match
                                                        </div>
                                                    )}

                                                    {/* Application Status */}
                                                    {appStatus && appStatus.label !== 'Saved' && (
                                                        <div
                                                            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
                                                            style={{ background: appStatus.bg, color: appStatus.color }}
                                                        >
                                                            {appStatus.icon && <appStatus.icon className="w-3 h-3" />}
                                                            {appStatus.label}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>

                                            {/* Tech Skills Row */}
                                            {techSkills.length > 0 && (
                                                <div className="flex items-center gap-2 flex-wrap">
                                                    <Code className="w-3.5 h-3.5 text-[var(--text-tertiary)] flex-shrink-0" />
                                                    <div className="flex items-center gap-1.5 flex-wrap">
                                                        {techSkills.slice(0, 5).map((skill, idx) => (
                                                            <span
                                                                key={idx}
                                                                className="px-2 py-0.5 rounded-md text-xs bg-[var(--glass-hover)] text-[var(--text-secondary)] border border-[var(--glass-border)]"
                                                            >
                                                                {skill}
                                                            </span>
                                                        ))}
                                                        {techSkills.length > 5 && (
                                                            <span className="text-xs text-[var(--text-tertiary)]">
                                                                +{techSkills.length - 5} more
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                            )}
                                            {/* Notes */}
                                            {job.application_notes && (
                                                <div className="mt-3 pt-3 border-t border-[var(--glass-border)] flex items-start gap-2">
                                                    <StickyNote className="w-3 h-3 text-yellow-400/70 mt-0.5 flex-shrink-0" />
                                                    <p className="text-[10px] text-[var(--text-secondary)] line-clamp-2 italic">
                                                        {job.application_notes}
                                                    </p>
                                                </div>
                                            )}
                                        </div>

                                        {/* Actions */}
                                        <div className="flex items-center gap-2 flex-shrink-0">
                                            {/* Date */}
                                            <div className="hidden sm:flex items-center gap-1.5 text-xs text-[var(--text-tertiary)]">
                                                <Calendar className="w-3.5 h-3.5" />
                                                {new Date(job.created_at).toLocaleDateString()}
                                            </div>

                                            {/* Delete Button */}
                                            <button
                                                onClick={(e) => openDeleteDialog(e, job)}
                                                className="p-2 rounded-lg text-[var(--text-tertiary)] hover:text-red-400 hover:bg-red-500/10 transition-colors"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>

                                            {/* Arrow */}
                                            <ChevronRight className="w-5 h-5 text-[var(--text-tertiary)] group-hover:text-blue-400 transition-colors" />
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        )
                    })}

                </div>
            )}

            {/* Delete Confirmation Dialog */}
            {deleteJob && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
                    onClick={() => setDeleteJob(null)}
                >
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="w-full max-w-sm glass-card border-[var(--glass-border)] rounded-2xl p-6"
                        style={{ background: 'var(--bg-secondary)' }}
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: 'var(--bg-error)' }}>
                                <AlertTriangle className="w-5 h-5" style={{ color: 'var(--color-error)' }} />
                            </div>
                            <h3 className="text-lg font-semibold text-[var(--text-primary)]">Delete Job?</h3>
                        </div>
                        <p className="text-[var(--text-secondary)] mb-6">
                            This will permanently remove '{deleteJob.job_title}' from your saved jobs.
                        </p>
                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={() => setDeleteJob(null)}
                                className="btn-secondary"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmDelete}
                                className="px-4 py-2 rounded-xl bg-red-500 hover:bg-red-600 text-white font-medium transition-colors"
                            >
                                Delete
                            </button>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </div>
    )
}

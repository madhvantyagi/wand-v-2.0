import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Briefcase, Search, Calendar, ChevronRight, Plus, Trash2, AlertTriangle, Loader2, CheckCircle, Code, StickyNote, XCircle, ArrowRight, Clock, Sparkles, Clipboard, ChevronDown, ChevronUp } from 'lucide-react'
import { toast } from 'sonner'
import { profileApi, analyzeApi } from '../api/client'
import { useAnalysis } from '../context/AnalysisContext'

export default function Dashboard() {
    const navigate = useNavigate()
    const [jobText, setJobText] = useState('')
    const [companyInfo, setCompanyInfo] = useState('')
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [analysis, setAnalysis] = useState(null)
    const [profiles, setProfiles] = useState([])
    const [loadingProfiles, setLoadingProfiles] = useState(true)
    const textareaRef = useRef(null)

    // Global Analysis Context
    const {
        analysisTasks,
        activeTasks,
        recentTasks,
        isQueueOpen,
        setIsQueueOpen,
        isConnected,
        loadTasks,
        addAnalysisTask,
        handleDeleteTask,
        handleClearTasks
    } = useAnalysis()

    // Load profiles on mount (tasks handled by context)
    useEffect(() => {
        loadProfiles()
        setTimeout(() => textareaRef.current?.focus(), 100)
    }, [])


    // Clear tasks handled by context
    const [showConfirm, setShowConfirm] = useState(false)

    const confirmClearTasks = async () => {
        try {
            await handleClearTasks()
            setShowConfirm(false)
        } catch (error) {
            setShowConfirm(false)
        }
    }

    const loadProfiles = async () => {
        try {
            const profileList = await profileApi.list()
            setProfiles(profileList)
        } catch (error) {
            console.error('Failed to load profiles:', error)
        } finally {
            setLoadingProfiles(false)
        }
    }

    const handlePasteFromClipboard = async () => {
        try {
            const text = await navigator.clipboard.readText()
            if (text) {
                setJobText(text)
                toast.success('Pasted from clipboard')
            } else {
                toast.error('Clipboard is empty')
            }
        } catch (error) {
            toast.error('Unable to access clipboard. Please paste manually.')
        }
    }

    const handleAnalyze = async () => {
        if (!jobText.trim()) {
            toast.error('Please paste a job description')
            return
        }

        if (profiles.length === 0) {
            toast.error('Please upload at least one profile first')
            return
        }

        // Ensure WebSocket is connected
        if (!isConnected) {
            console.warn('WebSocket not connected, analysis will proceed but updates may not show')
        }

        setIsAnalyzing(true)
        setAnalysis(null)

        try {
            const profileIds = profiles.map(p => p.id)
            const companyName = companyInfo || null

            const result = await analyzeApi.analyze(jobText, profileIds, companyName)

            // Add to global context queue
            const newTask = {
                task_id: result.task_id,
                status: 'pending',
                progress_message: 'Queued for analysis...',
                progress: 0,
                company_name: companyName,
                created_at: new Date().toISOString()
            }
            addAnalysisTask(newTask)

            // Show initial toast
            toast.loading('Queued for analysis...', { id: `task - ${result.task_id} ` })

            // Clear input for next job
            setJobText('')
            setCompanyInfo('')
            setIsAnalyzing(false)

            // Analysis will continue in background via context
        } catch (error) {
            console.error('Analysis failed:', error)
            toast.error(error.message || 'Failed to start analysis')
            setIsAnalyzing(false)
        }
    }

    const getScoreColor = (score) => {
        if (score >= 80) return '#10B981'
        if (score >= 60) return '#3B82F6'
        if (score >= 40) return '#F59E0B'
        return '#EF4444'
    }

    const gap = analysis?.gapAnalysis

    // Tasks are filtered in context logic, but we can verify here if needed
    // Using filtered lists from context directly

    const getStatusIcon = (status) => {
        switch (status) {
            case 'complete': return <CheckCircle className="w-4 h-4 text-green-500" />
            case 'failed': return <XCircle className="w-4 h-4 text-red-500" />
            case 'pending': return <Clock className="w-4 h-4 text-gray-400" />
            default: return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
        }
    }

    const getStatusLabel = (status) => {
        const labels = {
            pending: 'Queued',
            parsing: 'Parsing',
            intel: 'Intel',
            analyzing: 'Analyzing',
            optimizing: 'Optimizing',
            complete: 'Complete',
            failed: 'Failed'
        }
        return labels[status] || status
    }

    return (
        <div className="max-w-5xl mx-auto space-y-8">
            {/* Hero */}
            <div className="text-center py-6">
                <motion.h1
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-4xl lg:text-5xl font-bold mb-3"
                >
                    <span className="gradient-text">Analyze Job Match</span>
                </motion.h1>
                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.1 }}
                    className="text-[var(--text-secondary)] text-lg"
                >
                    Get comprehensive AI-powered insights for your job application
                </motion.p>
            </div>

            {/* Analysis Queue */}
            {analysisTasks.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-card p-4 transition-all duration-300"
                >
                    <div
                        className="flex items-center justify-between cursor-pointer"
                        onClick={() => setIsQueueOpen(!isQueueOpen)}
                    >
                        <h3 className="font-semibold flex items-center gap-2">
                            <Clock className="w-4 h-4" />
                            Analysis Queue
                            {/* Status Dot */}
                            <div
                                className={`w-2 h-2 rounded-full transition-colors duration-300 ${isConnected ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-red-500'}`}
                                title={isConnected ? 'Connected' : 'Disconnected'}
                            />

                            {activeTasks.length > 0 && (
                                <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400">
                                    {activeTasks.length} active
                                </span>
                            )}
                        </h3>
                        <div className="flex items-center gap-3">
                            <button
                                onClick={(e) => {
                                    e.stopPropagation()
                                    setShowConfirm(true) // Open confirmation
                                }}
                                className="text-xs text-[var(--text-tertiary)] hover:text-red-400 px-2 py-1 rounded hover:bg-red-500/10 transition-colors"
                            >
                                Clear All
                            </button>
                        </div>
                        {isQueueOpen ? (
                            <ChevronUp className="w-4 h-4 text-[var(--text-tertiary)]" />
                        ) : (
                            <ChevronDown className="w-4 h-4 text-[var(--text-tertiary)]" />
                        )}
                    </div>

                    <AnimatePresence>
                        {isQueueOpen && (
                            <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                overflow="hidden"
                                className="space-y-2 mt-4"
                            >
                                <AnimatePresence>
                                    {activeTasks.map(task => (
                                        <motion.div
                                            key={task.task_id}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            exit={{ opacity: 0, x: 20 }}
                                            className="flex items-center gap-3 p-3 rounded-lg bg-[var(--bg-secondary)] border border-[var(--border-primary)] group"
                                        >
                                            {/* Status Icon */}
                                            <div className="mt-1">
                                                {task.status === 'processing' || task.status === 'parsing' || task.status === 'analyzing' ? (
                                                    <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                                                ) : task.status === 'complete' ? (
                                                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                                                ) : (
                                                    <XCircle className="w-5 h-5 text-red-400" />
                                                )}
                                            </div>

                                            {/* Content */}
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center justify-between gap-2">
                                                    <p className="text-sm font-medium text-slate-200 truncate">
                                                        {task.job_title || task.company_name || 'Job Analysis'}
                                                    </p>
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation()
                                                            handleDeleteTask(task.task_id)
                                                        }}
                                                        className="p-1 text-slate-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                                                        title="Remove from queue"
                                                    >
                                                        <XCircle className="w-4 h-4" />
                                                    </button>
                                                </div>
                                                <div className="flex items-center justify-between mt-1">
                                                    <p className="text-xs text-[var(--text-secondary)] truncate max-w-[200px]">
                                                        {task.progress_message || task.status}
                                                    </p>
                                                    <span className="text-xs font-medium text-slate-500">
                                                        {task.progress}%
                                                    </span>
                                                </div>
                                                <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden mt-2">
                                                    <motion.div
                                                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                                                        initial={{ width: 0 }}
                                                        animate={{ width: `${task.progress}% ` }}
                                                        transition={{ duration: 0.3 }}
                                                    />
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))}
                                </AnimatePresence>

                                {recentTasks.length > 0 && activeTasks.length > 0 && (
                                    <div className="border-t border-[var(--border-primary)] my-2" />
                                )}

                                {recentTasks.map(task => (
                                    <div
                                        key={task.task_id}
                                        className="flex items-center gap-3 p-2 rounded-lg opacity-60 hover:opacity-100 transition-opacity cursor-pointer hover:bg-[var(--bg-secondary)] group"
                                        onClick={() => task.result_job_id && navigate(`/ jobs / ${task.result_job_id} `)}
                                    >
                                        {getStatusIcon(task.status)}
                                        <span className="text-sm truncate flex-1">
                                            {task.job_title || task.company_name || 'Job Analysis'}
                                        </span>
                                        {task.total_duration && (
                                            <span className="text-xs text-[var(--text-tertiary)] font-mono mr-2 hidden sm:inline-block">
                                                {task.total_duration < 60
                                                    ? `${Math.round(task.total_duration)} s`
                                                    : `${Math.floor(task.total_duration / 60)}m ${Math.round(task.total_duration % 60)} s`}
                                            </span>
                                        )}
                                        <span className="text-xs text-[var(--text-secondary)] mr-2">
                                            {getStatusLabel(task.status)}
                                        </span>
                                        <div className="flex items-center gap-2">
                                            {task.result_job_id && (
                                                <ArrowRight className="w-4 h-4 text-[var(--text-secondary)]" />
                                            )}
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation()
                                                    handleDeleteTask(task.task_id)
                                                }}
                                                className="p-1 text-slate-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                                                title="Remove from history"
                                            >
                                                <XCircle className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>
            )}

            {/* Profiles Status */}
            {!loadingProfiles && profiles.length === 0 && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="p-4 rounded-xl border flex items-center gap-3"
                    style={{ background: 'var(--bg-warning)', borderColor: 'var(--border-warning)' }}
                >
                    <AlertTriangle className="w-5 h-5 flex-shrink-0" style={{ color: 'var(--color-warning)' }} />
                    <div className="flex-1">
                        <p className="font-medium" style={{ color: 'var(--color-warning)' }}>No profiles uploaded</p>
                        <p className="text-sm opacity-80" style={{ color: 'var(--color-warning)' }}>Upload your resume or LinkedIn profile to enable job matching.</p>
                    </div>
                    <button onClick={() => navigate('/profiles')} className="btn-secondary" style={{ color: 'var(--color-warning)', borderColor: 'var(--border-warning)' }}>
                        Upload Profile
                    </button>
                </motion.div>
            )}


            {/* Input Section */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card space-y-6">
                <div>
                    <div className="flex items-center justify-between mb-2">
                        <label className="block text-sm font-medium text-[var(--text-secondary)]">Job Description *</label>
                        <button
                            onClick={handlePasteFromClipboard}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--glass-bg)] hover:bg-[var(--glass-hover)] border border-[var(--glass-border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                        >
                            <Clipboard className="w-3.5 h-3.5" />
                            Paste from Clipboard
                        </button>
                    </div>
                    <textarea
                        ref={textareaRef}
                        value={jobText}
                        onChange={(e) => setJobText(e.target.value)}
                        placeholder="Paste the complete job posting here..."
                        className="min-h-[180px]"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">Company Name (Optional)</label>
                    <input type="text" value={companyInfo} onChange={(e) => setCompanyInfo(e.target.value)} placeholder="Company name for additional intelligence..." />
                </div>
                <div className="flex justify-end gap-3">
                    <button
                        onClick={handleAnalyze}
                        disabled={!jobText.trim() || profiles.length === 0 || isAnalyzing}
                        className="btn-primary"
                    >
                        {isAnalyzing ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Sparkles className="w-4 h-4" />
                                Analyze Match
                            </>
                        )}
                    </button>
                </div>
            </motion.div>

            {/* Results Section */}
            {analysis && gap && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">

                    {/* Header with Match Score */}
                    <div className="glass-card">
                        <div className="flex flex-col md:flex-row items-center gap-6">
                            <div className="relative w-28 h-28 flex-shrink-0">
                                <svg className="w-full h-full -rotate-90" viewBox="0 0 112 112">
                                    <circle cx="56" cy="56" r="48" fill="none" stroke="var(--glass-border)" strokeWidth="8" />
                                    <circle cx="56" cy="56" r="48" fill="none" stroke={getScoreColor(analysis.matchScore)} strokeWidth="8" strokeLinecap="round" strokeDasharray={`${analysis.matchScore * 3.01} 301`} />
                                </svg>
                                <div className="absolute inset-0 flex flex-col items-center justify-center">
                                    <span className="text-3xl font-bold" style={{ color: getScoreColor(analysis.matchScore) }}>{analysis.matchScore}%</span>
                                    <span className="text-xs text-[var(--text-tertiary)]">Match</span>
                                </div>
                            </div>
                            <div className="flex-1 text-center md:text-left">
                                <h2 className="text-2xl font-bold text-[var(--text-primary)] mb-1">{analysis.jobTitle}</h2>
                                <p className="text-[var(--text-secondary)] mb-2">{analysis.company}</p>
                                {gap.job_description && <p className="text-sm text-[var(--text-tertiary)] mb-3">{gap.job_description}</p>}
                                <div className="flex gap-3 justify-center md:justify-start">
                                    <button onClick={() => navigate(`/ cover - letters ? jobId = ${analysis.id} `)} className="btn-primary">
                                        <FileText className="w-4 h-4" />Generate Cover Letter
                                    </button>
                                    <button onClick={() => navigate(`/ jobs / ${analysis.id} `)} className="btn-secondary">
                                        View Details<ArrowRight className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* About Company & Compensation */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {gap.about_company && (
                            <div className="glass-card">
                                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-3 flex items-center gap-2">
                                    <Building2 className="w-5 h-5 text-cyan-400" />About Company
                                </h3>
                                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{gap.about_company}</p>
                            </div>
                        )}
                        {gap.compensation && (
                            <div className="glass-card">
                                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-3 flex items-center gap-2">
                                    <DollarSign className="w-5 h-5 text-emerald-400" />Compensation & Benefits
                                </h3>
                                {(gap.compensation.salary_min || gap.compensation.salary_max) && (
                                    <p className="text-xl font-bold text-emerald-400 mb-2">
                                        ${gap.compensation.salary_min?.toLocaleString() || '?'}
                                        {gap.compensation.salary_max && gap.compensation.salary_max !== gap.compensation.salary_min && ` - $${gap.compensation.salary_max.toLocaleString()} `}
                                        <span className="text-sm text-[var(--text-tertiary)] font-normal ml-2">
                                            {gap.compensation.currency || 'USD'} / {gap.compensation.pay_type || 'yearly'}
                                        </span>
                                    </p>
                                )}
                                {gap.compensation.benefits?.length > 0 && (
                                    <div className="flex flex-wrap gap-1.5 mt-2">
                                        {gap.compensation.benefits.map((b, i) => (
                                            <span key={i} className="px-2 py-0.5 text-xs rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">{b}</span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Qualifications */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {gap.required_qualifications?.length > 0 && (
                            <div className="glass-card">
                                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-3 flex items-center gap-2">
                                    <CheckCircle className="w-5 h-5 text-emerald-400" />Required Qualifications
                                </h3>
                                <ul className="space-y-1">
                                    {gap.required_qualifications.map((q, i) => (
                                        <li key={i} className="text-sm text-[var(--text-secondary)] flex items-start gap-2"><span className="text-emerald-400">•</span>{q}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        {gap.preferred_qualifications?.length > 0 && (
                            <div className="glass-card">
                                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-3 flex items-center gap-2">
                                    <GraduationCap className="w-5 h-5 text-yellow-400" />Preferred Qualifications
                                </h3>
                                <ul className="space-y-1">
                                    {gap.preferred_qualifications.map((q, i) => (
                                        <li key={i} className="text-sm text-[var(--text-secondary)] flex items-start gap-2"><span className="text-yellow-400">•</span>{q}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>

                    {/* Technical Skills by Source */}
                    {gap.technical_skills && (
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                <Award className="w-5 h-5 text-purple-400" />Technical Skills
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {gap.technical_skills.job_posting?.length > 0 && (
                                    <div>
                                        <p className="text-xs text-[var(--text-tertiary)] mb-2 flex items-center gap-1">
                                            <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 text-xs border border-blue-500/20">Job Posting</span>
                                        </p>
                                        <div className="flex flex-wrap gap-1.5">
                                            {gap.technical_skills.job_posting.map((skill, i) => (
                                                <span key={i} className="px-2 py-0.5 text-xs rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">{skill}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                {gap.technical_skills.company_intel?.length > 0 && (
                                    <div>
                                        <p className="text-xs text-[var(--text-tertiary)] mb-2 flex items-center gap-1">
                                            <span className="px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-400 text-xs border border-cyan-500/20">Company Intel</span>
                                        </p>
                                        <div className="flex flex-wrap gap-1.5">
                                            {gap.technical_skills.company_intel.map((skill, i) => (
                                                <span key={i} className="px-2 py-0.5 text-xs rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">{skill}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Soft Skills by Source (4 Categories) */}
                    {gap.soft_skills && (
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                <Lightbulb className="w-5 h-5 text-orange-400" />Soft Skills
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {gap.soft_skills.job_posting_explicit?.length > 0 && (
                                    <div>
                                        <p className="text-xs text-[var(--text-tertiary)] mb-2 flex items-center gap-2">
                                            <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 text-xs border border-blue-500/20">Job Posting</span>
                                            <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-xs border border-emerald-500/20">Explicit</span>
                                        </p>
                                        <div className="flex flex-wrap gap-1.5">
                                            {gap.soft_skills.job_posting_explicit.map((skill, i) => (
                                                <span key={i} className="px-2 py-0.5 text-xs rounded bg-orange-500/20 text-orange-300 border border-orange-500/30">{skill}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                {gap.soft_skills.job_posting_implicit?.length > 0 && (
                                    <div>
                                        <p className="text-xs text-[var(--text-tertiary)] mb-2 flex items-center gap-2">
                                            <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 text-xs border border-blue-500/20">Job Posting</span>
                                            <span className="px-1.5 py-0.5 rounded bg-yellow-500/20 text-yellow-400 text-xs border border-yellow-500/20">Implicit</span>
                                        </p>
                                        <div className="flex flex-wrap gap-1.5">
                                            {gap.soft_skills.job_posting_implicit.map((skill, i) => (
                                                <span key={i} className="px-2 py-0.5 text-xs rounded bg-yellow-500/20 text-yellow-300 border border-yellow-500/30">{skill}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                {gap.soft_skills.company_intel_explicit?.length > 0 && (
                                    <div>
                                        <p className="text-xs text-[var(--text-tertiary)] mb-2 flex items-center gap-2">
                                            <span className="px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-400 text-xs border border-cyan-500/20">Company Intel</span>
                                            <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-xs border border-emerald-500/20">Explicit</span>
                                        </p>
                                        <div className="flex flex-wrap gap-1.5">
                                            {gap.soft_skills.company_intel_explicit.map((skill, i) => (
                                                <span key={i} className="px-2 py-0.5 text-xs rounded bg-teal-500/20 text-teal-300 border border-teal-500/30">{skill}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                {gap.soft_skills.company_intel_implicit?.length > 0 && (
                                    <div>
                                        <p className="text-xs text-[var(--text-tertiary)] mb-2 flex items-center gap-2">
                                            <span className="px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-400 text-xs border border-cyan-500/20">Company Intel</span>
                                            <span className="px-1.5 py-0.5 rounded bg-yellow-500/20 text-yellow-400 text-xs border border-yellow-500/20">Implicit</span>
                                        </p>
                                        <div className="flex flex-wrap gap-1.5">
                                            {gap.soft_skills.company_intel_implicit.map((skill, i) => (
                                                <span key={i} className="px-2 py-0.5 text-xs rounded bg-slate-500/20 text-slate-300 border border-slate-500/30">{skill}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Skill Comparison Table */}
                    {gap.skill_comparison?.length > 0 && (
                        <div className="glass-card overflow-hidden">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Skill Match Analysis</h3>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b border-[var(--glass-border)]">
                                            <th className="text-left py-3 px-4 text-[var(--text-tertiary)] font-medium">Skill</th>
                                            <th className="text-left py-3 px-4 text-[var(--text-tertiary)] font-medium">Type</th>
                                            <th className="text-left py-3 px-4 text-[var(--text-tertiary)] font-medium">Source</th>
                                            <th className="text-left py-3 px-4 text-[var(--text-tertiary)] font-medium">In Profile</th>
                                            <th className="text-left py-3 px-4 text-[var(--text-tertiary)] font-medium">Importance</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-[var(--glass-border)]">
                                        {gap.skill_comparison.map((item, i) => (
                                            <tr key={i} className="hover:bg-[var(--glass-hover)] transition-colors">
                                                <td className="py-3 px-4 text-[var(--text-primary)] font-medium">{item.skill}</td>
                                                <td className="py-3 px-4">
                                                    <span className={`px - 2 py - 1 rounded text - xs border ${item.type === 'hard' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 'bg-orange-500/10 text-orange-400 border-orange-500/20'} `}>
                                                        {item.type === 'hard' ? 'Hard' : 'Soft'}
                                                    </span>
                                                </td>
                                                <td className="py-3 px-4 text-[var(--text-secondary)] capitalize text-xs">{item.source?.replace('_', ' ')}</td>
                                                <td className="py-3 px-4">
                                                    {item.in_profile || item.status === 'matched' ? (
                                                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                                                    ) : (
                                                        <XCircle className="w-4 h-4 text-red-400/50" />
                                                    )}
                                                </td>
                                                <td className="py-3 px-4 text-[var(--text-secondary)] capitalize">{item.importance}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* Resume Improvements */}


                    {/* Recommendations */}
                    {gap.recommendations?.length > 0 && (
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                <Lightbulb className="w-5 h-5 text-yellow-400" />Recommendations
                            </h3>
                            <div className="space-y-3">
                                {gap.recommendations.map((rec, i) => (
                                    <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-[var(--input-bg)]">
                                        <div className="w-6 h-6 rounded-full bg-yellow-500/20 flex items-center justify-center flex-shrink-0">
                                            <span className="text-xs text-yellow-400 font-medium">{i + 1}</span>
                                        </div>
                                        <p className="text-sm text-[var(--text-secondary)]">{rec}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Company News */}
                    {analysis.companyIntel?.news?.headlines?.length > 0 && (
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                <Newspaper className="w-5 h-5 text-yellow-400" />Latest News
                            </h3>
                            <div className="space-y-3">
                                {analysis.companyIntel.news.headlines.slice(0, 5).map((news, i) => (
                                    <div key={i} className="p-3 rounded-xl bg-[var(--input-bg)]">
                                        <p className="text-sm text-[var(--text-secondary)]">{news.title || news}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </motion.div>
            )}
            {/* Confirmation Modal */}
            <AnimatePresence>
                {showConfirm && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
                        onClick={() => setShowConfirm(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            className="glass-card w-full max-w-sm p-6 space-y-4 shadow-2xl"
                            onClick={e => e.stopPropagation()}
                        >
                            <div className="flex items-center gap-3 text-red-400">
                                <div className="w-10 h-10 rounded-full bg-red-500/10 flex items-center justify-center">
                                    <AlertTriangle className="w-5 h-5" />
                                </div>
                                <h3 className="text-lg font-semibold text-[var(--text-primary)]">Clear History?</h3>
                            </div>

                            <p className="text-[var(--text-secondary)]">
                                Are you sure you want to delete all analysis history? This action cannot be undone.
                            </p>

                            <div className="flex justify-end gap-3 pt-2">
                                <button
                                    onClick={() => setShowConfirm(false)}
                                    className="px-4 py-2 text-sm font-medium rounded-lg hover:bg-[var(--bg-tertiary)] text-[var(--text-secondary)] transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={confirmClearTasks}
                                    className="px-4 py-2 text-sm font-medium rounded-lg bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/20 transition-all"
                                >
                                    Yes, Clear All
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}

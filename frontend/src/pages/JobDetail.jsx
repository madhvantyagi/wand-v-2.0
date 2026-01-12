import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
    ArrowLeft, FileText, CheckCircle, XCircle, Lightbulb,
    Building2, Newspaper, Briefcase, GraduationCap, Award,
    FolderOpen, Calendar, Trash2, AlertTriangle, Loader2, Eye,
    TrendingUp, HelpCircle, BadgeCheck, Edit3, Copy, History, Clock, ChevronRight
} from 'lucide-react'
import { toast } from 'sonner'
import { jobApi, matchApi, profileApi } from '../api/client'

export default function JobDetail() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [job, setJob] = useState(null)
    const [gapAnalysis, setGapAnalysis] = useState(null)

    // Core Data States
    const [loading, setLoading] = useState(true)
    const [analyzing, setAnalyzing] = useState(false)
    const [profiles, setProfiles] = useState([])
    const [coverLetters, setCoverLetters] = useState([])
    const [showDeleteDialog, setShowDeleteDialog] = useState(false)

    // Optimization States (New)
    const [optimizationData, setOptimizationData] = useState(null)
    const [optimizationLoading, setOptimizationLoading] = useState(false)
    const [optimizationError, setOptimizationError] = useState(null)

    // History State
    const [historyOpen, setHistoryOpen] = useState(false)
    const [historyData, setHistoryData] = useState([])
    const [historyLoading, setHistoryLoading] = useState(false)

    useEffect(() => {
        loadJobAndAnalysis()
        loadCoverLetters()
    }, [id])

    // Load optimization separately when profiles are ready
    useEffect(() => {
        if (profiles.length > 0 && id) {
            loadOptimization()
        }
    }, [profiles, id, job]) // Added job to dependencies

    const loadOptimization = async () => {
        if (!job || !profiles.length) return

        try {
            setOptimizationLoading(true)
            setOptimizationError(null)
            const resumeProfile = profiles.find(p => p.source_type === 'resume')
            if (!resumeProfile) {
                setOptimizationError('No resume profile found.')
                setOptimizationLoading(false)
                return
            }

            const data = await matchApi.optimizeResume(resumeProfile.id, job.id)
            setOptimizationData(data)
        } catch (error) {
            console.error('Optimization error:', error)
            setOptimizationError('Failed to load resume optimization.')
        } finally {
            setOptimizationLoading(false)
        }
    }

    const loadHistory = async () => {
        if (historyOpen) {
            setHistoryOpen(false)
            return
        }

        try {
            setHistoryLoading(true)
            setHistoryOpen(true)
            const data = await matchApi.getGapHistory(id)
            setHistoryData(data)
        } catch (error) {
            toast.error('Failed to load history')
        } finally {
            setHistoryLoading(false)
        }
    }

    const handleRestoreAnalysis = async (analysisId) => {
        setHistoryOpen(false)
        await loadJobAndAnalysis(analysisId)
        toast.success('Historical report loaded')
    }

    const loadJobAndAnalysis = async (analysisId = null) => {
        try {
            // Load job
            const jobData = await jobApi.get(id)
            setJob(jobData)

            // Load profiles
            const profilesList = await profileApi.list()
            setProfiles(profilesList)

            // Check if gap analysis already exists for this job or load specific one
            let existingAnalysis = null
            try {
                if (analysisId) {
                    existingAnalysis = await matchApi.get(analysisId)
                } else {
                    existingAnalysis = await matchApi.getByJobId(id)
                }

                if (existingAnalysis) {
                    console.log('✅ Loaded cached analysis', analysisId ? '(historical)' : '(current)')
                    setGapAnalysis(existingAnalysis)
                    setLoading(false)
                    return // Stop here - we have cached analysis, no need to re-run
                }
            } catch (error) {
                console.log('No cached analysis found, will run new analysis')
            }

            // Auto-run gap analysis ONLY if no existing analysis was found
            if (profilesList.length > 0 && !existingAnalysis) {
                setAnalyzing(true)
                try {
                    const profileIds = profilesList.map(p => p.id)
                    const analysis = await matchApi.analyzeGaps(profileIds, id)
                    setGapAnalysis(analysis)
                    console.log('✅ Created new gap analysis')
                } catch (error) {
                    console.error('Gap analysis failed:', error)
                    toast.error('Failed to analyze job match')
                } finally {
                    setAnalyzing(false)
                }
            }
        } catch (error) {
            console.error('Failed to load job:', error)
            setJob(null)
        } finally {
            setLoading(false)
        }
    }

    // ... render return ...

    const loadCoverLetters = async () => {
        try {
            const letters = await matchApi.listCoverLetters()
            setCoverLetters(letters.filter(l => l.job_id === id))
        } catch (error) {
            console.error('Failed to load cover letters:', error)
        }
    }

    const confirmDelete = async () => {
        try {
            await jobApi.delete(id)
            toast.success('Job deleted')
            navigate('/jobs')
        } catch (error) {
            toast.error('Failed to delete job')
        }
    }

    const getStatusIcon = (status) => {
        if (status === 'met' || status === 'matched') {
            return <CheckCircle className="w-4 h-4 text-emerald-400" />
        } else if (status === 'not_met' || status === 'missing') {
            return <XCircle className="w-4 h-4 text-red-400" />
        } else {
            return <HelpCircle className="w-4 h-4 text-yellow-400" />
        }
    }

    const getStatusColor = (status) => {
        if (status === 'met' || status === 'matched') return 'text-emerald-400'
        if (status === 'not_met' || status === 'missing') return 'text-red-400'
        return 'text-yellow-400'
    }

    const getInProfileValue = (value) => {
        if (value === 'yes' || value === true) return <CheckCircle className="w-4 h-4 text-emerald-400 mx-auto" />
        if (value === 'no' || value === false) return <XCircle className="w-4 h-4 text-red-400/50 mx-auto" />
        return <HelpCircle className="w-4 h-4 text-yellow-400 mx-auto" />
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
            </div>
        )
    }

    if (!job) {
        return (
            <div className="text-center py-20">
                <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-2">Job not found</h2>
                <p className="text-[var(--text-secondary)] mb-6">This job may have been deleted.</p>
                <Link to="/jobs" className="btn-primary inline-flex">
                    <ArrowLeft className="w-4 h-4" />
                    Back to Jobs
                </Link>
            </div>
        )
    }

    // Extract data
    const parsedData = job.parsed_data || {}
    const analysisData = gapAnalysis?.analysis_data || {}
    const existingCoverLetter = coverLetters.length > 0 ? coverLetters[0] : null
    const matchScore = gapAnalysis?.match_score || analysisData.match_score || 0

    return (
        <div className="max-w-5xl mx-auto space-y-6">
            {/* Back Button */}
            <button
                onClick={() => navigate('/jobs')}
                className="flex items-center gap-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
            >
                <ArrowLeft className="w-4 h-4" />
                Back to Jobs
            </button>

            {/* Header */}
            <div className="glass-card overflow-visible relative z-10">
                <div className="flex flex-col md:flex-row items-center gap-6">
                    {/* Match Score Circle */}
                    {matchScore > 0 && (
                        <div className="relative w-24 h-24 flex-shrink-0">
                            <svg className="w-full h-full -rotate-90" viewBox="0 0 96 96">
                                <circle cx="48" cy="48" r="40" fill="none" stroke="var(--glass-border)" strokeWidth="6" />
                                <circle
                                    cx="48" cy="48" r="40"
                                    fill="none"
                                    stroke={matchScore >= 80 ? '#10B981' : matchScore >= 60 ? '#3B82F6' : matchScore >= 40 ? '#F59E0B' : '#EF4444'}
                                    strokeWidth="6"
                                    strokeLinecap="round"
                                    strokeDasharray={`${matchScore * 2.51} 251`}
                                />
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className="text-2xl font-bold" style={{
                                    color: matchScore >= 80 ? '#10B981' : matchScore >= 60 ? '#3B82F6' : matchScore >= 40 ? '#F59E0B' : '#EF4444'
                                }}>
                                    {matchScore}%
                                </span>
                                <span className="text-xs text-[var(--text-tertiary)]">Match</span>
                            </div>
                        </div>
                    )}

                    {analyzing && (
                        <div className="flex items-center gap-2 text-blue-400">
                            <Loader2 className="w-5 h-5 animate-spin" />
                            <span className="text-sm">Analyzing match...</span>
                        </div>
                    )}

                    {/* Job Info */}
                    <div className="flex-1 text-center md:text-left">
                        <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-1">{job.job_title || 'Position'}</h1>
                        <p className="text-[var(--text-secondary)] mb-2">{job.company_name || 'Company'}</p>
                        <p className="text-xs text-[var(--text-tertiary)] flex items-center gap-1 justify-center md:justify-start">
                            <Calendar className="w-3 h-3" />
                            Analyzed {new Date(job.created_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                        </p>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 flex-shrink-0 relative">
                        {/* History Button */}
                        <div className="relative">
                            <button
                                onClick={loadHistory}
                                className={`p-2 rounded-lg border transition-colors ${historyOpen
                                    ? 'bg-blue-500/10 border-blue-500/30 text-blue-400'
                                    : 'border-[var(--glass-border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--glass-hover)]'
                                    }`}
                                title="View analysis history"
                            >
                                {historyLoading ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                ) : (
                                    <Clock className="w-5 h-5" />
                                )}
                            </button>

                            {/* History Dropdown */}
                            {historyOpen && (
                                <div className="absolute right-0 top-full mt-2 w-72 glass-card z-50 p-0 overflow-hidden shadow-xl border border-[var(--glass-border)]">
                                    <div className="p-3 border-b border-[var(--glass-border)] bg-[var(--glass-bg)]">
                                        <h4 className="text-sm font-semibold text-[var(--text-primary)]">Analysis History</h4>
                                    </div>
                                    <div className="max-h-64 overflow-y-auto">
                                        {historyData.length > 0 ? (
                                            <div className="divide-y divide-[var(--glass-border)]">
                                                {historyData.map((item) => (
                                                    <button
                                                        key={item.id}
                                                        onClick={() => handleRestoreAnalysis(item.id)}
                                                        className="w-full text-left p-3 hover:bg-[var(--glass-hover)] transition-colors flex items-center justify-between group"
                                                    >
                                                        <div>
                                                            <div className="text-sm font-medium text-[var(--text-primary)]">
                                                                {new Date(item.created_at).toLocaleDateString()}
                                                            </div>
                                                            <div className="text-xs text-[var(--text-tertiary)]">
                                                                {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                            </div>
                                                        </div>
                                                        <div className={`text-sm font-bold ${item.match_score >= 80 ? 'text-emerald-400' :
                                                            item.match_score >= 60 ? 'text-blue-400' :
                                                                item.match_score >= 40 ? 'text-yellow-400' : 'text-red-400'
                                                            }`}>
                                                            {item.match_score}%
                                                        </div>
                                                    </button>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="p-4 text-center text-sm text-[var(--text-secondary)]">
                                                No history available
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                        {existingCoverLetter ? (
                            <button
                                onClick={() => navigate('/cover-letters')}
                                className="btn-secondary text-emerald-400 border-emerald-500/20"
                            >
                                <Eye className="w-4 h-4" />
                                View Cover Letter
                            </button>
                        ) : (
                            <button
                                onClick={() => navigate(`/cover-letters?jobId=${job.id}`)}
                                className="btn-primary"
                            >
                                <FileText className="w-4 h-4" />
                                Generate Cover Letter
                            </button>
                        )}
                        <button
                            onClick={() => setShowDeleteDialog(true)}
                            className="btn-secondary text-red-400 border-red-500/20 hover:bg-red-500/10"
                        >
                            <Trash2 className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>



            {/* Qualifications with Match Status - UPDATED */}
            {analysisData.qualification_comparison?.length > 0 && (
                <div className="glass-card overflow-hidden">
                    <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                        <BadgeCheck className="w-5 h-5 text-purple-400" />
                        Qualifications Analysis
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-[var(--glass-border)]">
                                    <th className="text-left py-2 px-3 text-[var(--text-tertiary)] font-medium">Qualification</th>
                                    <th className="text-center py-2 px-3 text-[var(--text-tertiary)] font-medium">Type</th>
                                    <th className="text-center py-2 px-3 text-[var(--text-tertiary)] font-medium">Status</th>
                                    <th className="text-left py-2 px-3 text-[var(--text-tertiary)] font-medium">Evidence</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-[var(--glass-border)]">
                                {analysisData.qualification_comparison.map((qual, i) => (
                                    <tr key={i} className="hover:bg-[var(--glass-hover)] transition-colors">
                                        <td className="py-2 px-3 text-[var(--text-primary)]">{qual.qualification}</td>
                                        <td className="py-2 px-3 text-center">
                                            <span className={`px-2 py-0.5 text-xs rounded ${qual.type === 'required'
                                                ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                                                : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'}`}>
                                                {qual.type}
                                            </span>
                                        </td>
                                        <td className="py-2 px-3 text-center">
                                            <div className="flex items-center justify-center gap-2">
                                                {getStatusIcon(qual.status)}
                                                <span className={`text-xs ${getStatusColor(qual.status)}`}>
                                                    {qual.status.replace('_', ' ')}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="py-2 px-3 text-xs text-[var(--text-secondary)]">{qual.evidence}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Skills Comparison - UPDATED */}
            {analysisData.skill_comparison?.length > 0 && (
                <div className="glass-card overflow-hidden">
                    <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-cyan-400" />
                        Skills Analysis
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-[var(--glass-border)]">
                                    <th className="text-left py-2 px-3 text-[var(--text-tertiary)] font-medium">Skill</th>
                                    <th className="text-center py-2 px-3 text-[var(--text-tertiary)] font-medium">Type</th>
                                    <th className="text-center py-2 px-3 text-[var(--text-tertiary)] font-medium">Source</th>
                                    <th className="text-center py-2 px-3 text-[var(--text-tertiary)] font-medium">Importance</th>
                                    <th className="text-center py-2 px-3 text-[var(--text-tertiary)] font-medium">In Profile</th>
                                    <th className="text-center py-2 px-3 text-[var(--text-tertiary)] font-medium">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-[var(--glass-border)]">
                                {analysisData.skill_comparison.map((skill, i) => (
                                    <tr key={i} className="hover:bg-[var(--glass-hover)] transition-colors">
                                        <td className="py-2 px-3 text-[var(--text-primary)]">{skill.skill}</td>
                                        <td className="py-2 px-3 text-center">
                                            <span className={`px-2 py-0.5 text-xs rounded ${skill.type === 'hard'
                                                ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                                                : 'bg-orange-500/10 text-orange-400 border border-orange-500/20'}`}>
                                                {skill.type}
                                            </span>
                                        </td>
                                        <td className="py-2 px-3 text-center text-xs text-[var(--text-tertiary)]">
                                            {skill.source?.replace('_', ' ')}
                                        </td>
                                        <td className="py-2 px-3 text-center">
                                            <span className={`text-xs ${skill.importance === 'high' ? 'text-red-400' :
                                                skill.importance === 'medium' ? 'text-yellow-400' :
                                                    'text-blue-400'
                                                }`}>
                                                {skill.importance}
                                            </span>
                                        </td>
                                        <td className="py-2 px-3 text-center">
                                            {getInProfileValue(skill.in_profile)}
                                        </td>
                                        <td className="py-2 px-3 text-center">
                                            <div className="flex items-center justify-center gap-1">
                                                {getStatusIcon(skill.status)}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Resume Optimization - Full Width */}
            <div className="glass-card overflow-hidden">
                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                    <Edit3 className="w-5 h-5 text-blue-400" />
                    Resume Optimization
                </h3>

                {optimizationLoading ? (
                    <div className="flex items-center justify-center py-8 text-blue-400 gap-2">
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Analyzing resume for optimizations...</span>
                    </div>
                ) : optimizationError ? (
                    <div className="text-center py-8 text-[var(--text-secondary)]">
                        <p>{optimizationError}</p>
                    </div>
                ) : optimizationData?.optimizations?.length > 0 ? (
                    <div className="space-y-4">
                        {optimizationData.optimizations.map((opt, i) => (
                            <div key={i} className="border border-[var(--glass-border)] rounded-xl overflow-hidden">
                                <div className="bg-[var(--glass-bg)] px-4 py-2 border-b border-[var(--glass-border)]">
                                    <h4 className="text-sm font-semibold text-[var(--text-primary)]">{opt.section_name}</h4>
                                    <p className="text-xs text-[var(--text-tertiary)] mt-1">{opt.explanation}</p>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-[var(--glass-border)]">
                                    {/* Before */}
                                    <div className="p-4">
                                        <div className="flex items-center gap-2 mb-3">
                                            <span className="text-xs font-semibold text-red-400">ORIGINAL</span>
                                        </div>
                                        <ul className="space-y-2">
                                            {opt.original_content
                                                .split(/(?<=[.!?])\s+(?=[A-Z])|(?=\n[•\-\*])|(?=\n\d+\.)|\n+/)
                                                .map(s => s.trim())
                                                .filter(s => s.length > 0)
                                                .map((line, idx) => (
                                                    <li key={idx} className="flex items-start gap-2 text-sm text-[var(--text-secondary)] opacity-80">
                                                        <span className="text-red-400/50 mt-1.5 text-[0.5rem] shrink-0">●</span>
                                                        <span className="leading-relaxed">{line.replace(/^[•\-\*]\s*/, '').replace(/^\d+\.\s*/, '')}</span>
                                                    </li>
                                                ))}
                                        </ul>
                                    </div>
                                    {/* After */}
                                    <div className="p-4 bg-emerald-500/5">
                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs font-semibold text-emerald-400">OPTIMIZED</span>
                                                <CheckCircle className="w-3 h-3 text-emerald-400" />
                                            </div>
                                            <button
                                                onClick={() => {
                                                    navigator.clipboard.writeText(opt.optimized_content)
                                                    toast.success('Copied to clipboard')
                                                }}
                                                className="p-1.5 hover:bg-emerald-500/10 rounded-lg transition-colors group"
                                                title="Copy customized content"
                                            >
                                                <Copy className="w-3.5 h-3.5 text-emerald-400/70 group-hover:text-emerald-400" />
                                            </button>
                                        </div>
                                        <ul className="space-y-2">
                                            {opt.optimized_content
                                                .split(/(?<=[.!?])\s+(?=[A-Z])|(?=\n[•\-\*])|(?=\n\d+\.)|\n+/)
                                                .map(s => s.trim())
                                                .filter(s => s.length > 0)
                                                .map((line, idx) => (
                                                    <li key={idx} className="flex items-start gap-2 text-sm text-[var(--text-primary)]">
                                                        <span className="text-emerald-400 mt-1.5 text-[0.5rem] shrink-0">●</span>
                                                        <span className="leading-relaxed">{line.replace(/^[•\-\*]\s*/, '').replace(/^\d+\.\s*/, '')}</span>
                                                    </li>
                                                ))}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        ))}                </div>
                ) : (
                    <div className="text-center py-8 text-[var(--text-secondary)]">
                        No optimizations suggestions available at this time.
                    </div>
                )}
            </div>

            {/* Job Details */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left Column */}
                <div className="space-y-6">
                    {/* Job Description */}
                    {parsedData.job_description && (
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                <Briefcase className="w-5 h-5 text-blue-400" />
                                Job Description
                            </h3>
                            <p className="text-[var(--text-secondary)] text-sm leading-relaxed">
                                {parsedData.job_description}
                            </p>
                        </div>
                    )}

                    {/* Required Qualifications - Basic List */}
                    {parsedData.required_qualifications?.length > 0 && (
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                <CheckCircle className="w-5 h-5 text-emerald-400" />
                                Required Qualifications
                            </h3>
                            <ul className="space-y-2">
                                {parsedData.required_qualifications.map((qual, i) => (
                                    <li key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                                        <span className="text-emerald-400 mt-1">•</span>
                                        {qual}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}



                    {/* Preferred Qualifications - Basic List */}
                    {parsedData.preferred_qualifications?.length > 0 && (
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                <GraduationCap className="w-5 h-5 text-yellow-400" />
                                Preferred Qualifications
                            </h3>
                            <ul className="space-y-2">
                                {parsedData.preferred_qualifications.map((qual, i) => (
                                    <li key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                                        <span className="text-yellow-400 mt-1">•</span>
                                        {qual}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>

                {/* Right Column */}
                <div className="space-y-6">
                    {/* Company About */}
                    {parsedData.about_company && (
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                <Building2 className="w-5 h-5 text-cyan-400" />
                                About the Company
                            </h3>
                            <p className="text-[var(--text-secondary)] text-sm leading-relaxed">
                                {parsedData.about_company}
                            </p>
                        </div>
                    )}

                    {/* Salary & Benefits */}
                    {(parsedData.salary_range || parsedData.benefits?.length > 0) && (
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                <GraduationCap className="w-5 h-5 text-yellow-400" />
                                Compensation & Benefits
                            </h3>
                            {parsedData.salary_range?.min && (
                                <p className="text-xl font-bold text-emerald-400 mb-3">
                                    ${parsedData.salary_range.min.toLocaleString()}
                                    {parsedData.salary_range.max && parsedData.salary_range.max !== parsedData.salary_range.min
                                        ? ` - $${parsedData.salary_range.max.toLocaleString()}`
                                        : ''}
                                    <span className="text-sm text-[var(--text-tertiary)] font-normal ml-2">
                                        {parsedData.salary_range.currency || 'USD'}
                                        {parsedData.salary_range.pay_type && ` / ${parsedData.salary_range.pay_type}`}
                                    </span>
                                </p>
                            )}
                            {parsedData.benefits?.length > 0 && (
                                <ul className="space-y-1">
                                    {parsedData.benefits.map((benefit, i) => (
                                        <li key={i} className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                                            <CheckCircle className="w-3 h-3 text-emerald-400" />
                                            {benefit}
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    )}

                    {/* Recommendations */}
                    {analysisData.recommendations?.length > 0 && (
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                <Lightbulb className="w-5 h-5 text-orange-400" />
                                Recommendations
                            </h3>
                            <ul className="space-y-2">
                                {analysisData.recommendations.map((rec, i) => (
                                    <li key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                                        <span className="text-orange-400 mt-1">→</span>
                                        {rec}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </div>

            {/* Delete Confirmation Dialog */}
            {showDeleteDialog && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
                    onClick={() => setShowDeleteDialog(false)}
                >
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="w-full max-w-sm glass-card border-[var(--glass-border)] rounded-2xl p-6"
                        style={{ background: 'var(--bg-secondary)' }}
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center">
                                <AlertTriangle className="w-5 h-5 text-red-400" />
                            </div>
                            <h3 className="text-lg font-semibold text-[var(--text-primary)]">Delete Job?</h3>
                        </div>
                        <p className="text-[var(--text-secondary)] mb-6">
                            This will permanently remove '{job.job_title}' from your saved jobs.
                        </p>
                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={() => setShowDeleteDialog(false)}
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

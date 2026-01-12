import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, CheckCircle, XCircle, Loader2, RefreshCw, FileText, Linkedin, Globe, Clock, ChevronRight } from 'lucide-react'
import { toast } from 'sonner'
import { discrepancyApi, profileApi } from '../api/client'

export default function Discrepancy() {
    const [profiles, setProfiles] = useState([])
    const [loading, setLoading] = useState(true)
    const [analyzing, setAnalyzing] = useState(false)
    const [analysis, setAnalysis] = useState(null)

    // History state
    const [historyOpen, setHistoryOpen] = useState(false)
    const [historyData, setHistoryData] = useState([])
    const [historyLoading, setHistoryLoading] = useState(false)

    useEffect(() => {
        loadProfiles()
    }, [])

    const loadProfiles = async () => {
        try {
            const profileList = await profileApi.list()
            setProfiles(profileList)
        } catch (error) {
            console.error('Failed to load profiles:', error)
            toast.error('Failed to load profiles')
        } finally {
            setLoading(false)
        }
    }

    const runAnalysis = async () => {
        if (profiles.length < 2) {
            toast.error('Need at least 2 profiles to compare')
            return
        }

        setAnalyzing(true)
        try {
            const profileIds = profiles.map(p => p.id)
            const result = await discrepancyApi.compare(profileIds)
            // The API now returns report_data which contains the analysis
            setAnalysis(result.report_data || result)
            toast.success('Analysis complete!')
        } catch (error) {
            toast.error(error.message || 'Analysis failed')
        } finally {
            setAnalyzing(false)
        }
    }

    const loadHistory = async () => {
        if (historyOpen) {
            setHistoryOpen(false)
            return
        }

        setHistoryLoading(true)
        setHistoryOpen(true)
        try {
            const data = await discrepancyApi.getHistory()
            setHistoryData(data)
        } catch (error) {
            toast.error('Failed to load history')
        } finally {
            setHistoryLoading(false)
        }
    }

    const handleRestoreReport = async (reportId) => {
        setHistoryOpen(false)
        try {
            const report = await discrepancyApi.get(reportId)
            setAnalysis(report.report_data)
            toast.success('Historical report loaded')
        } catch (error) {
            toast.error('Failed to load report')
        }
    }

    const getSourceIcon = (source) => {
        switch (source) {
            case 'resume': return <FileText className="w-4 h-4" />
            case 'linkedin': return <Linkedin className="w-4 h-4" />
            case 'portfolio': return <Globe className="w-4 h-4" />
            default: return <FileText className="w-4 h-4" />
        }
    }

    const getScoreColor = (score) => {
        if (score >= 80) return 'text-emerald-400'
        if (score >= 60) return 'text-yellow-400'
        return 'text-red-400'
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
            </div>
        )
    }

    return (
        <div className="max-w-5xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-1">Discrepancy Analysis</h1>
                    <p className="text-[var(--text-secondary)]">Compare your profiles for consistency</p>
                </div>
                <div className="flex gap-3 relative">
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
                                                    onClick={() => handleRestoreReport(item.id)}
                                                    className="w-full p-3 text-left hover:bg-[var(--glass-hover)] transition-colors flex items-center justify-between group"
                                                >
                                                    <div>
                                                        <div className="text-sm font-medium text-[var(--text-primary)]">
                                                            {item.consistency_score}% Consistency
                                                        </div>
                                                        <div className="text-xs text-[var(--text-tertiary)]">
                                                            {new Date(item.created_at).toLocaleDateString('en-US', {
                                                                month: 'short', day: 'numeric', year: 'numeric',
                                                                hour: '2-digit', minute: '2-digit'
                                                            })}
                                                        </div>
                                                    </div>
                                                    <ChevronRight className="w-4 h-4 text-[var(--text-tertiary)] group-hover:text-[var(--text-primary)]" />
                                                </button>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="p-4 text-center text-[var(--text-tertiary)] text-sm">
                                            No previous reports
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Run Analysis Button */}
                    <button
                        onClick={runAnalysis}
                        disabled={analyzing || profiles.length < 2}
                        className="btn-primary"
                    >
                        {analyzing ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <RefreshCw className="w-4 h-4" />
                                Run Analysis
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Profiles Status */}
            {profiles.length < 2 && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="p-4 rounded-xl border flex items-center gap-3"
                    style={{ background: 'var(--bg-warning)', borderColor: 'var(--border-warning)' }}
                >
                    <AlertTriangle className="w-5 h-5 flex-shrink-0" style={{ color: 'var(--color-warning)' }} />
                    <div className="flex-1">
                        <p className="font-medium" style={{ color: 'var(--color-warning)' }}>Need more profiles</p>
                        <p className="text-sm opacity-80" style={{ color: 'var(--color-warning)' }}>
                            Upload at least 2 profiles (Resume, LinkedIn, Portfolio) to compare.
                        </p>
                    </div>
                </motion.div>
            )}

            {/* Profiles List */}
            <div className="glass-card">
                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Your Profiles</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {['resume', 'linkedin', 'portfolio'].map(type => {
                        const profile = profiles.find(p => p.source_type === type)
                        return (
                            <div
                                key={type}
                                className={`p-4 rounded-xl border ${profile
                                    ? 'bg-emerald-500/10 border-emerald-500/30'
                                    : 'bg-[var(--glass-hover)] border-[var(--glass-border)]'
                                    }`}
                            >
                                <div className="flex items-center gap-2 mb-2">
                                    {getSourceIcon(type)}
                                    <span className="font-medium text-[var(--text-primary)] capitalize">{type}</span>
                                </div>
                                {profile ? (
                                    <p className="text-xs text-emerald-400 flex items-center gap-1">
                                        <CheckCircle className="w-3 h-3" />
                                        Uploaded
                                    </p>
                                ) : (
                                    <p className="text-xs text-[var(--text-tertiary)]">Not uploaded</p>
                                )}
                            </div>
                        )
                    })}
                </div>
            </div>

            {/* Analysis Results */}
            {analysis && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-6"
                >
                    {/* Consistency Score */}
                    <div className="glass-card text-center">
                        <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Consistency Score</h3>
                        <div className={`text-5xl font-bold mb-2 ${getScoreColor(analysis.consistency_score)}`}>
                            {analysis.consistency_score}%
                        </div>
                        <p className="text-[var(--text-secondary)] text-sm">
                            {analysis.consistency_score >= 80
                                ? 'Great! Your profiles are consistent.'
                                : analysis.consistency_score >= 60
                                    ? 'Some discrepancies found. Review below.'
                                    : 'Significant discrepancies detected. Please review.'}
                        </p>
                    </div>

                    {/* Discrepancies Table */}
                    {analysis.discrepancies?.length > 0 && (
                        <div className="glass-card overflow-hidden">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                <AlertTriangle className="w-5 h-5 text-yellow-400" />
                                Discrepancies Found
                            </h3>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b border-[var(--glass-border)]">
                                            <th className="text-left py-3 px-4 text-[var(--text-tertiary)] font-medium">Section</th>
                                            <th className="text-left py-3 px-4 text-[var(--text-tertiary)] font-medium">Resume</th>
                                            <th className="text-left py-3 px-4 text-[var(--text-tertiary)] font-medium">LinkedIn</th>
                                            <th className="text-left py-3 px-4 text-[var(--text-tertiary)] font-medium">Portfolio</th>
                                            <th className="text-left py-3 px-4 text-[var(--text-tertiary)] font-medium">Severity</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-[var(--glass-border)]">
                                        {analysis.discrepancies.map((item, i) => (
                                            <tr key={i} className="hover:bg-[var(--glass-hover)] transition-colors">
                                                <td className="py-3 px-4 text-[var(--text-primary)] font-medium">{item.section}</td>
                                                <td className="py-3 px-4 text-[var(--text-secondary)]">{item.resume || '—'}</td>
                                                <td className="py-3 px-4 text-[var(--text-secondary)]">{item.linkedin || '—'}</td>
                                                <td className="py-3 px-4 text-[var(--text-secondary)]">{item.portfolio || '—'}</td>
                                                <td className="py-3 px-4">
                                                    <span className={`px-2 py-1 rounded text-xs border ${item.severity === 'high'
                                                        ? 'bg-red-500/10 text-red-400 border-red-500/20'
                                                        : item.severity === 'medium'
                                                            ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
                                                            : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                                                        }`}>
                                                        {item.severity || 'low'}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* Skill Comparison */}
                    {analysis.skill_comparison?.length > 0 && (
                        <div className="glass-card overflow-hidden">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Skill Presence</h3>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b border-[var(--glass-border)]">
                                            <th className="text-left py-3 px-4 text-[var(--text-tertiary)] font-medium">Skill</th>
                                            <th className="text-center py-3 px-4 text-[var(--text-tertiary)] font-medium">Resume</th>
                                            <th className="text-center py-3 px-4 text-[var(--text-tertiary)] font-medium">LinkedIn</th>
                                            <th className="text-center py-3 px-4 text-[var(--text-tertiary)] font-medium">Portfolio</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-[var(--glass-border)]">
                                        {analysis.skill_comparison.map((item, i) => (
                                            <tr key={i} className="hover:bg-[var(--glass-hover)] transition-colors">
                                                <td className="py-3 px-4 text-[var(--text-primary)] font-medium">{item.skill}</td>
                                                <td className="py-3 px-4 text-center">
                                                    {item.in_resume ? (
                                                        <CheckCircle className="w-4 h-4 text-emerald-400 mx-auto" />
                                                    ) : (
                                                        <XCircle className="w-4 h-4 text-red-400/50 mx-auto" />
                                                    )}
                                                </td>
                                                <td className="py-3 px-4 text-center">
                                                    {item.in_linkedin ? (
                                                        <CheckCircle className="w-4 h-4 text-emerald-400 mx-auto" />
                                                    ) : (
                                                        <XCircle className="w-4 h-4 text-red-400/50 mx-auto" />
                                                    )}
                                                </td>
                                                <td className="py-3 px-4 text-center">
                                                    {item.in_portfolio ? (
                                                        <CheckCircle className="w-4 h-4 text-emerald-400 mx-auto" />
                                                    ) : (
                                                        <XCircle className="w-4 h-4 text-red-400/50 mx-auto" />
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* Missing Items */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {analysis.missing_in_resume?.length > 0 && (
                            <div className="glass-card">
                                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                    <XCircle className="w-5 h-5 text-red-400" />
                                    Missing in Resume
                                </h3>
                                <div className="flex flex-wrap gap-2">
                                    {analysis.missing_in_resume.map((item, i) => (
                                        <span key={i} className="px-3 py-1 text-sm rounded-lg bg-red-500/10 text-red-400 border border-red-500/20">
                                            {item}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {analysis.missing_online?.length > 0 && (
                            <div className="glass-card">
                                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                    <XCircle className="w-5 h-5 text-yellow-400" />
                                    Missing Online
                                </h3>
                                <div className="flex flex-wrap gap-2">
                                    {analysis.missing_online.map((item, i) => (
                                        <span key={i} className="px-3 py-1 text-sm rounded-lg bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                                            {item}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Recommendations */}
                    {analysis.recommendations?.length > 0 && (
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Recommendations</h3>
                            <div className="space-y-3">
                                {analysis.recommendations.map((rec, i) => (
                                    <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-[var(--input-bg)]">
                                        <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                                            <span className="text-xs text-blue-400 font-medium">{i + 1}</span>
                                        </div>
                                        <p className="text-sm text-[var(--text-secondary)]">{rec}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </motion.div>
            )}
        </div>
    )
}

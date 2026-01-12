import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
    Sparkles, Loader2, CheckCircle, XCircle, Lightbulb,
    Building2, Newspaper, FileText, Briefcase, GraduationCap,
    Award, FolderOpen, ArrowRight, AlertTriangle, DollarSign
} from 'lucide-react'
import { toast } from 'sonner'
import { jobApi, matchApi, profileApi } from '../api/client'

export default function Dashboard() {
    const navigate = useNavigate()
    const [jobText, setJobText] = useState('')
    const [companyInfo, setCompanyInfo] = useState('')
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [analysis, setAnalysis] = useState(null)
    const [profiles, setProfiles] = useState([])
    const [loadingProfiles, setLoadingProfiles] = useState(true)

    useEffect(() => {
        loadProfiles()
    }, [])

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

    const handleAnalyze = async () => {
        if (!jobText.trim()) {
            toast.error('Please paste a job description')
            return
        }

        if (profiles.length === 0) {
            toast.error('Please upload at least one profile first')
            return
        }

        setIsAnalyzing(true)
        setAnalysis(null)

        try {
            toast.loading('Parsing job posting...', { id: 'analyze' })
            const job = await jobApi.parsePosting(jobText, null, companyInfo || null)

            let companyIntel = null
            const companyName = companyInfo || job.company_name
            if (companyName) {
                toast.loading('Gathering company intelligence...', { id: 'analyze' })
                try {
                    companyIntel = await jobApi.getCompanyIntel(companyName)
                } catch (error) {
                    console.warn('Failed to get company intel:', error)
                }
            }

            toast.loading('Analyzing match...', { id: 'analyze' })
            const profileIds = profiles.map(p => p.id)
            const gapAnalysis = await matchApi.analyzeGaps(profileIds, job.id)

            const result = {
                id: job.id,
                jobTitle: gapAnalysis.analysis_data?.job_title || job.job_title,
                company: gapAnalysis.analysis_data?.company_name || job.company_name,
                matchScore: gapAnalysis.match_score || gapAnalysis.analysis_data?.match_score,
                parsedJob: job.parsed_data,
                gapAnalysis: gapAnalysis.analysis_data,
                companyIntel: companyIntel?.intelligence || null,
            }

            setAnalysis(result)
            toast.success('Analysis complete!', { id: 'analyze' })

            // Redirect to job detail page
            navigate(`/jobs/${job.id}`)

        } catch (error) {
            console.error('Analysis failed:', error)
            toast.error(error.message || 'Analysis failed', { id: 'analyze' })
        } finally {
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
                    <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">Job Description *</label>
                    <textarea
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
                <div className="flex justify-end">
                    <button onClick={handleAnalyze} disabled={!jobText.trim() || isAnalyzing || profiles.length === 0} className="btn-primary">
                        {isAnalyzing ? (<><Loader2 className="w-4 h-4 animate-spin" />Analyzing...</>) : (<><Sparkles className="w-4 h-4" />Analyze Match</>)}
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
                                    <button onClick={() => navigate(`/cover-letters?jobId=${analysis.id}`)} className="btn-primary">
                                        <FileText className="w-4 h-4" />Generate Cover Letter
                                    </button>
                                    <button onClick={() => navigate(`/jobs/${analysis.id}`)} className="btn-secondary">
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
                                        {gap.compensation.salary_max && gap.compensation.salary_max !== gap.compensation.salary_min && ` - $${gap.compensation.salary_max.toLocaleString()}`}
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
                                                    <span className={`px-2 py-1 rounded text-xs border ${item.type === 'hard' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 'bg-orange-500/10 text-orange-400 border-orange-500/20'}`}>
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
        </div>
    )
}

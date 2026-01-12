import { useState, useEffect } from 'react'
import { useSearchParams, Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FileText, Search, Copy, CheckCircle, Loader2, Sparkles, Palette, MessageSquare, Trash2, AlertTriangle } from 'lucide-react'
import { toast } from 'sonner'
import { matchApi, profileApi, jobApi } from '../api/client'

const themes = [
    { id: 'professional', label: 'Professional', description: 'Formal and polished tone' },
    { id: 'enthusiastic', label: 'Enthusiastic', description: 'Energetic and passionate' },
    { id: 'concise', label: 'Concise', description: 'Brief and impactful' },
]

export default function CoverLetters() {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()
    const jobIdFromUrl = searchParams.get('jobId')

    const [letters, setLetters] = useState([])
    const [searchTerm, setSearchTerm] = useState('')
    const [copiedId, setCopiedId] = useState(null)
    const [deleteLetter, setDeleteLetter] = useState(null)
    const [loading, setLoading] = useState(true)

    // New letter form
    const [showForm, setShowForm] = useState(!!jobIdFromUrl)
    const [selectedTheme, setSelectedTheme] = useState('professional')
    const [customInstructions, setCustomInstructions] = useState('')
    const [isGenerating, setIsGenerating] = useState(false)
    const [generatedLetter, setGeneratedLetter] = useState(null)
    const [profiles, setProfiles] = useState([])
    const [jobData, setJobData] = useState(null)

    // Load letters and profiles
    useEffect(() => {
        loadData()
    }, [jobIdFromUrl])

    const loadData = async () => {
        try {
            // Load cover letters
            const letterList = await matchApi.listCoverLetters()
            setLetters(letterList)

            // Load profiles
            const profileList = await profileApi.list()
            setProfiles(profileList)

            // Load job if coming from job detail
            if (jobIdFromUrl) {
                try {
                    const job = await jobApi.get(jobIdFromUrl)
                    setJobData(job)
                } catch (error) {
                    console.error('Failed to load job:', error)
                }
            }
        } catch (error) {
            console.error('Failed to load data:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleGenerate = async () => {
        if (profiles.length === 0) {
            toast.error('Please upload at least one profile first')
            return
        }

        if (!jobIdFromUrl && !jobData) {
            toast.error('Please select a job to generate a cover letter for')
            return
        }

        setIsGenerating(true)

        try {
            const profileIds = profiles.map(p => p.id)
            const letter = await matchApi.generateCoverLetter(profileIds, jobIdFromUrl, selectedTheme)

            setGeneratedLetter(letter)
            setLetters(prev => [letter, ...prev])
            toast.success('Cover letter generated!')
        } catch (error) {
            toast.error(error.message || 'Failed to generate cover letter')
        } finally {
            setIsGenerating(false)
        }
    }

    const handleCopy = (id, text) => {
        navigator.clipboard.writeText(text)
        setCopiedId(id)
        toast.success('Copied to clipboard')
        setTimeout(() => setCopiedId(null), 2000)
    }

    const confirmDelete = async () => {
        if (!deleteLetter) return

        try {
            await matchApi.deleteCoverLetter(deleteLetter.id)
            setLetters(letters.filter(l => l.id !== deleteLetter.id))
            toast.success('Cover letter deleted')
        } catch (error) {
            toast.error('Failed to delete cover letter')
        }
        setDeleteLetter(null)
    }

    const filteredLetters = letters.filter(letter =>
        letter.style?.toLowerCase().includes(searchTerm.toLowerCase())
    )

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
                    <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-1">Cover Letters</h1>
                    <p className="text-[var(--text-secondary)]">{letters.length} cover letters generated</p>
                </div>
                {!showForm && (
                    <button onClick={() => setShowForm(true)} className="btn-primary">
                        <Sparkles className="w-4 h-4" />
                        New Cover Letter
                    </button>
                )}
            </div>

            {/* New Letter Form */}
            {showForm && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-card space-y-6"
                >
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-semibold text-[var(--text-primary)] flex items-center gap-2">
                            <Sparkles className="w-5 h-5 text-blue-400" />
                            Generate Cover Letter
                        </h2>
                        <button
                            onClick={() => {
                                setShowForm(false)
                                setGeneratedLetter(null)
                            }}
                            className="text-[var(--text-tertiary)] hover:text-[var(--text-primary)]"
                        >
                            ✕
                        </button>
                    </div>

                    {/* Job Info */}
                    {jobData ? (
                        <div className="p-4 rounded-xl bg-[var(--input-bg)] border border-[var(--glass-border)]">
                            <p className="text-sm text-[var(--text-tertiary)] mb-1">Generating for:</p>
                            <p className="font-semibold text-[var(--text-primary)]">{jobData.job_title}</p>
                            <p className="text-sm text-[var(--text-secondary)]">{jobData.company_name}</p>
                        </div>
                    ) : (
                        <div className="p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/30">
                            <p className="text-yellow-300 text-sm">
                                No job selected.
                                <Link to="/jobs" className="underline ml-1">Select a job</Link> or
                                <Link to="/" className="underline ml-1">analyze a new one</Link> first.
                            </p>
                        </div>
                    )}

                    {/* Theme Selection */}
                    <div>
                        <label className="block text-sm font-medium text-[var(--text-secondary)] mb-3 flex items-center gap-2">
                            <Palette className="w-4 h-4" />
                            Choose Tone
                        </label>
                        <div className="flex gap-3">
                            {themes.map(theme => (
                                <button
                                    key={theme.id}
                                    onClick={() => setSelectedTheme(theme.id)}
                                    className={`flex-1 p-3 rounded-xl border transition-all ${selectedTheme === theme.id
                                        ? 'bg-blue-500/20 border-blue-500/50 text-blue-400'
                                        : 'bg-[var(--glass-hover)] border-[var(--glass-border)] text-[var(--text-secondary)] hover:border-[var(--text-tertiary)]'
                                        }`}
                                >
                                    <p className="font-medium text-sm">{theme.label}</p>
                                    <p className="text-xs opacity-70 mt-0.5">{theme.description}</p>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Custom Instructions */}
                    <div>
                        <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2 flex items-center gap-2">
                            <MessageSquare className="w-4 h-4" />
                            Custom Instructions (Optional)
                        </label>
                        <textarea
                            value={customInstructions}
                            onChange={(e) => setCustomInstructions(e.target.value)}
                            placeholder="Any specific points you'd like to emphasize..."
                            className="min-h-[80px]"
                        />
                    </div>

                    {/* Generate Button */}
                    <div className="flex justify-end">
                        <button
                            onClick={handleGenerate}
                            disabled={isGenerating || !jobIdFromUrl || profiles.length === 0}
                            className="btn-primary"
                        >
                            {isGenerating ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-4 h-4" />
                                    Generate
                                </>
                            )}
                        </button>
                    </div>

                    {/* Generated Letter Preview */}
                    {generatedLetter && (
                        <div className="p-4 rounded-xl bg-[var(--input-bg)] border border-[var(--glass-border)]">
                            <div className="flex items-center justify-between mb-3">
                                <p className="text-sm font-medium text-[var(--text-primary)]">Generated Letter</p>
                                <button
                                    onClick={() => handleCopy(generatedLetter.id, generatedLetter.letter)}
                                    className="btn-secondary text-sm"
                                >
                                    {copiedId === generatedLetter.id ? (
                                        <>
                                            <CheckCircle className="w-3 h-3" />
                                            Copied
                                        </>
                                    ) : (
                                        <>
                                            <Copy className="w-3 h-3" />
                                            Copy
                                        </>
                                    )}
                                </button>
                            </div>
                            <div className="text-sm text-[var(--text-secondary)] space-y-3">
                                {generatedLetter.letter.split('\n\n').map((para, i) => (
                                    <p key={i} className="leading-relaxed">{para}</p>
                                ))}
                            </div>
                        </div>
                    )}
                </motion.div>
            )}

            {/* Search */}
            {!showForm && letters.length > 0 && (
                <div className="relative max-w-md">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]" />
                    <input
                        type="text"
                        placeholder="Search cover letters..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-11"
                        style={{ paddingLeft: '4rem' }}
                    />
                </div>
            )}

            {/* Cover Letters List */}
            {!showForm && (
                <>
                    {filteredLetters.length === 0 ? (
                        <div className="text-center py-20">
                            <div className="w-16 h-16 rounded-full bg-[var(--glass-hover)] flex items-center justify-center mx-auto mb-4">
                                <FileText className="w-8 h-8 text-[var(--text-tertiary)]" />
                            </div>
                            <h3 className="text-lg font-medium text-[var(--text-secondary)] mb-2">
                                {letters.length === 0 ? 'No cover letters yet' : 'No matching letters'}
                            </h3>
                            <p className="text-[var(--text-tertiary)] mb-6">
                                {letters.length === 0 ? 'Generate your first cover letter' : 'Try a different search term'}
                            </p>
                        </div>
                    ) : (
                        <div className="grid gap-4">
                            {filteredLetters.map((letter, index) => (
                                <motion.div
                                    key={letter.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                    className="glass-card"
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <div>
                                            <span className="px-2 py-0.5 text-xs rounded bg-blue-500/20 text-blue-300 border border-blue-500/30 capitalize">
                                                {letter.style}
                                            </span>
                                            <p className="text-xs text-[var(--text-tertiary)] mt-2">
                                                {new Date(letter.created_at).toLocaleDateString()}
                                            </p>
                                        </div>
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => handleCopy(letter.id, letter.letter)}
                                                className="p-2 rounded-lg hover:bg-[var(--glass-hover)] text-[var(--text-tertiary)] hover:text-[var(--text-primary)] transition-colors"
                                            >
                                                {copiedId === letter.id ? (
                                                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                                                ) : (
                                                    <Copy className="w-4 h-4" />
                                                )}
                                            </button>
                                            <button
                                                onClick={() => setDeleteLetter(letter)}
                                                className="p-2 rounded-lg hover:bg-red-500/10 text-[var(--text-tertiary)] hover:text-red-400 transition-colors"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                    <div className="text-sm text-[var(--text-secondary)] space-y-3">
                                        {letter.letter.split('\n\n').map((para, i) => (
                                            <p key={i} className="leading-relaxed">{para}</p>
                                        ))}
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    )}
                </>
            )}

            {/* Delete Confirmation Dialog */}
            {deleteLetter && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
                    onClick={() => setDeleteLetter(null)}
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
                            <h3 className="text-lg font-semibold text-[var(--text-primary)]">Delete Cover Letter?</h3>
                        </div>
                        <p className="text-[var(--text-secondary)] mb-6">
                            This will permanently remove this cover letter.
                        </p>
                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={() => setDeleteLetter(null)}
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

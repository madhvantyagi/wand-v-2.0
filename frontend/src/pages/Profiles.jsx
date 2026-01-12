import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    User, FileText, Linkedin, Globe, Upload, CheckCircle,
    Trash2, ChevronDown, ChevronUp, Briefcase, Loader2
} from 'lucide-react'
import { toast } from 'sonner'
import { profileApi } from '../api/client'
import { useUpload } from '../context/UploadContext'

const profileTypes = [
    {
        type: 'resume',
        label: 'Resume',
        icon: FileText,
        color: 'blue',
        description: 'Upload your PDF resume',
        accept: '.pdf'
    },
    {
        type: 'linkedin',
        label: 'LinkedIn',
        icon: Linkedin,
        color: 'cyan',
        description: 'Export from LinkedIn as PDF',
        accept: '.pdf'
    },
    {
        type: 'portfolio',
        label: 'Portfolio',
        icon: Globe,
        color: 'purple',
        description: 'Your portfolio as HTML file',
        accept: '.html,.htm'
    },
]

export default function Profiles() {
    const { startUpload, getUploadStatus, uploadStates } = useUpload()
    const [profiles, setProfiles] = useState({})
    const [loading, setLoading] = useState(true)
    const [expandedProfile, setExpandedProfile] = useState(null)

    // Load profiles from API
    useEffect(() => {
        loadProfiles()
    }, [])

    // Watch for successful uploads to reload data
    useEffect(() => {
        // If any upload just succeeded, reload profiles
        const hasSuccess = Object.values(uploadStates).some(s => s.status === 'success')
        if (hasSuccess) {
            loadProfiles()
        }
    }, [uploadStates])

    const loadProfiles = async () => {
        try {
            const profileList = await profileApi.list()
            // Convert array to object keyed by source_type
            const profileMap = {}
            profileList.forEach(p => {
                profileMap[p.source_type] = p
            })
            setProfiles(profileMap)
        } catch (error) {
            console.error('Failed to load profiles:', error)
        } finally {
            setLoading(false)
        }
    }

    // Upload new profile
    const handleUpload = async (type, file) => {
        try {
            await startUpload(type, file)
            // Success handling is done via useEffect watching uploadStates
        } catch (error) {
            // Error handling is managed by context toast
        }
    }

    // Delete profile
    const handleDelete = async (type) => {
        try {
            await profileApi.delete(type)
            setProfiles(prev => {
                const updated = { ...prev }
                delete updated[type]
                return updated
            })
            if (expandedProfile === type) setExpandedProfile(null)
            toast.success('Profile removed')
        } catch (error) {
            toast.error('Failed to delete profile')
        }
    }

    const toggleExpand = (type) => {
        setExpandedProfile(expandedProfile === type ? null : type)
    }

    const getColorClasses = (color) => ({
        blue: 'from-blue-500/20 to-blue-600/20 border-blue-500/30',
        cyan: 'from-cyan-500/20 to-cyan-600/20 border-cyan-500/30',
        purple: 'from-purple-500/20 to-purple-600/20 border-purple-500/30'
    }[color])

    const getIconColor = (color) => ({
        blue: 'text-blue-400',
        cyan: 'text-cyan-400',
        purple: 'text-purple-400'
    }[color])

    // Extract skills from parsed_data
    const getSkills = (profile) => {
        if (!profile?.parsed_data) return []
        const data = profile.parsed_data

        // Try different skill locations based on profile type
        if (data.technical_skills) {
            const allSkills = []
            Object.values(data.technical_skills).forEach(skills => {
                if (Array.isArray(skills)) allSkills.push(...skills)
            })
            return allSkills.slice(0, 6)
        }
        if (data.top_skills) return data.top_skills
        return []
    }

    // Extract experience from parsed_data
    const getExperience = (profile) => {
        if (!profile?.parsed_data) return []
        const data = profile.parsed_data

        if (data.work_experience) return data.work_experience.slice(0, 2)
        if (data.experience) return data.experience.slice(0, 2)
        if (data.professional_experience) return data.professional_experience.slice(0, 2)
        return []
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
            <div>
                <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-1 flex items-center gap-3">
                    <User className="w-8 h-8 text-blue-400" />
                    Your Profiles
                </h1>
                <p className="text-[var(--text-secondary)]">Upload and manage your resume and profiles for better job matching</p>
            </div>

            {/* Profile Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {profileTypes.map(({ type, label, icon: Icon, color, description, accept }, index) => {
                    const profile = profiles[type]
                    const uploadState = getUploadStatus(type)
                    const isUploading = uploadState.status === 'uploading'
                    const isExpanded = expandedProfile === type

                    return (
                        <motion.div
                            key={type}
                            layout
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className={`glass-card flex flex-col ${isExpanded ? 'md:col-span-2 lg:col-span-3' : ''}`}
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${getColorClasses(color)} flex items-center justify-center border`}>
                                        <Icon className={`w-5 h-5 ${getIconColor(color)}`} />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-[var(--text-primary)]">{label}</h3>
                                        {profile ? (
                                            <p className="text-xs text-[var(--text-secondary)] truncate max-w-[200px]">{profile.file_name}</p>
                                        ) : (
                                            <p className="text-xs text-[var(--text-tertiary)]">Not uploaded</p>
                                        )}
                                    </div>
                                </div>
                                {profile && (
                                    <div className="flex gap-1">
                                        <button
                                            onClick={() => toggleExpand(type)}
                                            className="p-2 rounded-lg hover:bg-[var(--glass-hover)] text-[var(--text-tertiary)] hover:text-blue-400 transition-colors"
                                        >
                                            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                                        </button>
                                        <button
                                            onClick={() => handleDelete(type)}
                                            className="p-2 rounded-lg hover:bg-red-500/10 text-[var(--text-tertiary)] hover:text-red-400 transition-colors"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                )}
                            </div>

                            {/* Content */}
                            {profile ? (
                                <div className="space-y-4">
                                    {!isExpanded && (
                                        <motion.div
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            className="flex items-center gap-2 p-3 rounded-xl border"
                                            style={{ background: 'var(--bg-success)', borderColor: 'var(--border-success)' }}
                                        >
                                            <CheckCircle className="w-4 h-4" style={{ color: 'var(--color-success)' }} />
                                            <span className="text-sm font-medium" style={{ color: 'var(--color-success)' }}>Ready for analysis</span>
                                        </motion.div>
                                    )}

                                    <AnimatePresence>
                                        {isExpanded && (
                                            <motion.div
                                                initial={{ height: 0, opacity: 0 }}
                                                animate={{ height: 'auto', opacity: 1 }}
                                                exit={{ height: 0, opacity: 0 }}
                                                className="overflow-hidden"
                                            >
                                                <div className="pt-4 border-t border-[var(--glass-border)] space-y-6">
                                                    {/* Full Width File Preview */}
                                                    <div>
                                                        <h4 className="text-xs font-semibold uppercase text-[var(--text-tertiary)] mb-2">
                                                            {type === 'portfolio' ? 'Portfolio Preview' : 'Document Preview'}
                                                        </h4>
                                                        <div className="rounded-xl border border-[var(--glass-border)] overflow-hidden bg-white" style={{ height: '500px' }}>
                                                            {type === 'portfolio' ? (
                                                                <iframe
                                                                    src={profileApi.getFileUrl(profile.id)}
                                                                    className="w-full h-full"
                                                                    title="Portfolio Preview"
                                                                    sandbox="allow-same-origin"
                                                                />
                                                            ) : (
                                                                <iframe
                                                                    src={profileApi.getFileUrl(profile.id)}
                                                                    className="w-full h-full"
                                                                    title="PDF Preview"
                                                                />
                                                            )}
                                                        </div>
                                                    </div>

                                                    {/* Parsed Data in Grid */}
                                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                                        {/* Personal Info */}
                                                        {profile.parsed_data?.personal_info && (
                                                            <div>
                                                                <h4 className="text-xs font-semibold uppercase text-[var(--text-tertiary)] mb-2">Personal Info</h4>
                                                                <div className="p-4 rounded-xl bg-[var(--input-bg)] space-y-1">
                                                                    <p className="font-semibold text-[var(--text-primary)]">{profile.parsed_data.personal_info.name}</p>
                                                                    <p className="text-sm text-[var(--text-secondary)]">{profile.parsed_data.personal_info.email}</p>
                                                                    {profile.parsed_data.personal_info.location && (
                                                                        <p className="text-sm text-[var(--text-tertiary)]">{profile.parsed_data.personal_info.location}</p>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        )}

                                                        {/* Skills Preview */}
                                                        {getSkills(profile).length > 0 && (
                                                            <div>
                                                                <h4 className="text-xs font-semibold uppercase text-[var(--text-tertiary)] mb-2">Skills Found</h4>
                                                                <div className="flex flex-wrap gap-1.5">
                                                                    {getSkills(profile).map((skill, i) => (
                                                                        <span key={i} className="px-2 py-0.5 text-xs rounded bg-[var(--glass-hover)] text-[var(--text-secondary)] border border-[var(--glass-border)]">
                                                                            {skill}
                                                                        </span>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        )}

                                                        {/* Experience */}
                                                        {getExperience(profile).length > 0 && (
                                                            <div>
                                                                <h4 className="text-xs font-semibold uppercase text-[var(--text-tertiary)] mb-2">Recent Experience</h4>
                                                                <div className="space-y-2">
                                                                    {getExperience(profile).map((exp, i) => (
                                                                        <div key={i} className="p-3 rounded-xl bg-[var(--input-bg)]">
                                                                            <p className="font-medium text-[var(--text-primary)] text-sm">{exp.title || exp.role}</p>
                                                                            <p className="text-xs text-[var(--text-secondary)]">{exp.company || exp.organization}</p>
                                                                            <p className="text-xs text-[var(--text-tertiary)] mt-1">{exp.dates || exp.duration}</p>
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>

                                                    {/* Raw Parsed Data Preview */}
                                                    <div>
                                                        <h4 className="text-xs font-semibold uppercase text-[var(--text-tertiary)] mb-2">Extracted JSON Data</h4>
                                                        <pre className="p-4 rounded-xl bg-black/20 text-xs text-[var(--text-secondary)] overflow-auto max-h-[200px] border border-[var(--glass-border)]">
                                                            {JSON.stringify(profile.parsed_data, null, 2)}
                                                        </pre>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>

                                    {/* Re-upload */}
                                    {!isExpanded && (
                                        <label className="block cursor-pointer mt-2">
                                            <input
                                                type="file"
                                                accept={accept}
                                                onChange={(e) => e.target.files?.[0] && handleUpload(type, e.target.files[0])}
                                                className="hidden"
                                            />
                                            <div className="text-center py-2 text-xs text-[var(--text-tertiary)] hover:text-blue-400 transition-colors">
                                                Update file
                                            </div>
                                        </label>
                                    )}
                                </div>
                            ) : (
                                /* Upload Area */
                                <label className="block cursor-pointer flex-1 min-h-[140px]">
                                    <input
                                        type="file"
                                        accept={accept}
                                        onChange={(e) => e.target.files?.[0] && handleUpload(type, e.target.files[0])}
                                        className="hidden"
                                        disabled={isUploading}
                                    />
                                    <div className="flex flex-col items-center justify-center h-full border-2 border-dashed border-[var(--glass-border)] rounded-xl p-4 text-center hover:border-[var(--text-tertiary)] hover:bg-[var(--glass-hover)] transition-all">
                                        {isUploading ? (
                                            <Loader2 className="w-8 h-8 text-blue-400 animate-spin mb-2" />
                                        ) : (
                                            <Upload className="w-8 h-8 text-[var(--text-tertiary)] mb-2" />
                                        )}
                                        <p className="text-sm text-[var(--text-secondary)]">
                                            {isUploading ? 'Uploading...' : description}
                                        </p>
                                        <p className="text-xs text-[var(--text-tertiary)] mt-1">
                                            {accept.replace(/\./g, '').toUpperCase()} only
                                        </p>
                                    </div>
                                </label>
                            )}
                        </motion.div>
                    )
                })}
            </div>
        </div>
    )
}

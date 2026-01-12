/**
 * Wand API Client
 * All API calls to the backend with JWT authentication
 */

const API_BASE = 'http://localhost:8000';

// Get token from localStorage
const getToken = () => localStorage.getItem('wand_token');

// Common headers with auth
const getHeaders = () => {
    const headers = {
        'Accept': 'application/json'
    };

    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
};

// ============================================================================
// AUTH APIs (handled by AuthContext, but available here too)
// ============================================================================

export const authApi = {
    register: async (email, password, name) => {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
            body: JSON.stringify({ email, password, name })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        return response.json();
    },

    login: async (email, password) => {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        return response.json();
    },

    getMe: async () => {
        const response = await fetch(`${API_BASE}/auth/me`, {
            headers: getHeaders()
        });

        if (!response.ok) throw new Error('Not authenticated');
        return response.json();
    }
};

// ============================================================================
// PROFILE APIs
// ============================================================================

export const profileApi = {
    // Upload profile (resume, linkedin, portfolio)
    upload: async (type, file) => {
        const formData = new FormData();
        formData.append('file', file);

        const headers = {};
        const token = getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE}/profile/${type}`, {
            method: 'POST',
            headers,
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        return response.json();
    },

    // Get specific profile type
    get: async (type) => {
        const response = await fetch(`${API_BASE}/profile/${type}`, {
            headers: getHeaders()
        });

        if (response.status === 404) return null;
        if (!response.ok) throw new Error('Failed to get profile');

        return response.json();
    },

    // Get all profiles
    list: async () => {
        const response = await fetch(`${API_BASE}/profile/`, {
            headers: getHeaders()
        });

        if (!response.ok) throw new Error('Failed to list profiles');
        return response.json();
    },

    // Delete profile
    delete: async (type) => {
        const response = await fetch(`${API_BASE}/profile/${type}`, {
            method: 'DELETE',
            headers: getHeaders()
        });

        if (!response.ok) throw new Error('Failed to delete profile');
        return response.json();
    },

    // Get file URL for preview (returns URL with auth token)
    getFileUrl: (profileId) => {
        const token = getToken();
        return `${API_BASE}/profile/${profileId}/file?token=${token}`;
    }
};

// ============================================================================
// JOB APIs
// ============================================================================

export const jobApi = {
    // Parse job posting
    parsePosting: async (jobText, jobTitle = null, companyName = null) => {
        const response = await fetch(`${API_BASE}/job/posting`, {
            method: 'POST',
            headers: { ...getHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_text: jobText,
                job_title: jobTitle,
                company_name: companyName
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to parse job');
        }

        return response.json();
    },

    // Get company intelligence
    getCompanyIntel: async (companyName, options = {}) => {
        const response = await fetch(`${API_BASE}/job/company`, {
            method: 'POST',
            headers: { ...getHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify({
                company_name: companyName,
                max_jobs: options.maxJobs || 50,
                include_website: options.includeWebsite !== false,
                include_news: options.includeNews !== false
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get company intel');
        }

        return response.json();
    },

    // Get job by ID
    get: async (jobId) => {
        const response = await fetch(`${API_BASE}/job/${jobId}`, {
            headers: getHeaders()
        });

        if (!response.ok) throw new Error('Job not found');
        return response.json();
    },

    // List all jobs
    list: async () => {
        const response = await fetch(`${API_BASE}/job/`, {
            headers: getHeaders()
        });

        if (!response.ok) throw new Error('Failed to list jobs');
        return response.json();
    },

    // Delete job
    delete: async (jobId) => {
        const response = await fetch(`${API_BASE}/job/${jobId}`, {
            method: 'DELETE',
            headers: getHeaders()
        });

        if (!response.ok) throw new Error('Failed to delete job');
        return response.json();
    }
};

// ============================================================================
// MATCH APIs
// ============================================================================

export const matchApi = {
    // Analyze gaps between profiles and job
    analyzeGaps: async (profileIds, jobId) => {
        const response = await fetch(`${API_BASE}/match/gaps`, {
            method: 'POST',
            headers: { ...getHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify({
                profile_ids: profileIds,
                job_id: jobId
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Gap analysis failed');
        }

        return response.json();
    },

    // Get specific gap analysis by ID
    get: async (analysisId) => {
        const response = await fetch(`${API_BASE}/match/gaps/${analysisId}`, {
            headers: getHeaders()
        });

        if (!response.ok) throw new Error('Failed to get gap analysis');
        return response.json();
    },

    // Get existing gap analysis by job ID
    getByJobId: async (jobId) => {
        const response = await fetch(`${API_BASE}/match/gaps/by-job/${jobId}`, {
            headers: getHeaders()
        });

        if (response.status === 404) return null;
        if (!response.ok) throw new Error('Failed to get gap analysis');

        return response.json();
    },

    // Generate cover letter
    generateCoverLetter: async (profileIds, jobId, style = 'professional') => {
        const response = await fetch(`${API_BASE}/match/cover-letter`, {
            method: 'POST',
            headers: { ...getHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify({
                profile_ids: profileIds,
                job_id: jobId,
                style: style
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Cover letter generation failed');
        }

        return response.json();
    },

    // Optimize Resume
    optimizeResume: async (resumeId, jobId) => {
        const response = await fetch(`${API_BASE}/match/resume-optimize`, {
            method: 'POST',
            headers: { ...getHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify({
                resume_id: resumeId,
                job_id: jobId
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Resume optimization failed');
        }

        return response.json();
    },

    // List cover letters
    listCoverLetters: async () => {
        const response = await fetch(`${API_BASE}/match/cover-letters/`, {
            headers: getHeaders()
        });

        if (!response.ok) throw new Error('Failed to list cover letters');
        return response.json();
    },

    // Delete cover letter
    deleteCoverLetter: async (letterId) => {
        const response = await fetch(`${API_BASE}/match/cover-letter/${letterId}`, {
            method: 'DELETE',
            headers: getHeaders()
        });

        if (!response.ok) throw new Error('Failed to delete cover letter');
        return response.json();
    }
};

// ============================================================================
// DISCREPANCY APIs
// ============================================================================

export const discrepancyApi = {
    // Compare profiles for discrepancies
    compare: async (profileIds) => {
        const response = await fetch(`${API_BASE}/discrepancy/compare`, {
            method: 'POST',
            headers: { ...getHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify({ profile_ids: profileIds })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Discrepancy analysis failed');
        }

        return response.json();
    },

    // Get history of discrepancy reports
    getHistory: async () => {
        const response = await fetch(`${API_BASE}/discrepancy/history`, {
            headers: getHeaders()
        });

        if (!response.ok) throw new Error('Failed to fetch history');
        return response.json();
    },

    // Get specific report by ID
    get: async (reportId) => {
        const response = await fetch(`${API_BASE}/discrepancy/${reportId}`, {
            headers: getHeaders()
        });

        if (!response.ok) throw new Error('Failed to fetch report');
        return response.json();
    }
};

// Export all
export default {
    auth: authApi,
    profile: profileApi,
    job: jobApi,
    match: matchApi,
    discrepancy: discrepancyApi
};

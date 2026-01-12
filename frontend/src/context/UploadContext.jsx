import { createContext, useContext, useState, useCallback } from 'react'
import { toast } from 'sonner'
import { profileApi } from '../api/client'

const UploadContext = createContext(null)

export function UploadProvider({ children }) {
    // Track upload state by profile type: { [type]: { status: 'idle' | 'uploading' | 'success' | 'error', error: null } }
    const [uploadStates, setUploadStates] = useState({})

    const startUpload = useCallback(async (type, file) => {
        // Set state to uploading
        setUploadStates(prev => ({
            ...prev,
            [type]: { status: 'uploading', error: null }
        }))

        const toastId = toast.loading(`Uploading ${type}...`)

        try {
            // Perform upload
            const result = await profileApi.upload(type, file)

            // Set success
            setUploadStates(prev => ({
                ...prev,
                [type]: { status: 'success', error: null }
            }))

            toast.success(`${type} uploaded successfully`, { id: toastId })

            // Clear success state after delay to reset UI
            setTimeout(() => {
                setUploadStates(prev => {
                    const current = { ...prev }
                    delete current[type]
                    return current
                })
            }, 3000)

            return result
        } catch (error) {
            console.error(`Upload failed for ${type}:`, error)

            // Set error
            setUploadStates(prev => ({
                ...prev,
                [type]: { status: 'error', error: error.message }
            }))

            toast.error(`Failed to upload ${type}: ${error.message}`, { id: toastId })
            throw error
        }
    }, [])

    const getUploadStatus = useCallback((type) => {
        return uploadStates[type] || { status: 'idle', error: null }
    }, [uploadStates])

    return (
        <UploadContext.Provider value={{ startUpload, getUploadStatus, uploadStates }}>
            {children}
        </UploadContext.Provider>
    )
}

export function useUpload() {
    const context = useContext(UploadContext)
    if (!context) {
        throw new Error('useUpload must be used within an UploadProvider')
    }
    return context
}

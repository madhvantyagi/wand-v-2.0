import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { toast } from 'sonner'
import { analyzeApi } from '../api/client'
import { useAnalysisWebSocket } from '../hooks/useAnalysisWebSocket'

const AnalysisContext = createContext(null)

export function useAnalysis() {
    return useContext(AnalysisContext)
}

export function AnalysisProvider({ children }) {
    const [analysisTasks, setAnalysisTasks] = useState([])
    const [isQueueOpen, setIsQueueOpen] = useState(true)

    // WebSocket callbacks
    const handleStatusUpdate = useCallback((data) => {
        // Only show toast for relevant status changes to avoid spam
        if (data.status !== 'pending' && data.status !== 'processing') {
            toast.loading(data.message, { id: `task-${data.task_id}` })
        }

        setAnalysisTasks(prev => prev.map(task =>
            task.task_id === data.task_id
                ? { ...task, status: data.status, progress_message: data.message, progress: data.progress, total_duration: data.total_duration, job_title: data.job_title }
                : task
        ))
    }, [])

    const handleComplete = useCallback((data) => {
        toast.success(`Analysis complete! Match: ${data.match_score}%`, { id: `task-${data.task_id}` })

        setAnalysisTasks(prev => prev.map(task =>
            task.task_id === data.task_id
                ? { ...task, status: 'complete', progress: 100, result_job_id: data.job_id, total_duration: data.total_duration, job_title: data.job_title }
                : task
        ))
    }, [])

    const handleError = useCallback((data) => {
        toast.error(data.message || data.error || 'Analysis failed', { id: `task-${data.task_id}` })

        setAnalysisTasks(prev => prev.map(task =>
            task.task_id === data.task_id
                ? { ...task, status: 'failed', error_message: data.message || data.error, total_duration: data.total_duration }
                : task
        ))
    }, [])

    // Initialize WebSocket
    const { isConnected } = useAnalysisWebSocket({
        onStatusUpdate: handleStatusUpdate,
        onComplete: handleComplete,
        onError: handleError
    })

    // Load tasks on mount
    useEffect(() => {
        loadTasks()
    }, [])

    const loadTasks = async () => {
        try {
            const tasks = await analyzeApi.getTasks()
            setAnalysisTasks(tasks)
        } catch (error) {
            console.error('Failed to load tasks:', error)
        }
    }

    const addAnalysisTask = (task) => {
        setAnalysisTasks(prev => [task, ...prev])
        // If queue was closed, open it to show the new task
        setIsQueueOpen(true)
    }

    const handleDeleteTask = async (taskId) => {
        try {
            await analyzeApi.deleteTask(taskId)
            setAnalysisTasks(prev => prev.filter(t => t.task_id !== taskId))
            toast.success('Task removed from queue')
        } catch (error) {
            console.error('Failed to delete task:', error)
            toast.error('Failed to remove task')
        }
    }

    const handleClearTasks = async () => {
        try {
            await analyzeApi.clearTasks()
            setAnalysisTasks([])
            toast.success('All tasks cleared')
        } catch (error) {
            console.error('Failed to clear tasks:', error)
            // We allow the caller to handle the error too if they need to close a modal
            throw error
        }
    }

    // Derived state
    const activeTasks = analysisTasks.filter(t => !['complete', 'failed'].includes(t.status))
    const recentTasks = analysisTasks.filter(t => ['complete', 'failed'].includes(t.status)).slice(0, 3)

    return (
        <AnalysisContext.Provider value={{
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
        }}>
            {children}
        </AnalysisContext.Provider>
    )
}

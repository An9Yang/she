'use client'

import { useState, useCallback } from 'react'
import { Upload, X, FileText, CheckCircle, AlertCircle, Cloud, Sparkles } from 'lucide-react'
import api from '@/services/api'

interface FileUploadProps {
  onSuccess?: (personaId: string) => void
}

export default function FileUpload({ onSuccess }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'success' | 'error'>('idle')
  const [progress, setProgress] = useState(0)
  const [errorMessage, setErrorMessage] = useState('')

  const acceptedFormats = ['.txt', '.json', '.csv', '.html', '.zip']

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      validateAndSetFile(droppedFile)
    }
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      validateAndSetFile(selectedFile)
    }
  }

  const validateAndSetFile = (file: File) => {
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase()
    
    if (!acceptedFormats.includes(fileExt)) {
      setErrorMessage(`不支持的文件格式。支持的格式: ${acceptedFormats.join(', ')}`)
      return
    }

    // 限制文件大小 (100MB)
    if (file.size > 100 * 1024 * 1024) {
      setErrorMessage('文件大小不能超过100MB')
      return
    }

    setFile(file)
    setErrorMessage('')
  }

  const handleUpload = async () => {
    if (!file) return

    setUploadStatus('uploading')
    setProgress(0)

    try {
      // 上传文件
      const uploadResponse = await api.upload.uploadFile(file)
      const taskId = uploadResponse.task_id

      setUploadStatus('processing')
      
      // 轮询任务状态
      let attempts = 0
      const maxAttempts = 60 // 最多等待5分钟
      
      const checkStatus = async () => {
        if (attempts >= maxAttempts) {
          throw new Error('处理超时')
        }
        
        const status = await api.upload.getTaskStatus(taskId)
        
        if (status.status === 'completed') {
          setUploadStatus('success')
          setProgress(100)
          if (status.persona_id && onSuccess) {
            onSuccess(status.persona_id)
          }
        } else if (status.status === 'failed') {
          throw new Error(status.error || '处理失败')
        } else {
          // 继续等待
          setProgress(Math.min(90, progress + 10))
          attempts++
          setTimeout(checkStatus, 5000) // 5秒后再次检查
        }
      }

      await checkStatus()
      
    } catch (error: any) {
      setUploadStatus('error')
      setErrorMessage(error.message || '上传失败')
    }
  }

  const reset = () => {
    setFile(null)
    setUploadStatus('idle')
    setProgress(0)
    setErrorMessage('')
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      {uploadStatus === 'idle' && !file && (
        <div
          className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 overflow-hidden ${
            isDragging 
              ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 scale-[1.02]' 
              : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 bg-gray-50 dark:bg-gray-800/50'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {/* Background decoration */}
          <div className="absolute inset-0 opacity-5">
            <div className="absolute top-10 left-10 w-32 h-32 bg-blue-500 rounded-full blur-3xl" />
            <div className="absolute bottom-10 right-10 w-40 h-40 bg-purple-500 rounded-full blur-3xl" />
          </div>
          
          <div className="relative z-10">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-400 to-purple-400 flex items-center justify-center shadow-lg transform transition-transform hover:scale-110">
              <Cloud className="w-10 h-10 text-white" />
            </div>
            
            <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">
              拖拽文件到这里上传
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">或者点击下方按钮选择文件</p>
            
            <label className="inline-block">
              <input
                type="file"
                className="hidden"
                accept={acceptedFormats.join(',')}
                onChange={handleFileSelect}
              />
              <span className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-8 py-3 rounded-xl cursor-pointer hover:from-blue-600 hover:to-purple-600 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl inline-flex items-center gap-2">
                <Upload className="w-5 h-5" />
                选择文件
              </span>
            </label>
            
            <div className="mt-8 space-y-2">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                支持格式: {acceptedFormats.join(', ')}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                最大文件大小: 100MB
              </p>
            </div>
            
            {/* Feature badges */}
            <div className="mt-6 flex justify-center gap-4">
              <div className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
                <Sparkles className="w-4 h-4 text-yellow-500" />
                <span>智能解析</span>
              </div>
              <div className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>安全加密</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {file && uploadStatus === 'idle' && (
        <div className="card-modern p-6 fade-in">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 flex items-center justify-center mr-4">
                <FileText className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="font-semibold text-gray-900 dark:text-white">{file.name}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={reset}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200 hover:scale-110"
            >
              <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>
          </div>
          <button
            onClick={handleUpload}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 rounded-xl hover:from-blue-600 hover:to-purple-600 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl font-medium"
          >
            开始上传
          </button>
        </div>
      )}

      {(uploadStatus === 'uploading' || uploadStatus === 'processing') && (
        <div className="card-modern p-6 scale-in">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <p className="font-semibold text-gray-900 dark:text-white">
                {uploadStatus === 'uploading' ? '上传中...' : '处理中...'}
              </p>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {progress}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500 relative overflow-hidden bg-gradient-to-r from-blue-500 to-purple-500"
                style={{ width: `${progress}%` }}
              >
                <div className="absolute inset-0 bg-white/30 animate-pulse" />
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {uploadStatus === 'uploading' 
                ? '正在安全上传您的文件...' 
                : '正在智能分析聊天记录，这可能需要几分钟...'}
            </p>
          </div>
        </div>
      )}

      {uploadStatus === 'success' && (
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-2xl p-8 text-center scale-in">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-green-400 to-emerald-400 flex items-center justify-center shadow-lg animate-bounce">
            <CheckCircle className="w-12 h-12 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">上传成功！</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">聊天记录已成功导入，AI正在学习中...</p>
          <button
            onClick={reset}
            className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-8 py-3 rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl font-medium"
          >
            继续上传
          </button>
        </div>
      )}

      {uploadStatus === 'error' && (
        <div className="bg-gradient-to-br from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 rounded-2xl p-6 fade-in">
          <div className="flex items-start mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-400 to-pink-400 flex items-center justify-center mr-4 flex-shrink-0">
              <AlertCircle className="w-7 h-7 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-gray-900 dark:text-white mb-1">上传失败</p>
              <p className="text-gray-700 dark:text-gray-300">{errorMessage}</p>
            </div>
          </div>
          <button
            onClick={reset}
            className="w-full bg-gradient-to-r from-red-500 to-pink-500 text-white px-6 py-3 rounded-xl hover:from-red-600 hover:to-pink-600 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl font-medium"
          >
            重新尝试
          </button>
        </div>
      )}

      {errorMessage && uploadStatus === 'idle' && (
        <div className="mt-4 bg-red-50 dark:bg-red-900/20 rounded-xl p-4 border border-red-200 dark:border-red-800 fade-in">
          <p className="text-red-600 dark:text-red-400 text-sm flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            {errorMessage}
          </p>
        </div>
      )}
    </div>
  )
}
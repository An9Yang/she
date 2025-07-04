'use client'

import { useState, useCallback } from 'react'
import { Upload, X, FileText, CheckCircle, AlertCircle } from 'lucide-react'
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
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p className="text-lg mb-2">拖拽文件到这里，或者</p>
          <label className="inline-block">
            <input
              type="file"
              className="hidden"
              accept={acceptedFormats.join(',')}
              onChange={handleFileSelect}
            />
            <span className="bg-blue-600 text-white px-4 py-2 rounded-lg cursor-pointer hover:bg-blue-700">
              选择文件
            </span>
          </label>
          <p className="text-sm text-gray-500 mt-4">
            支持格式: {acceptedFormats.join(', ')} (最大100MB)
          </p>
        </div>
      )}

      {file && uploadStatus === 'idle' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <FileText className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <p className="font-semibold">{file.name}</p>
                <p className="text-sm text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={reset}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
          <button
            onClick={handleUpload}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            开始上传
          </button>
        </div>
      )}

      {(uploadStatus === 'uploading' || uploadStatus === 'processing') && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="mb-4">
            <p className="font-semibold mb-2">
              {uploadStatus === 'uploading' ? '上传中...' : '处理中...'}
            </p>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
          <p className="text-sm text-gray-500">
            {uploadStatus === 'uploading' 
              ? '正在上传文件...' 
              : '正在分析聊天记录，这可能需要几分钟...'}
          </p>
        </div>
      )}

      {uploadStatus === 'success' && (
        <div className="bg-green-50 rounded-lg p-6 text-center">
          <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
          <p className="text-lg font-semibold text-green-800 mb-2">上传成功！</p>
          <p className="text-gray-600 mb-4">聊天记录已成功导入</p>
          <button
            onClick={reset}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
          >
            继续上传
          </button>
        </div>
      )}

      {uploadStatus === 'error' && (
        <div className="bg-red-50 rounded-lg p-6">
          <div className="flex items-start">
            <AlertCircle className="w-6 h-6 text-red-600 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-semibold text-red-800 mb-1">上传失败</p>
              <p className="text-red-600">{errorMessage}</p>
            </div>
          </div>
          <button
            onClick={reset}
            className="mt-4 bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700"
          >
            重试
          </button>
        </div>
      )}

      {errorMessage && uploadStatus === 'idle' && (
        <div className="mt-4 bg-red-50 rounded-lg p-4">
          <p className="text-red-600 text-sm">{errorMessage}</p>
        </div>
      )}
    </div>
  )
}
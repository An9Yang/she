'use client'

import { MessageCircle, Calendar, BarChart3, Trash2, Sparkles, User } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface PersonaCardProps {
  persona: {
    id: string
    name: string
    message_count: number
    created_at: string
    status: string
    date_range_start?: string
    date_range_end?: string
  }
  onDelete?: (id: string) => void
  index?: number
}

export default function PersonaCard({ persona, onDelete, index = 0 }: PersonaCardProps) {
  const router = useRouter()

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'ready':
        return {
          color: 'from-green-400 to-green-500',
          bgColor: 'bg-green-50 dark:bg-green-900/20',
          text: '可用',
          textColor: 'text-green-700 dark:text-green-300'
        }
      case 'processing':
        return {
          color: 'from-yellow-400 to-orange-400',
          bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
          text: '处理中',
          textColor: 'text-yellow-700 dark:text-yellow-300'
        }
      case 'error':
        return {
          color: 'from-red-400 to-red-500',
          bgColor: 'bg-red-50 dark:bg-red-900/20',
          text: '错误',
          textColor: 'text-red-700 dark:text-red-300'
        }
      default:
        return {
          color: 'from-gray-400 to-gray-500',
          bgColor: 'bg-gray-50 dark:bg-gray-900/20',
          text: status,
          textColor: 'text-gray-700 dark:text-gray-300'
        }
    }
  }

  const handleStartChat = () => {
    router.push(`/chat/new?persona=${persona.id}`)
  }

  const handleViewDetails = () => {
    router.push(`/personas/${persona.id}`)
  }

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (onDelete && confirm(`确定要删除 ${persona.name} 吗？`)) {
      onDelete(persona.id)
    }
  }

  const statusConfig = getStatusConfig(persona.status)
  const gradientColors = ['gradient-1', 'gradient-2', 'gradient-3', 'gradient-4']
  const gradientClass = gradientColors[index % gradientColors.length]

  return (
    <div 
      className="group relative card-modern hover-lift cursor-pointer overflow-hidden fade-in"
      onClick={handleViewDetails}
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      {/* Gradient decoration */}
      <div className={`absolute top-0 right-0 w-32 h-32 opacity-10 blur-3xl rounded-full bg-gradient-to-br ${statusConfig.color}`} />
      
      <div className="relative p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              {/* Avatar */}
              <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${statusConfig.color} flex items-center justify-center shadow-lg transform transition-transform group-hover:scale-110`}>
                <User className="w-6 h-6 text-white" />
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  {persona.name}
                  {persona.status === 'ready' && (
                    <Sparkles className="w-4 h-4 text-yellow-500 animate-pulse" />
                  )}
                </h3>
                <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusConfig.bgColor} ${statusConfig.textColor}`}>
                  <span className={`w-2 h-2 rounded-full bg-gradient-to-r ${statusConfig.color} mr-1.5 ${persona.status === 'processing' ? 'animate-pulse' : ''}`} />
                  {statusConfig.text}
                </div>
              </div>
            </div>
          </div>
          
          {/* Delete button */}
          <button
            onClick={handleDelete}
            className="opacity-0 group-hover:opacity-100 p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all duration-200 transform hover:scale-110"
            title="删除"
          >
            <Trash2 className="w-4 h-4 text-red-500" />
          </button>
        </div>

        {/* Stats */}
        <div className="space-y-3">
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-300 transition-colors hover:text-gray-900 dark:hover:text-white">
            <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/20 mr-3">
              <MessageCircle className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            </div>
            <span className="font-medium">{persona.message_count}</span>
            <span className="ml-1">条消息</span>
          </div>
          
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-300 transition-colors hover:text-gray-900 dark:hover:text-white">
            <div className="p-2 rounded-lg bg-purple-50 dark:bg-purple-900/20 mr-3">
              <Calendar className="w-4 h-4 text-purple-600 dark:text-purple-400" />
            </div>
            <span>创建于 {formatDate(persona.created_at)}</span>
          </div>
          
          {persona.date_range_start && persona.date_range_end && (
            <div className="flex items-center text-sm text-gray-600 dark:text-gray-300 transition-colors hover:text-gray-900 dark:hover:text-white">
              <div className="p-2 rounded-lg bg-green-50 dark:bg-green-900/20 mr-3">
                <BarChart3 className="w-4 h-4 text-green-600 dark:text-green-400" />
              </div>
              <span className="text-xs">
                {formatDate(persona.date_range_start)} - {formatDate(persona.date_range_end)}
              </span>
            </div>
          )}
        </div>

        {/* Action button */}
        {persona.status === 'ready' && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              handleStartChat()
            }}
            className={`mt-5 w-full py-3 px-4 rounded-lg font-medium text-white transition-all duration-200 transform hover:scale-105 hover:shadow-lg bg-gradient-to-r ${statusConfig.color} relative overflow-hidden group`}
          >
            <span className="relative z-10 flex items-center justify-center gap-2">
              <MessageCircle className="w-4 h-4" />
              开始对话
            </span>
            <div className="absolute inset-0 bg-white/20 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-500" />
          </button>
        )}
        
        {persona.status === 'processing' && (
          <div className="mt-5 w-full py-3 px-4 rounded-lg bg-gray-100 dark:bg-gray-800 text-center">
            <div className="flex items-center justify-center gap-2 text-gray-600 dark:text-gray-400">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              <span className="text-sm">处理中...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
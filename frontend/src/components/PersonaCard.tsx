'use client'

import { MessageCircle, Calendar, BarChart3, Trash2 } from 'lucide-react'
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
}

export default function PersonaCard({ persona, onDelete }: PersonaCardProps) {
  const router = useRouter()

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
        return 'bg-green-100 text-green-800'
      case 'processing':
        return 'bg-yellow-100 text-yellow-800'
      case 'error':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'ready':
        return '可用'
      case 'processing':
        return '处理中'
      case 'error':
        return '错误'
      default:
        return status
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

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer" onClick={handleViewDetails}>
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{persona.name}</h3>
            <span className={`inline-block px-2 py-1 text-xs rounded-full mt-1 ${getStatusColor(persona.status)}`}>
              {getStatusText(persona.status)}
            </span>
          </div>
          <button
            onClick={handleDelete}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="删除"
          >
            <Trash2 className="w-4 h-4 text-gray-500" />
          </button>
        </div>

        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex items-center">
            <MessageCircle className="w-4 h-4 mr-2" />
            <span>{persona.message_count} 条消息</span>
          </div>
          <div className="flex items-center">
            <Calendar className="w-4 h-4 mr-2" />
            <span>创建于 {formatDate(persona.created_at)}</span>
          </div>
          {persona.date_range_start && persona.date_range_end && (
            <div className="flex items-center">
              <BarChart3 className="w-4 h-4 mr-2" />
              <span>
                {formatDate(persona.date_range_start)} - {formatDate(persona.date_range_end)}
              </span>
            </div>
          )}
        </div>

        {persona.status === 'ready' && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              handleStartChat()
            }}
            className="mt-4 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            开始对话
          </button>
        )}
      </div>
    </div>
  )
}
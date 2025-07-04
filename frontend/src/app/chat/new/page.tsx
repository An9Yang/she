'use client'

import { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import api from '@/services/api'

export default function NewChatPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const personaId = searchParams.get('persona')

  useEffect(() => {
    if (!personaId) {
      router.push('/personas')
      return
    }

    createNewChat()
  }, [personaId])

  const createNewChat = async () => {
    try {
      const chat = await api.chat.createChat(personaId!)
      router.replace(`/chat/${chat.id}`)
    } catch (error) {
      console.error('Failed to create chat:', error)
      router.push('/personas')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">创建对话中...</p>
      </div>
    </div>
  )
}
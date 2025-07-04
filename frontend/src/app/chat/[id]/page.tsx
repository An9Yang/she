'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Users, Menu } from 'lucide-react'
import ChatInterface from '@/components/ChatInterface'
import api from '@/services/api'

interface ChatData {
  id: string
  title: string
  persona_id: string
  messages: any[]
}

interface PersonaData {
  id: string
  name: string
}

export default function ChatPage() {
  const params = useParams()
  const router = useRouter()
  const chatId = params.id as string
  
  const [chat, setChat] = useState<ChatData | null>(null)
  const [persona, setPersona] = useState<PersonaData | null>(null)
  const [recentChats, setRecentChats] = useState<ChatData[]>([])
  const [showSidebar, setShowSidebar] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadChatData()
    loadRecentChats()
  }, [chatId])

  const loadChatData = async () => {
    try {
      const chatData = await api.chat.getChat(chatId)
      setChat(chatData)
      
      // 加载人格信息
      const personaData = await api.persona.get(chatData.persona_id)
      setPersona(personaData)
    } catch (error) {
      console.error('Failed to load chat:', error)
      router.push('/personas')
    } finally {
      setIsLoading(false)
    }
  }

  const loadRecentChats = async () => {
    try {
      const chats = await api.chat.listChats()
      setRecentChats(chats.slice(0, 10)) // 最近10个对话
    } catch (error) {
      console.error('Failed to load recent chats:', error)
    }
  }

  const handleNewChat = async () => {
    if (!persona) return
    
    try {
      const newChat = await api.chat.createChat(persona.id)
      router.push(`/chat/${newChat.id}`)
    } catch (error) {
      console.error('Failed to create new chat:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  if (!chat || !persona) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* 侧边栏 */}
      <div className={`${
        showSidebar ? 'translate-x-0' : '-translate-x-full'
      } fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="h-full flex flex-col">
          {/* 侧边栏头部 */}
          <div className="p-4 border-b">
            <button
              onClick={() => router.push('/personas')}
              className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              返回人格列表
            </button>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Users className="w-5 h-5 text-gray-500 mr-2" />
                <span className="font-semibold">{persona.name}</span>
              </div>
            </div>
          </div>

          {/* 新建对话按钮 */}
          <div className="p-4">
            <button
              onClick={handleNewChat}
              className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              新建对话
            </button>
          </div>

          {/* 最近对话列表 */}
          <div className="flex-1 overflow-y-auto">
            <div className="px-4 pb-2 text-sm text-gray-500">最近对话</div>
            {recentChats.map((recentChat) => (
              <button
                key={recentChat.id}
                onClick={() => router.push(`/chat/${recentChat.id}`)}
                className={`w-full text-left px-4 py-3 hover:bg-gray-100 transition-colors ${
                  recentChat.id === chatId ? 'bg-gray-100 border-l-4 border-blue-600' : ''
                }`}
              >
                <p className="font-medium text-sm truncate">{recentChat.title}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {recentChat.messages.length} 条消息
                </p>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="flex-1 flex flex-col">
        {/* 顶部栏 - 移动端 */}
        <div className="lg:hidden bg-white shadow-sm p-4 flex items-center justify-between">
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <Menu className="w-5 h-5" />
          </button>
          <span className="font-semibold">{chat.title}</span>
          <div className="w-9" /> {/* 占位 */}
        </div>

        {/* 聊天界面 */}
        <div className="flex-1 p-4 lg:p-6">
          <div className="h-full max-w-4xl mx-auto">
            <ChatInterface chatId={chatId} personaName={persona.name} />
          </div>
        </div>
      </div>

      {/* 遮罩层 - 移动端 */}
      {showSidebar && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setShowSidebar(false)}
        />
      )}
    </div>
  )
}
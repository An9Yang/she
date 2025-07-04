'use client'

import { useState, useEffect, useRef } from 'react'
import { Send, RefreshCw, Download, Trash2 } from 'lucide-react'
import api from '@/services/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface ChatInterfaceProps {
  chatId: string
  personaName: string
}

export default function ChatInterface({ chatId, personaName }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isRegenerating, setIsRegenerating] = useState<number | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // 加载聊天历史
  useEffect(() => {
    loadChatHistory()
  }, [chatId])

  // 自动滚动到底部
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadChatHistory = async () => {
    try {
      const chat = await api.chat.getChat(chatId)
      setMessages(chat.messages || [])
    } catch (error) {
      console.error('Failed to load chat history:', error)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage = inputValue.trim()
    setInputValue('')
    setIsLoading(true)

    // 立即显示用户消息
    const tempUserMessage: Message = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    }
    setMessages(prev => [...prev, tempUserMessage])

    try {
      const response = await api.chat.sendMessage(chatId, userMessage)
      
      // 更新消息列表
      if (response.user_message && response.assistant_message) {
        setMessages(prev => [
          ...prev.slice(0, -1), // 移除临时消息
          response.user_message,
          response.assistant_message,
        ])
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      // 移除临时消息
      setMessages(prev => prev.slice(0, -1))
      alert('发送失败，请重试')
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleRegenerate = async (messageIndex: number) => {
    setIsRegenerating(messageIndex)
    try {
      const response = await api.chat.regenerateMessage(chatId, messageIndex)
      
      // 更新指定位置的消息
      setMessages(prev => {
        const newMessages = [...prev]
        newMessages[messageIndex] = response
        return newMessages
      })
    } catch (error) {
      console.error('Failed to regenerate message:', error)
      alert('重新生成失败')
    } finally {
      setIsRegenerating(null)
    }
  }

  const handleExport = async () => {
    try {
      const data = await api.chat.exportChat(chatId)
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `chat-${personaName}-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export chat:', error)
      alert('导出失败')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* 头部 */}
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold">与 {personaName} 的对话</h2>
        <button
          onClick={handleExport}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="导出对话"
        >
          <Download className="w-5 h-5 text-gray-600" />
        </button>
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 mt-8">
            <p>开始你们的对话吧...</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] rounded-lg px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                <div className="flex items-center justify-between mt-1">
                  <span className={`text-xs ${
                    message.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                  }`}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                  {message.role === 'assistant' && (
                    <button
                      onClick={() => handleRegenerate(index)}
                      disabled={isRegenerating === index}
                      className={`ml-2 p-1 rounded hover:bg-gray-200 transition-colors ${
                        isRegenerating === index ? 'opacity-50' : ''
                      }`}
                      title="重新生成"
                    >
                      <RefreshCw className={`w-3 h-3 text-gray-500 ${
                        isRegenerating === index ? 'animate-spin' : ''
                      }`} />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="border-t p-4">
        <div className="flex items-end space-x-2">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入消息..."
            className="flex-1 resize-none rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px] max-h-32"
            rows={1}
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            className={`p-3 rounded-lg transition-colors ${
              !inputValue.trim() || isLoading
                ? 'bg-gray-200 text-gray-400'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}
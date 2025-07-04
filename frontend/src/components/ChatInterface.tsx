'use client'

import { useState, useEffect, useRef } from 'react'
import { Send, RefreshCw, Download, Trash2, Bot, Sparkles } from 'lucide-react'
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
    <div className="flex flex-col h-full bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      {/* 头部 */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-900">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center shadow-md">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              {personaName}
              <Sparkles className="w-4 h-4 text-yellow-500" />
            </h2>
            <p className="text-xs text-gray-600 dark:text-gray-400">AI对话助手</p>
          </div>
        </div>
        <button
          onClick={handleExport}
          className="p-2 hover:bg-white/50 dark:hover:bg-gray-700/50 rounded-lg transition-all duration-200 hover:scale-110"
          title="导出对话"
        >
          <Download className="w-5 h-5 text-gray-600 dark:text-gray-400" />
        </button>
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
        {messages.length === 0 ? (
          <div className="text-center mt-20 fade-in">
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-r from-blue-400 to-purple-400 flex items-center justify-center animate-pulse">
              <Bot className="w-10 h-10 text-white" />
            </div>
            <p className="text-gray-500 dark:text-gray-400 text-lg">开始你们的对话吧...</p>
            <p className="text-gray-400 dark:text-gray-500 text-sm mt-2">我已准备好与你交流</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} ${
                message.role === 'user' ? 'slide-in-right' : 'slide-in-left'
              }`}
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <div
                className={`relative max-w-[70%] rounded-2xl px-5 py-3 transition-all duration-200 hover:scale-[1.02] ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg'
                    : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 shadow-md border border-gray-200 dark:border-gray-700'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="absolute -left-10 top-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-400 to-purple-400 flex items-center justify-center shadow-md">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  </div>
                )}
                <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                <div className="flex items-center justify-between mt-2 pt-1 border-t border-gray-100 dark:border-gray-700">
                  <span className={`text-xs ${
                    message.role === 'user' ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
                  }`}>
                    {new Date(message.timestamp).toLocaleTimeString('zh-CN', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                  {message.role === 'assistant' && (
                    <button
                      onClick={() => handleRegenerate(index)}
                      disabled={isRegenerating === index}
                      className={`ml-2 p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 hover:scale-110 ${
                        isRegenerating === index ? 'opacity-50' : ''
                      }`}
                      title="重新生成"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 text-gray-500 dark:text-gray-400 ${
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
          <div className="flex justify-start slide-in-left">
            <div className="relative bg-white dark:bg-gray-800 rounded-2xl px-5 py-3 shadow-md border border-gray-200 dark:border-gray-700">
              <div className="absolute -left-10 top-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-400 to-purple-400 flex items-center justify-center shadow-md animate-pulse">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-sm text-gray-500 dark:text-gray-400 ml-1">思考中...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800">
        <div className="flex items-end space-x-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入消息..."
              className="w-full resize-none rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent min-h-[48px] max-h-32 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500 text-gray-900 dark:text-white"
              rows={1}
            />
            <div className="absolute right-2 bottom-2 text-xs text-gray-400 dark:text-gray-500">
              {inputValue.length > 0 && `${inputValue.length} 字符`}
            </div>
          </div>
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            className={`p-3 rounded-xl transition-all duration-200 transform hover:scale-105 disabled:hover:scale-100 ${
              !inputValue.trim() || isLoading
                ? 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500'
                : 'bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 shadow-lg hover:shadow-xl'
            }`}
          >
            <Send className={`w-5 h-5 ${inputValue.trim() && !isLoading ? 'transform rotate-0 hover:rotate-12 transition-transform' : ''}`} />
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-400 dark:text-gray-500 text-center">
          按 Enter 发送，Shift + Enter 换行
        </div>
      </div>
    </div>
  )
}
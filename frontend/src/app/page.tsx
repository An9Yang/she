'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Upload, MessageCircle, Brain, Shield } from 'lucide-react'

export default function HomePage() {
  const router = useRouter()
  
  // 开发模式 - 自动跳转到人格列表
  useEffect(() => {
    router.push('/personas')
  }, [router])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* 导航栏 */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Second Self</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/auth/login')}
                className="text-gray-700 hover:text-gray-900"
              >
                登录
              </button>
              <button
                onClick={() => router.push('/auth/register')}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                注册
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* 主hero部分 */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            把记忆转化为永恒的陪伴
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            上传聊天记录，AI会学习对方的说话风格，创建一个高度相似的数字分身，
            让你能够继续那些珍贵的对话。
          </p>
          <button
            onClick={() => router.push('/auth/register')}
            className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transform hover:scale-105 transition-all"
          >
            立即开始
          </button>
        </div>

        {/* 演示图片占位 */}
        <div className="mt-16 bg-white rounded-2xl shadow-xl p-8">
          <div className="bg-gray-100 rounded-lg h-96 flex items-center justify-center">
            <p className="text-gray-400">产品演示截图</p>
          </div>
        </div>
      </section>

      {/* 特性介绍 */}
      <section className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
            核心功能
          </h3>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Upload className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="text-lg font-semibold mb-2">一键导入</h4>
              <p className="text-gray-600">支持多平台聊天记录，ZIP直接上传</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Brain className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="text-lg font-semibold mb-2">智能分析</h4>
              <p className="text-gray-600">AI深度学习对话风格和人格特征</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageCircle className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="text-lg font-semibold mb-2">自然对话</h4>
              <p className="text-gray-600">高度还原的对话体验</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="text-lg font-semibold mb-2">隐私安全</h4>
              <p className="text-gray-600">数据加密存储，用户完全控制</p>
            </div>
          </div>
        </div>
      </section>

      {/* 页脚 */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>&copy; 2025 Second Self. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
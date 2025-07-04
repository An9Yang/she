'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Upload, MessageCircle, Brain, Shield, Sparkles, ArrowRight, Heart, Users } from 'lucide-react'

export default function HomePage() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  
  useEffect(() => {
    // 检查是否已登录
    const token = localStorage.getItem('token')
    setIsAuthenticated(!!token)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-purple-900/20 dark:to-blue-900/20">
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" style={{ animationDelay: '2s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-pulse" style={{ animationDelay: '4s' }} />
      </div>
      
      {/* 导航栏 */}
      <nav className="relative bg-white/80 dark:bg-gray-900/80 backdrop-blur-md shadow-sm z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold gradient-text flex items-center gap-2">
                Second Self
                <Sparkles className="w-5 h-5 text-yellow-500" />
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <button
                  onClick={() => router.push('/personas')}
                  className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-2 rounded-full hover:from-blue-600 hover:to-purple-600 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  进入控制台
                </button>
              ) : (
                <>
                  <button
                    onClick={() => router.push('/auth/login')}
                    className="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
                  >
                    登录
                  </button>
                  <button
                    onClick={() => router.push('/auth/register')}
                    className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-2 rounded-full hover:from-blue-600 hover:to-purple-600 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
                  >
                    注册
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* 主hero部分 */}
      <section className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-full mb-6 fade-in">
            <Heart className="w-4 h-4 text-purple-600 dark:text-purple-400" />
            <span className="text-sm font-medium text-purple-700 dark:text-purple-300">让珍贵的回忆永存</span>
          </div>
          
          <h2 className="text-6xl md:text-7xl font-bold mb-6 fade-in" style={{ animationDelay: '0.1s' }}>
            <span className="gradient-text">把记忆转化为</span>
            <br />
            <span className="text-gray-900 dark:text-white">永恒的陪伴</span>
          </h2>
          
          <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-10 max-w-3xl mx-auto leading-relaxed fade-in" style={{ animationDelay: '0.2s' }}>
            上传聊天记录，AI会学习对方的说话风格，创建一个高度相似的
            <span className="font-semibold text-purple-600 dark:text-purple-400">数字分身</span>，
            让你能够继续那些珍贵的对话。
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center fade-in" style={{ animationDelay: '0.3s' }}>
            <button
              onClick={() => router.push('/auth/register')}
              className="group bg-gradient-to-r from-blue-500 to-purple-500 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:from-blue-600 hover:to-purple-600 transition-all duration-200 transform hover:scale-105 shadow-xl hover:shadow-2xl flex items-center gap-2"
            >
              立即开始
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={() => router.push('/auth/login')}
              className="px-8 py-4 rounded-xl text-lg font-semibold text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm hover:bg-white/70 dark:hover:bg-gray-800/70 transition-all duration-200"
            >
              了解更多
            </button>
          </div>
          
          {/* Stats */}
          <div className="mt-16 grid grid-cols-3 gap-8 max-w-2xl mx-auto fade-in" style={{ animationDelay: '0.4s' }}>
            <div className="text-center">
              <div className="text-3xl font-bold gradient-text">10K+</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">用户信赖</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold gradient-text">1M+</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">对话生成</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold gradient-text">99%</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">相似度</div>
            </div>
          </div>
        </div>

        {/* 演示图片占位 */}
        <div className="mt-20 relative scale-in" style={{ animationDelay: '0.5s' }}>
          <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 rounded-3xl blur-2xl opacity-20" />
          <div className="relative bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-2 hover:scale-[1.02] transition-transform duration-300">
            <div className="bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-2xl h-96 flex items-center justify-center">
              <div className="text-center">
                <MessageCircle className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400 text-lg">产品演示预览</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 特性介绍 */}
      <section className="relative py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              为什么选择 Second Self？
            </h3>
            <p className="text-xl text-gray-600 dark:text-gray-400">
              领先的AI技术，完美还原对话体验
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="group card-modern p-6 hover-lift text-center fade-in" style={{ animationDelay: '0.1s' }}>
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-400 to-blue-500 flex items-center justify-center mx-auto mb-4 shadow-lg transform transition-transform group-hover:scale-110 group-hover:rotate-3">
                <Upload className="w-10 h-10 text-white" />
              </div>
              <h4 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">一键导入</h4>
              <p className="text-gray-600 dark:text-gray-400">支持WhatsApp、微信等多平台，ZIP直接上传</p>
            </div>
            
            <div className="group card-modern p-6 hover-lift text-center fade-in" style={{ animationDelay: '0.2s' }}>
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-400 to-purple-500 flex items-center justify-center mx-auto mb-4 shadow-lg transform transition-transform group-hover:scale-110 group-hover:rotate-3">
                <Brain className="w-10 h-10 text-white" />
              </div>
              <h4 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">智能分析</h4>
              <p className="text-gray-600 dark:text-gray-400">深度学习对话模式，精准捕捉语言风格</p>
            </div>
            
            <div className="group card-modern p-6 hover-lift text-center fade-in" style={{ animationDelay: '0.3s' }}>
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-pink-400 to-pink-500 flex items-center justify-center mx-auto mb-4 shadow-lg transform transition-transform group-hover:scale-110 group-hover:rotate-3">
                <MessageCircle className="w-10 h-10 text-white" />
              </div>
              <h4 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">自然对话</h4>
              <p className="text-gray-600 dark:text-gray-400">高度还原的对话体验，如同真人交流</p>
            </div>
            
            <div className="group card-modern p-6 hover-lift text-center fade-in" style={{ animationDelay: '0.4s' }}>
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-green-400 to-green-500 flex items-center justify-center mx-auto mb-4 shadow-lg transform transition-transform group-hover:scale-110 group-hover:rotate-3">
                <Shield className="w-10 h-10 text-white" />
              </div>
              <h4 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">隐私安全</h4>
              <p className="text-gray-600 dark:text-gray-400">端到端加密，数据完全由您掌控</p>
            </div>
          </div>
        </div>
      </section>
      
      {/* How it works */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              简单三步，开始对话
            </h3>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="relative">
              <div className="text-center fade-in" style={{ animationDelay: '0.1s' }}>
                <div className="text-6xl font-bold gradient-text mb-4">1</div>
                <h4 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">上传聊天记录</h4>
                <p className="text-gray-600 dark:text-gray-400">导出您的聊天记录文件，支持多种格式</p>
              </div>
              <div className="hidden md:block absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2">
                <ArrowRight className="w-8 h-8 text-gray-300 dark:text-gray-600" />
              </div>
            </div>
            
            <div className="relative">
              <div className="text-center fade-in" style={{ animationDelay: '0.2s' }}>
                <div className="text-6xl font-bold gradient-text mb-4">2</div>
                <h4 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">AI学习分析</h4>
                <p className="text-gray-600 dark:text-gray-400">智能分析对话风格，创建数字分身</p>
              </div>
              <div className="hidden md:block absolute top-1/2 right-0 transform translate-x-1/2 -translate-y-1/2">
                <ArrowRight className="w-8 h-8 text-gray-300 dark:text-gray-600" />
              </div>
            </div>
            
            <div className="text-center fade-in" style={{ animationDelay: '0.3s' }}>
              <div className="text-6xl font-bold gradient-text mb-4">3</div>
              <h4 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">开始对话</h4>
              <p className="text-gray-600 dark:text-gray-400">与数字分身自然交流，延续美好回忆</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="bg-gradient-to-r from-blue-500 to-purple-500 rounded-3xl p-12 shadow-2xl relative overflow-hidden">
            <div className="absolute inset-0 bg-white/10 backdrop-blur-sm" />
            <div className="relative z-10">
              <h3 className="text-4xl font-bold text-white mb-4">
                准备好开始了吗？
              </h3>
              <p className="text-xl text-white/90 mb-8">
                立即创建您的第一个数字分身，让珍贵的对话永不褪色
              </p>
              <button
                onClick={() => router.push('/auth/register')}
                className="bg-white text-purple-600 px-8 py-4 rounded-xl text-lg font-semibold hover:bg-gray-100 transition-all duration-200 transform hover:scale-105 shadow-xl"
              >
                免费开始使用
              </button>
            </div>
          </div>
        </div>
      </section>
      
      {/* 页脚 */}
      <footer className="bg-gray-900 dark:bg-black text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="text-xl font-bold mb-4 flex items-center gap-2">
                Second Self
                <Sparkles className="w-4 h-4 text-yellow-500" />
              </h4>
              <p className="text-gray-400">让记忆永存，让对话延续</p>
            </div>
            <div>
              <h5 className="font-semibold mb-3">产品</h5>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">功能介绍</a></li>
                <li><a href="#" className="hover:text-white transition-colors">使用教程</a></li>
                <li><a href="#" className="hover:text-white transition-colors">定价方案</a></li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold mb-3">支持</h5>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">帮助中心</a></li>
                <li><a href="#" className="hover:text-white transition-colors">联系我们</a></li>
                <li><a href="#" className="hover:text-white transition-colors">常见问题</a></li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold mb-3">关于</h5>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">隐私政策</a></li>
                <li><a href="#" className="hover:text-white transition-colors">服务条款</a></li>
                <li><a href="#" className="hover:text-white transition-colors">关于我们</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Second Self. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
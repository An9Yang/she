'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Plus, Upload as UploadIcon, LogOut } from 'lucide-react'
import PersonaCard from '@/components/PersonaCard'
import PersonaCardSkeleton from '@/components/PersonaCardSkeleton'
import FileUpload from '@/components/FileUpload'
import api from '@/services/api'

export default function PersonasPage() {
  const router = useRouter()
  const [personas, setPersonas] = useState([])
  const [showUpload, setShowUpload] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [currentUser, setCurrentUser] = useState<any>(null)

  useEffect(() => {
    checkAuthAndLoadData()
  }, [])

  const checkAuthAndLoadData = async () => {
    try {
      // 先检查认证
      const user = await api.auth.getCurrentUser()
      setCurrentUser(user)
      
      // 认证成功后再加载数据
      await loadPersonas()
    } catch (error: any) {
      // 跳转到登录页
      router.push('/auth/login')
    }
  }

  const loadPersonas = async () => {
    try {
      const data = await api.persona.list()
      setPersonas(data)
    } catch (error) {
      console.error('Failed to load personas:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (personaId: string) => {
    try {
      await api.persona.delete(personaId)
      setPersonas(personas.filter((p: any) => p.id !== personaId))
    } catch (error) {
      console.error('Failed to delete persona:', error)
      alert('删除失败')
    }
  }

  const handleUploadSuccess = (personaId: string) => {
    setShowUpload(false)
    loadPersonas()
  }

  const handleLogout = () => {
    api.auth.logout()
    // 使用 replace 而不是 push，避免用户点击返回按钮
    router.replace('/')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">我的数字分身</h1>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">欢迎, {currentUser?.name || currentUser?.email}</span>
              <button
                onClick={handleLogout}
                className="flex items-center text-gray-600 hover:text-gray-900"
              >
                <LogOut className="w-5 h-5 mr-1" />
                退出
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 操作栏 */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">人格列表</h2>
            <p className="text-gray-600 mt-1">管理你的数字分身</p>
          </div>
          <button
            onClick={() => setShowUpload(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
          >
            <Plus className="w-5 h-5 mr-2" />
            导入聊天记录
          </button>
        </div>

        {/* 人格列表 */}
        {isLoading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, index) => (
              <PersonaCardSkeleton key={`skeleton-${index}`} />
            ))}
          </div>
        ) : personas.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <UploadIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">还没有数字分身</h3>
            <p className="text-gray-600 mb-6">上传聊天记录，创建你的第一个数字分身</p>
            <button
              onClick={() => setShowUpload(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
            >
              立即导入
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {personas.map((persona: any, index: number) => (
              <PersonaCard
                key={persona.id || `persona-${index}`}
                persona={persona}
                onDelete={handleDelete}
                index={index}
              />
            ))}
          </div>
        )}
      </div>

      {/* 上传弹窗 */}
      {showUpload && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold">导入聊天记录</h3>
              <button
                onClick={() => setShowUpload(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            <FileUpload onSuccess={handleUploadSuccess} />
          </div>
        </div>
      )}
    </div>
  )
}
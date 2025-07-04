/**
 * API服务封装
 */
import { mockApi } from './mockApi'

// 开发模式 - 使用真实API
const USE_MOCK_API = false

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function fetchAPI(
  endpoint: string,
  options: RequestInit = {}
): Promise<any> {
  const token = localStorage.getItem('token')
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Network error' }))
    throw new ApiError(response.status, error.detail || 'Request failed')
  }
  
  return response.json()
}

// 认证相关
export const authApi = {
  register: async (data: { email: string; username: string; password: string; name: string }) => {
    return fetchAPI('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },
  
  login: async (data: { username: string; password: string }) => {
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)
    
    const response = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    })
    
    if (!response.ok) {
      throw new ApiError(response.status, 'Login failed')
    }
    
    const result = await response.json()
    localStorage.setItem('token', result.access_token)
    // 同时设置cookie供middleware使用
    document.cookie = `auth-token=${result.access_token}; path=/; max-age=86400`
    return result
  },
  
  logout: () => {
    localStorage.removeItem('token')
    // 清除cookie
    document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
  },
  
  getCurrentUser: async () => {
    return fetchAPI('/auth/me')
  },
}

// 人格相关
export const personaApi = {
  list: async () => {
    return fetchAPI('/personas/')  // 添加尾部斜杠
  },
  
  get: async (id: string) => {
    return fetchAPI(`/personas/${id}`)
  },
  
  delete: async (id: string) => {
    return fetchAPI(`/personas/${id}`, {
      method: 'DELETE',
    })
  },
}

// 上传相关
export const uploadApi = {
  uploadFile: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const token = localStorage.getItem('token')
    const headers: HeadersInit = {}
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    const response = await fetch(`${API_BASE_URL}/upload/`, {  // 添加尾部斜杠
      method: 'POST',
      headers,
      body: formData,
    })
    
    if (!response.ok) {
      throw new ApiError(response.status, 'Upload failed')
    }
    
    return response.json()
  },
  
  getTaskStatus: async (taskId: string) => {
    return fetchAPI(`/upload/status/${taskId}`)
  },
}

// 对话相关
export const chatApi = {
  listChats: async () => {
    return fetchAPI('/chat/')  // 添加尾部斜杠
  },
  
  createChat: async (personaId: string, title?: string) => {
    return fetchAPI('/chat/', {  // 添加尾部斜杠
      method: 'POST',
      body: JSON.stringify({ persona_id: personaId, title }),
    })
  },
  
  getChat: async (chatId: string) => {
    return fetchAPI(`/chat/${chatId}`)
  },
  
  sendMessage: async (chatId: string, content: string) => {
    return fetchAPI(`/chat/${chatId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    })
  },
  
  regenerateMessage: async (chatId: string, messageIndex: number) => {
    return fetchAPI(`/chat/${chatId}/messages/${messageIndex}/regenerate`, {
      method: 'POST',
    })
  },
  
  deleteChat: async (chatId: string) => {
    return fetchAPI(`/chat/${chatId}`, {
      method: 'DELETE',
    })
  },
  
  exportChat: async (chatId: string) => {
    return fetchAPI(`/chat/${chatId}/export`)
  },
}

// 根据开发模式选择API
const api = USE_MOCK_API ? mockApi : {
  auth: authApi,
  persona: personaApi,  // 注意：这里应该是 persona 不是 personas
  upload: uploadApi,
  chat: chatApi,
}

export default api
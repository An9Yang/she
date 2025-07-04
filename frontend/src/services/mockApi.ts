// 模拟API服务 - 开发模式，绕过后端

const mockUser = {
  id: 'mock-user-001',
  email: 'y794847929@gmail.com',
  name: '测试用户',
  username: 'y794847929',
  is_active: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
}

const mockPersonas = [
  {
    id: 'persona-001',
    user_id: 'mock-user-001',
    name: '小雨',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=rain',
    description: '温柔体贴的朋友，总是能理解你的心情',
    traits: ['温柔', '体贴', '善解人意', '幽默'],
    speaking_style: '语气温和，喜欢用可爱的表情，经常鼓励别人',
    message_count: 142,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_chat_at: new Date().toISOString()
  },
  {
    id: 'persona-002',
    user_id: 'mock-user-001',
    name: '阳阳',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=sunny',
    description: '充满活力的同学，总能带来快乐',
    traits: ['活泼', '开朗', '积极', '爱开玩笑'],
    speaking_style: '语气活泼，喜欢用流行语，充满正能量',
    message_count: 89,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_chat_at: new Date().toISOString()
  },
  {
    id: 'persona-003',
    user_id: 'mock-user-001',
    name: '智慧导师',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=mentor',
    description: '博学多才的导师，能给出深刻的见解',
    traits: ['智慧', '耐心', '博学', '理性'],
    speaking_style: '语言严谨，善于引导思考，经常分享知识',
    message_count: 256,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_chat_at: new Date().toISOString()
  }
]

const mockChats = [
  {
    id: 'chat-001',
    user_id: 'mock-user-001',
    persona_id: 'persona-001',
    title: '今天的心情',
    last_message: '希望你今天过得愉快！记得要好好照顾自己哦~',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
]

const mockMessages = [
  {
    id: 'msg-001',
    chat_id: 'chat-001',
    role: 'user',
    content: '今天感觉有点累',
    created_at: new Date(Date.now() - 1000 * 60 * 5).toISOString()
  },
  {
    id: 'msg-002',
    chat_id: 'chat-001',
    role: 'assistant',
    content: '辛苦了呢~ 是工作太忙了吗？要不要休息一下，喝杯热茶放松一下？',
    created_at: new Date(Date.now() - 1000 * 60 * 4).toISOString()
  },
  {
    id: 'msg-003',
    chat_id: 'chat-001',
    role: 'user',
    content: '是啊，最近项目压力有点大',
    created_at: new Date(Date.now() - 1000 * 60 * 3).toISOString()
  },
  {
    id: 'msg-004',
    chat_id: 'chat-001',
    role: 'assistant',
    content: '项目压力大的时候，记得要适当调节哦。可以试试深呼吸，或者听听舒缓的音乐。晚上早点休息，明天又是充满活力的一天！加油，我相信你一定可以的！💪',
    created_at: new Date(Date.now() - 1000 * 60 * 2).toISOString()
  }
]

// 延迟函数，模拟网络请求
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export const mockApi = {
  auth: {
    login: async () => {
      await delay(500)
      return { access_token: 'mock-token', token_type: 'bearer' }
    },
    register: async () => {
      await delay(500)
      return mockUser
    },
    getCurrentUser: async () => {
      await delay(300)
      return mockUser
    }
  },

  personas: {
    list: async () => {
      await delay(500)
      return mockPersonas
    },
    get: async (id: string) => {
      await delay(300)
      return mockPersonas.find(p => p.id === id) || mockPersonas[0]
    },
    create: async (data: any) => {
      await delay(500)
      return {
        ...data,
        id: `persona-${Date.now()}`,
        user_id: 'mock-user-001',
        message_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        last_chat_at: new Date().toISOString()
      }
    },
    update: async (id: string, data: any) => {
      await delay(500)
      const persona = mockPersonas.find(p => p.id === id)
      return { ...persona, ...data, updated_at: new Date().toISOString() }
    },
    delete: async (id: string) => {
      await delay(500)
      return { success: true }
    }
  },

  chat: {
    list: async () => {
      await delay(500)
      return mockChats
    },
    create: async (personaId: string) => {
      await delay(500)
      return {
        id: `chat-${Date.now()}`,
        user_id: 'mock-user-001',
        persona_id: personaId,
        title: '新对话',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    },
    getMessages: async (chatId: string) => {
      await delay(500)
      return mockMessages
    },
    sendMessage: async (chatId: string, content: string) => {
      await delay(1000)
      const persona = mockPersonas[0]
      const responses = [
        `收到你的消息了！"${content.slice(0, 20)}..." 让我想想怎么回复...`,
        '这是个很有意思的话题呢！你能多说说吗？',
        '我理解你的感受。有时候生活确实会有些挑战，但我相信你能够克服的！',
        '哈哈，你说得对！我也是这么想的~',
        '嗯嗯，我在认真听着呢。还有什么想分享的吗？'
      ]
      return {
        id: `msg-${Date.now()}`,
        chat_id: chatId,
        role: 'assistant',
        content: responses[Math.floor(Math.random() * responses.length)],
        created_at: new Date().toISOString()
      }
    }
  },

  upload: {
    uploadFile: async (file: File) => {
      await delay(2000)
      return {
        task_id: `task-${Date.now()}`,
        status: 'processing',
        message: '文件上传成功，正在处理中...'
      }
    },
    checkStatus: async (taskId: string) => {
      await delay(1000)
      return {
        task_id: taskId,
        status: 'completed',
        result: {
          persona_id: 'persona-001',
          message: '处理完成！已成功创建人格。'
        }
      }
    }
  }
}
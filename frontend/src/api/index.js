import axios from 'axios'

const http = axios.create({
  baseURL: '',
  timeout: 90000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器：自动带 JWT
http.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截器：401 自动跳登录
http.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.hash = '#/login'
    }
    return Promise.reject(err)
  }
)

// API 函数
export const authAPI = {
  login: (data) => http.post('/api/auth/login', data),
  register: (data) => http.post('/api/auth/register', data),
  me: () => http.get('/api/auth/me'),
}

export const sessionAPI = {
  list: () => http.get('/api/sessions'),
  messages: (id) => http.get(`/api/sessions/${id}/messages`),
  delete: (id) => http.delete(`/api/sessions/${id}`),
}

export const chatAPI = {
  // SSE 流式，使用相对路径，Nginx 代理
  chatStream: (query, sessionId, token) => {
    const body = JSON.stringify({ query, session_id: sessionId || null })
    return fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body,
    })
  },
}

export default http
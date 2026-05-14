<template>
  <div class="chat-page">
    <!-- 顶部导航 -->
    <van-nav-bar title="智能客服助手" left-text="会话" @click-left="showDrawer = true" fixed>
      <template #right>
        <van-button size="small" plain @click="handleLogout">退出</van-button>
      </template>
    </van-nav-bar>

    <!-- 消息列表 -->
    <div class="msg-list" ref="msgList">
      <div v-if="messages.length === 0" class="empty-hint">  开始对话吧</div>
      <MessageBubble v-for="(msg, i) in messages" :key="i" :role="msg.role" :content="msg.content" />
      <div v-if="streaming" class="streaming-hint">正在输入...</div>
    </div>

    <!-- 底部输入栏 -->
    <div class="input-bar">
      <van-field v-model="inputText" placeholder="请输入问题" :disabled="streaming" @keyup.enter="sendMsg" />
      <van-button type="primary" :loading="streaming" @click="sendMsg">发送</van-button>
    </div>

    <!-- 会话抽屉 -->
    <van-popup v-model:show="showDrawer" position="left" :style="{ width: '75%', height: '100%' }">
      <div class="drawer">
        <h3>  历史会话</h3>
        <van-button block plain @click="newSession" style="margin-bottom:12px">+ 新对话</van-button>
        <van-swipe-cell v-for="s in sessions" :key="s.id">
          <van-cell :title="s.title || '新对话'" :label="s.updated_at?.slice(0,10)" @click="switchSession(s.id)" />
          <template #right>
            <van-button square type="danger" text="删除" @click="deleteSession(s.id)" />
          </template>
        </van-swipe-cell>
        <div v-if="sessions.length === 0" style="padding:20px;color:#999;text-align:center">暂无历史会话</div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { sessionAPI, chatAPI } from '../api/index.js'
import MessageBubble from '../components/MessageBubble.vue'

const router = useRouter()
const messages = ref([])
const inputText = ref('')
const streaming = ref(false)
const showDrawer = ref(false)
const sessions = ref([])
const currentSession = ref(null)
const msgList = ref(null)

const token = () => localStorage.getItem('token')

// 加载会话列表
const loadSessions = async () => {
  try {
    const { data } = await sessionAPI.list()
    sessions.value = data
  } catch { /* ignore */ }
}

// 加载会话消息
const loadMessages = async (sid) => {
  try {
    const { data } = await sessionAPI.messages(sid)
    messages.value = data
    scrollBottom()
  } catch { messages.value = [] }
}

// 切换会话
const switchSession = async (sid) => {
  currentSession.value = sid
  showDrawer.value = false
  await loadMessages(sid)
}

// 新建会话
const newSession = () => {
  currentSession.value = null
  messages.value = []
  showDrawer.value = false
}

// 删除会话
const deleteSession = async (sid) => {
  try {
    await sessionAPI.delete(sid)
    if (currentSession.value === sid) {
      currentSession.value = null
      messages.value = []
    }
    await loadSessions()
  } catch (e) {
    showToast('删除失败')
  }
}

// 发送消息
const sendMsg = async () => {
  const text = inputText.value.trim()
  if (!text || streaming.value) return

  inputText.value = ''
  messages.value.push({ role: 'user', content: text })
  messages.value.push({ role: 'assistant', content: '' })
  scrollBottom()

  streaming.value = true
  const idx = messages.value.length - 1

  try {
    const resp = await chatAPI.chatStream(text, currentSession.value, token())
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const chunk = line.slice(6)
          if (chunk === '[DONE]') continue
          messages.value[idx].content += chunk
          scrollBottom()
        }
      }
    }
  } catch (e) {
    messages.value[idx].content = '请求失败，请重试'
  } finally {
    streaming.value = false
    await loadSessions()
    if (!currentSession.value && sessions.value.length > 0) {
      currentSession.value = sessions.value[0].id
    }
  }
}

// 退出
const handleLogout = () => {
  localStorage.clear()
  router.push('/login')
}

// 滚动到底部
const scrollBottom = async () => {
  await nextTick()
  const el = msgList.value
  if (el) el.scrollTop = el.scrollHeight
}

onMounted(() => {
  loadSessions()
})
</script>

<style scoped>
.chat-page { height: 100vh; display: flex; flex-direction: column; background: #f7f8fa; }
.msg-list { flex: 1; overflow-y: auto; padding: 60px 12px 12px; }
.empty-hint { text-align: center; color: #999; margin-top: 40vh; font-size: 16px; }
.streaming-hint { text-align: center; color: #1989fa; font-size: 13px; padding: 8px; }
.input-bar { display: flex; align-items: center; padding: 8px 12px; background: #fff; border-top: 1px solid #ebedf0; }
.input-bar .van-field { flex: 1; background: #f7f8fa; border-radius: 20px; padding: 4px 12px; margin-right: 8px; }
.drawer { padding: 16px; }
.drawer h3 { margin-bottom: 12px; font-size: 16px; }
</style>
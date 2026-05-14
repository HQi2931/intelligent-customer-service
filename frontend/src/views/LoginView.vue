<template>
  <div class="login-page">
    <div class="logo">   </div>
    <h1>智能客服助手</h1>
    <p>基于 AI 的扫地机器人知识助手</p>

    <van-tabs v-model:active="activeTab" color="#1989fa">
      <van-tab title="登录">
        <van-form @submit="handleLogin">
          <van-field v-model="loginForm.username" label="用户名" placeholder="请输入用户名" :rules="[{ required: true }]" />
          <van-field v-model="loginForm.password" label="密码" type="password" placeholder="请输入密码" :rules="[{ required: true }]" />
          <van-button block type="primary" native-type="submit" :loading="loading">登录</van-button>
        </van-form>
      </van-tab>
      <van-tab title="注册">
        <van-form @submit="handleRegister">
          <van-field v-model="regForm.username" label="用户名" placeholder="至少3个字符" :rules="[{ required: true, min: 3 }]" />
          <van-field v-model="regForm.password" label="密码" type="password" placeholder="至少6个字符" :rules="[{ required: true, min: 6 }]" />
          <van-field v-model="regForm.email" label="邮箱" placeholder="选填" />
          <van-button block type="primary" native-type="submit" :loading="loading">注册</van-button>
        </van-form>
      </van-tab>
    </van-tabs>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { authAPI } from '../api/index.js'

const router = useRouter()
const activeTab = ref(0)
const loading = ref(false)

const loginForm = reactive({ username: '', password: '' })
const regForm = reactive({ username: '', password: '', email: '' })

const handleLogin = async () => {
  loading.value = true
  try {
    const { data } = await authAPI.login(loginForm)
    localStorage.setItem('token', data.token)
    localStorage.setItem('username', data.username)
    localStorage.setItem('user_id', data.user_id)
    router.push('/chat')
  } catch (e) {
    showToast(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  loading.value = true
  try {
    const { data } = await authAPI.register(regForm)
    localStorage.setItem('token', data.token)
    localStorage.setItem('username', data.username)
    localStorage.setItem('user_id', data.user_id)
    router.push('/chat')
  } catch (e) {
    showToast(e.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page { max-width: 400px; margin: 0 auto; padding: 40px 20px; text-align: center; }
.logo { font-size: 56px; margin-bottom: 8px; }
h1 { font-size: 22px; color: #323233; margin-bottom: 4px; }
p { color: #969799; font-size: 14px; margin-bottom: 24px; }
.van-form { margin-top: 16px; text-align: left; }
.van-button { margin-top: 16px; }
</style>
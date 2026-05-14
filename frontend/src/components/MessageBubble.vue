<template>
  <div :class="['bubble', role]">
    <div class="avatar">{{ role === 'user' ? '  ' : '  ' }}</div>
    <div class="content">{{ content }}</div>
  </div>
</template>

<script setup>
defineProps({
  role: { type: String, required: true },
  content: { type: String, default: '' },
})
</script>

<style scoped>
.bubble { display: flex; margin-bottom: 12px; gap: 8px; }
.bubble.user { flex-direction: row-reverse; }
.avatar { width: 36px; height: 36px; border-radius: 50%; background: #1989fa; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.bubble.assistant .avatar { background: #07c160; }
.content { max-width: 75%; padding: 10px 14px; border-radius: 12px; font-size: 15px; line-height: 1.6; white-space: pre-wrap; word-break: break-word; }
.bubble.user .content { background: #1989fa; color: #fff; border-bottom-right-radius: 4px; }
.bubble.assistant .content { background: #fff; color: #323233; border-bottom-left-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.06); }
</style>
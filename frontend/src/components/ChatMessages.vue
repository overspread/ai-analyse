<template>
  <div>
    <div v-for="(msg, idx) in messages" :key="idx" :style="msg.role === 'user' ? userStyle : assistantStyle">
      <div :style="msg.role === 'user' ? userBubbleStyle : assistantBubbleStyle">
        <div style="white-space: pre-wrap;">{{ msg.content }}</div>
        <SourceReference v-if="msg.sources && msg.sources.length > 0" :sources="msg.sources" />
      </div>
    </div>
    <div v-if="!messages.length" style="text-align: center; padding: 80px 0; color: #999;">
      <n-icon size="48"><chatbubbles-outline /></n-icon>
      <n-p>选择左侧文档，输入问题开始对话</n-p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ChatbubblesOutline } from '@vicons/ionicons5'
import SourceReference from './SourceReference.vue'
import type { SourceChunk } from '../api'

defineProps<{
  messages: { role: string; content: string; sources?: SourceChunk[] }[]
}>()

const userStyle = { display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }
const assistantStyle = { display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }
const userBubbleStyle = {
  maxWidth: '70%',
  padding: '10px 16px',
  borderRadius: '18px 18px 4px 18px',
  background: '#18a058',
  color: '#fff',
  fontSize: '14px',
  lineHeight: '1.6',
}
const assistantBubbleStyle = {
  maxWidth: '70%',
  padding: '10px 16px',
  borderRadius: '18px 18px 18px 4px',
  background: 'var(--n-color)',
  color: 'var(--n-text-color)',
  border: '1px solid var(--border-color)',
  fontSize: '14px',
  lineHeight: '1.6',
}
</script>

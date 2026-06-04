<template>
  <div class="chat-panel">
    <div class="chat-header">
      <span class="header-title">AI 对话</span>
      <span class="header-badge">在线</span>
    </div>

    <div class="messages-area" ref="messagesRef">
      <div v-if="!messages.length" class="empty-state">
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
          <circle cx="20" cy="20" r="18" stroke="rgba(0,212,255,0.2)" stroke-width="1.5" stroke-dasharray="4 3"/>
          <path d="M20 12V28M12 20H28" stroke="rgba(0,212,255,0.3)" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <p class="empty-text">选择文档后输入问题，AI 将基于文档内容回答</p>
      </div>

      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        class="message-row"
        :class="msg.role"
      >
        <div class="avatar">
          <svg v-if="msg.role === 'assistant'" width="28" height="28" viewBox="0 0 28 28" fill="none">
            <circle cx="14" cy="14" r="12" stroke="#00d4ff" stroke-width="1" fill="rgba(0,212,255,0.05)"/>
            <path d="M14 8C14 8 17 11 17 14C17 17 14 20 14 20" stroke="#00d4ff" stroke-width="1.2" stroke-linecap="round"/>
            <path d="M14 8C14 8 11 11 11 14C11 17 14 20 14 20" stroke="#7b2ff7" stroke-width="1.2" stroke-linecap="round"/>
            <circle cx="14" cy="14" r="2" fill="rgba(0,212,255,0.3)"/>
          </svg>
          <svg v-else width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect x="4" y="4" width="20" height="20" rx="6" stroke="#7b2ff7" stroke-width="1" fill="rgba(123,47,247,0.05)"/>
            <circle cx="14" cy="12" r="3" stroke="#7b2ff7" stroke-width="1" fill="rgba(123,47,247,0.1)"/>
            <path d="M8 22C8 18.5 10.5 16 14 16C17.5 16 20 18.5 20 22" stroke="#7b2ff7" stroke-width="1" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="bubble">
          <div class="bubble-text">{{ msg.content }}</div>
          <div v-if="msg.sources && msg.sources.length" class="sources-bar">
            <span class="sources-label">来源</span>
            <span
              v-for="(src, si) in msg.sources"
              :key="si"
              :ref="el => setSourceRef(idx, si, el)"
              class="source-tag"
              :class="{ active: hoveredSourceIdx === idx && hoveredSourceSub === si }"
              @mouseenter="onSourceEnter($event, idx, si, src.page_number)"
              @mouseleave="onSourceLeave"
            >
              {{ src.document_name }}
              <span v-if="src.page_number" class="page-ref">[引用页码 {{ src.page_number }}]</span>
            </span>
          </div>
        </div>
      </div>

      <div v-if="sending" class="message-row assistant">
        <div class="avatar">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <circle cx="14" cy="14" r="12" stroke="#00d4ff" stroke-width="1" fill="rgba(0,212,255,0.05)"/>
            <circle cx="14" cy="14" r="2" fill="rgba(0,212,255,0.3)"/>
          </svg>
        </div>
        <div class="bubble typing-bubble">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
      </div>
    </div>

    <div class="input-area">
      <div class="input-glow"></div>
      <div class="input-row">
        <input
          v-model="question"
          class="chat-input"
          placeholder="输入你的问题..."
          :disabled="sending || !docId"
          @keydown.enter.prevent="send"
        />
        <button
          class="send-btn"
          :disabled="!question.trim() || sending || !docId"
          @click="send"
        >
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path d="M2 9L16 2L9 16L7 11L2 9Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import type { SourceChunk } from '../api'

interface MessageItem {
  role: 'user' | 'assistant'
  content: string
  sources?: SourceChunk[]
}

const props = defineProps<{
  messages: MessageItem[]
  sending: boolean
  docId: number | null
  hoveredSourceIdx: number | null
  hoveredSourceSub: number | null
}>()

const emit = defineEmits<{
  (e: 'send', question: string): void
  (e: 'source-hover', payload: {
    messageIdx: number
    sourceIdx: number
    page: number | null | undefined
    sourceRect: { left: number; top: number; right: number; bottom: number; width: number; height: number } | null
  }): void
  (e: 'source-leave'): void
}>()

const question = ref('')
const messagesRef = ref<HTMLElement>()
const sourceRefs = ref<Map<string, HTMLElement>>(new Map())

function setSourceRef(msgIdx: number, srcIdx: number, el: any) {
  if (el) {
    sourceRefs.value.set(`${msgIdx}-${srcIdx}`, el as HTMLElement)
  }
}

function onSourceEnter(e: MouseEvent, msgIdx: number, srcIdx: number, page: number | null | undefined) {
  const key = `${msgIdx}-${srcIdx}`
  const el = sourceRefs.value.get(key)
  const rect = el?.getBoundingClientRect()
  emit('source-hover', {
    messageIdx: msgIdx,
    sourceIdx: srcIdx,
    page,
    sourceRect: rect ? {
      left: rect.left,
      top: rect.top,
      right: rect.right,
      bottom: rect.bottom,
      width: rect.width,
      height: rect.height,
    } : null,
  })
}

function onSourceLeave() {
  emit('source-leave')
}

function send() {
  const q = question.value.trim()
  if (!q || props.sending || !props.docId) return
  emit('send', q)
  question.value = ''
}

watch(() => props.messages.length, () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
})
</script>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.header-title {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  letter-spacing: 2px;
}

.header-badge {
  font-size: 10px;
  color: #00ff88;
  padding: 2px 8px;
  border-radius: 8px;
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.2);
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.messages-area::-webkit-scrollbar {
  width: 4px;
}
.messages-area::-webkit-scrollbar-track {
  background: transparent;
}
.messages-area::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 12px;
}

.empty-text {
  color: rgba(255, 255, 255, 0.25);
  font-size: 13px;
  letter-spacing: 0.5px;
}

.message-row {
  display: flex;
  gap: 10px;
  animation: msgIn 0.3s ease;
}

@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-row.user {
  flex-direction: row-reverse;
}

.avatar {
  flex-shrink: 0;
  margin-top: 4px;
}

.bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.85);
}

.message-row.assistant .bubble {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-bottom-left-radius: 4px;
}

.message-row.user .bubble {
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.15);
  border-bottom-right-radius: 4px;
  color: rgba(255, 255, 255, 0.9);
}

.bubble-text {
  white-space: pre-wrap;
  word-break: break-word;
}

.sources-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.sources-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.25);
  letter-spacing: 1px;
  padding: 2px 0;
}

.source-tag {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 8px;
  background: rgba(0, 212, 255, 0.06);
  border: 1px solid rgba(0, 212, 255, 0.15);
  color: rgba(0, 212, 255, 0.6);
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.source-tag:hover {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.4);
  color: #00d4ff;
}
.source-tag.active {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  color: #00d4ff;
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.2);
}

.page-ref {
  font-size: 10px;
  color: rgba(123, 47, 247, 0.7);
  animation: glowPulse 2s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; text-shadow: 0 0 8px rgba(123, 47, 247, 0.4); }
}

.typing-bubble {
  display: flex;
  gap: 4px;
  padding: 14px 18px;
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(0, 212, 255, 0.4);
  animation: typingBounce 1.4s ease-in-out infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); background: rgba(0, 212, 255, 0.8); }
}

.input-area {
  position: relative;
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.input-glow {
  position: absolute;
  top: -1px;
  left: 20%;
  right: 20%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.3), transparent);
  animation: breatheLight 3s ease-in-out infinite;
}

@keyframes breatheLight {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.8; }
}

.input-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chat-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 10px 14px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  outline: none;
  transition: all 0.3s;
}
.chat-input:focus {
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 0 16px rgba(0, 212, 255, 0.08);
}
.chat-input::placeholder {
  color: rgba(255, 255, 255, 0.2);
}
.chat-input:disabled {
  opacity: 0.4;
}

.send-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid rgba(0, 212, 255, 0.2);
  background: rgba(0, 212, 255, 0.08);
  color: rgba(0, 212, 255, 0.6);
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.send-btn:hover:not(:disabled) {
  background: rgba(0, 212, 255, 0.2);
  border-color: rgba(0, 212, 255, 0.4);
  color: #00d4ff;
  box-shadow: 0 0 16px rgba(0, 212, 255, 0.15);
}
.send-btn:disabled {
  opacity: 0.25;
  cursor: default;
}
</style>

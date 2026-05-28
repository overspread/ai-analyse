<template>
  <div style="display: flex; height: 100%;">
    <n-layout-sider
      bordered
      width="280"
      style="overflow: auto;"
      content-style="padding: 16px;"
    >
      <n-h4>选择文档</n-h4>
      <n-checkbox-group v-model:value="store.selectedDocIds">
        <n-space vertical>
          <div v-for="doc in store.documents" :key="doc.id" style="padding: 4px 0;">
            <n-checkbox :value="doc.id" :label="doc.original_filename" />
          </div>
        </n-space>
      </n-checkbox-group>
      <n-empty v-if="store.documents.length === 0" description="暂无文档，请先上传" style="margin-top: 24px;" />
      <n-button
        v-if="store.documents.length > 0"
        size="small"
        quaternary
        style="margin-top: 12px;"
        @click="store.fetchDocuments()"
        :loading="store.loading"
      >
        刷新文档列表
      </n-button>
    </n-layout-sider>

    <n-layout-content style="display: flex; flex-direction: column;">
      <div style="flex: 1; overflow-y: auto; padding: 16px;">
        <div style="max-width: 800px; margin: 0 auto;">
          <ChatMessages ref="chatRef" :messages="messages" />
        </div>
      </div>

      <div style="border-top: 1px solid var(--border-color); padding: 16px 24px;">
        <div style="max-width: 800px; margin: 0 auto; display: flex; gap: 12px;">
          <n-input
            v-model:value="question"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 4 }"
            placeholder="输入你的问题..."
            :disabled="sending"
            @keydown.enter.prevent="sendMessage"
          />
          <n-button
            type="primary"
            :loading="sending"
            :disabled="!question.trim() || store.selectedDocIds.length === 0"
            @click="sendMessage"
            style="align-self: flex-end;"
          >
            发送
          </n-button>
        </div>
      </div>
    </n-layout-content>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { api } from '../api'
import { useAppStore } from '../stores/app'
import ChatMessages from '../components/ChatMessages.vue'
import type { SourceChunk } from '../api'

const store = useAppStore()
const message = useMessage()

interface MessageItem {
  role: 'user' | 'assistant'
  content: string
  sources?: SourceChunk[]
}

const question = ref('')
const sending = ref(false)
const messages = ref<MessageItem[]>([])

onMounted(async () => {
  try {
    await store.fetchDocuments()
  } catch (e: any) {
    console.error('Failed to load documents on mount:', e)
    // Error is already handled in store
  }
})

async function sendMessage() {
  const q = question.value.trim()
  if (!q) {
    message.warning('请输入问题')
    return
  }
  if (store.selectedDocIds.length === 0) {
    message.warning('请先选择要查询的文档')
    return
  }

  messages.value.push({ role: 'user', content: q })
  question.value = ''
  sending.value = true

  try {
    const res = await api.chat(q, store.selectedDocIds)
    messages.value.push({ role: 'assistant', content: res.answer, sources: res.sources })
  } catch (e: any) {
    const errorMsg = e?.message || e?.response?.data?.detail || '请求失败，请稍后重试'
    message.error(errorMsg)
    messages.value.push({ role: 'assistant', content: `抱歉，${errorMsg}` })
  } finally {
    sending.value = false
  }
}
</script>

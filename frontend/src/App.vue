<template>
  <n-message-provider>
    <n-notification-provider>
      <n-dialog-provider>
        <n-config-provider :theme="isDark ? darkTheme : null" :locale="zhCN" :date-locale="dateZhCN">
          <n-layout position="absolute" :has-sider="true">
            <n-layout-header bordered style="height: 56px; display: flex; align-items: center; padding: 0 24px;">
              <n-h3 style="margin: 0; flex: 1;">AI 透析助手</n-h3>
              <n-space>
                <n-button :type="route.path === '/documents' ? 'primary' : 'default'" @click="$router.push('/documents')">
                  文档管理
                </n-button>
                <n-button :type="route.path === '/chat' ? 'primary' : 'default'" @click="$router.push('/chat')">
                  问答对话
                </n-button>
                <n-button quaternary circle @click="isDark = !isDark">
                  <template #icon>
                    <n-icon><div v-if="isDark">☀️</div><div v-else>🌙</div></n-icon>
                  </template>
                </n-button>
              </n-space>
            </n-layout-header>
            <n-layout-content position="absolute" style="top: 56px; bottom: 0;">
              <router-view />
            </n-layout-content>
          </n-layout>
        </n-config-provider>
      </n-dialog-provider>
    </n-notification-provider>
  </n-message-provider>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { darkTheme, zhCN, dateZhCN } from 'naive-ui'
import { useAppStore } from './stores/app'

const route = useRoute()
const isDark = ref(false)
const store = useAppStore()

onMounted(() => {
  store.fetchDocuments()
})
</script>

<style>
body { margin: 0; }
#app { height: 100vh; }
</style>

<template>
  <n-message-provider>
    <n-notification-provider>
      <n-dialog-provider>
        <n-config-provider :theme="isDark ? darkTheme : null" :locale="zhCN" :date-locale="dateZhCN">
          <n-layout position="absolute" :has-sider="true">
            <n-layout-header bordered style="height: 56px; display: flex; align-items: center; padding: 0 24px;">
              <n-space style="flex: 1;">
              </n-space>
              <n-space>
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
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { darkTheme, zhCN, dateZhCN } from 'naive-ui'
import { useAppStore } from './stores/app'
import { ref } from 'vue'

const store = useAppStore()
const route = useRoute()
const isDark = ref(false)

onMounted(() => {
  store.fetchDocuments()
})
</script>

<style>
body {
  margin: 0;
  background: #0a0e1a;
}
#app {
  height: 100vh;
  background: #0a0e1a;
}
/* Override global Naive UI defaults for dark theme */
:root {
  --n-color: #0a0e1a;
  --n-text-color: rgba(255, 255, 255, 0.8);
  --border-color: rgba(255, 255, 255, 0.06);
}
.n-layout {
  --n-color: #0a0e1a !important;
}
.n-layout-sider,
.n-layout-header,
.n-layout-content {
  --n-color: #0a0e1a !important;
}
</style>

<template>
  <n-message-provider>
    <n-notification-provider>
      <n-dialog-provider>
        <n-config-provider :theme="darkTheme" :locale="zhCN" :date-locale="dateZhCN">
          <n-layout position="absolute" style="background: #0a0e1a;">
            <n-layout-content position="absolute" style="top: 0; bottom: 0; background: #0a0e1a;">
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
import { darkTheme, zhCN, dateZhCN } from 'naive-ui'
import { useAppStore } from './stores/app'

const store = useAppStore()

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

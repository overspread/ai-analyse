<template>
  <n-collapse style="margin-top: 12px;">
    <n-collapse-item title="查看引用来源" name="sources">
      <div v-for="(source, idx) in sources" :key="idx" style="margin-bottom: 8px; padding: 8px; border-left: 3px solid #18a058; background: var(--n-color); border-radius: 4px;">
        <n-text depth="3" style="font-size: 12px;">
          来源 {{ idx + 1 }}:
          <n-tag size="tiny" bordered>{{ source.document_name }}</n-tag>
          <n-tag size="tiny" type="warning" bordered>匹配度: {{ (source.score * 100).toFixed(1) }}%</n-tag>
        </n-text>
        <n-ellipsis :line-clamp="3" :tooltip="{ width: 600 }" style="margin-top: 4px; font-size: 13px;">
          {{ source.content }}
        </n-ellipsis>
      </div>
    </n-collapse-item>
  </n-collapse>
</template>

<script setup lang="ts">
import type { SourceChunk } from '../api'

defineProps<{
  sources: SourceChunk[]
}>()
</script>

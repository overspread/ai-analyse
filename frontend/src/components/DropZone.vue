<template>
  <div
    class="dropzone-wrapper"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
    @click="openFileDialog"
    :class="{ 'is-dragging': isDragging }"
  >
    <div class="title-bar">OmniMind Doc // 智能文档解析舱</div>
    <div class="glass-card" :class="{ 'drag-active': isDragging }">
      <div class="icon-area">
        <svg width="72" height="72" viewBox="0 0 72 72" fill="none">
          <path d="M16 8H42L56 22V60C56 62.2 54.2 64 52 64H16C13.8 64 12 62.2 12 60V12C12 9.8 13.8 8 16 8Z" stroke="url(#grad1)" stroke-width="2" stroke-dasharray="4 3" fill="rgba(0,212,255,0.05)"/>
          <path d="M34 28V44M26 36H42" stroke="url(#grad1)" stroke-width="2" stroke-linecap="round"/>
          <rect x="16" y="46" width="16" height="2" rx="1" fill="rgba(0,212,255,0.3)"/>
          <rect x="16" y="50" width="24" height="2" rx="1" fill="rgba(0,212,255,0.2)"/>
          <rect x="16" y="54" width="20" height="2" rx="1" fill="rgba(0,212,255,0.15)"/>
          <defs>
            <linearGradient id="grad1" x1="0" y1="0" x2="72" y2="72">
              <stop offset="0%" stop-color="#00d4ff"/>
              <stop offset="100%" stop-color="#7b2ff7"/>
            </linearGradient>
          </defs>
        </svg>
      </div>
      <p class="hint-primary">将您的文档拖拽至此，或点击浏览</p>
      <p class="hint-secondary">支持 PDF、DOCX &middot; 单文件最大 50MB</p>
    </div>
    <input
      type="file"
      ref="fileInput"
      accept=".pdf,.docx"
      multiple
      hidden
      @change="onFileSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  (e: 'files-selected', files: File[]): void
}>()

const isDragging = ref(false)
const fileInput = ref<HTMLInputElement>()

function onDragOver() {
  isDragging.value = true
}

function onDragLeave() {
  isDragging.value = false
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    emit('files-selected', Array.from(files))
  }
}

function openFileDialog() {
  fileInput.value?.click()
}

function onFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    emit('files-selected', Array.from(target.files))
    target.value = ''
  }
}
</script>

<style scoped>
.dropzone-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  cursor: pointer;
  transition: background 0.3s;
}
.dropzone-wrapper.is-dragging {
  background: rgba(0, 212, 255, 0.03);
}

.title-bar {
  position: absolute;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 20px;
  font-weight: 300;
  letter-spacing: 6px;
  color: rgba(255, 255, 255, 0.6);
  text-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
  white-space: nowrap;
}
.title-bar::before,
.title-bar::after {
  content: '';
  display: inline-block;
  width: 40px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.4), transparent);
  vertical-align: middle;
  margin: 0 16px;
}

.glass-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 48px 64px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow:
    0 0 40px rgba(0, 212, 255, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: all 0.4s ease;
  position: relative;
}
.glass-card::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 24px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), transparent 40%, transparent 60%, rgba(123, 47, 247, 0.3));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  opacity: 0.6;
  transition: opacity 0.4s;
}
.glass-card.drag-active {
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow:
    0 0 60px rgba(0, 212, 255, 0.1),
    inset 0 1px 0 rgba(0, 212, 255, 0.1);
  transform: scale(1.02);
}
.glass-card.drag-active::before {
  opacity: 1;
}

.icon-area {
  position: relative;
  padding: 8px;
  border-radius: 16px;
  background: rgba(0, 212, 255, 0.03);
}

.hint-primary {
  color: rgba(255, 255, 255, 0.7);
  font-size: 16px;
  letter-spacing: 1px;
  margin: 0;
}

.hint-secondary {
  color: rgba(255, 255, 255, 0.3);
  font-size: 13px;
  letter-spacing: 0.5px;
  margin: 0;
}
</style>

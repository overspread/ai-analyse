<template>
  <div class="pdf-preview" ref="containerRef">
    <div class="pdf-toolbar">
      <span class="doc-title">{{ docName }}</span>
      <span v-if="totalPages" class="page-indicator">
        <button class="page-btn" @click="prevPage" :disabled="currentPage <= 1">‹</button>
        <span class="page-num">{{ currentPage }} / {{ totalPages }}</span>
        <button class="page-btn" @click="nextPage" :disabled="currentPage >= totalPages">›</button>
      </span>
    </div>
    <div class="pdf-viewport" ref="viewportRef" @scroll="onScroll">
      <div v-if="!isPdf" class="unsupported-notice">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
          <path d="M8 6H30L40 16V40C40 41.1 39.1 42 38 42H8C6.9 42 6 41.1 6 40V8C6 6.9 6.9 6 8 6Z" stroke="#7b2ff7" stroke-width="1.5" fill="rgba(123,47,247,0.05)"/>
          <path d="M16 22H32M16 28H28M16 34H24" stroke="#7b2ff7" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="3 3"/>
        </svg>
        <p>该文档格式暂不支持预览</p>
        <p class="sub">DOCX 文件已上传，可进行 AI 问答</p>
      </div>
      <div v-else class="pdf-render">
        <div
          v-for="p in totalPages"
          :key="p"
          :ref="el => setPageRef(p, el)"
          class="pdf-page-wrapper"
          :class="{ 'page-highlight': highlightPage === p }"
          :data-page="p"
        >
          <vue-pdf-embed
            :source="pdfUrl"
            :page="p"
            :style="{ width: '100%' }"
          />
        </div>
      </div>
    </div>
    <Transition name="fade">
      <div v-if="highlightPage" class="page-overlay" :style="overlayStyle">
        <div class="overlay-beam"></div>
        <div class="overlay-label">第 {{ highlightPage }} 页 引用</div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'

const props = defineProps<{
  docId: number | null
  docName: string
  docType: string
  highlightPage: number | null
}>()

const emit = defineEmits<{
  (e: 'page-visible', page: number): void
}>()

const isPdf = computed(() => props.docType === 'pdf')
const pdfUrl = computed(() => props.docId ? `/api/documents/${props.docId}/file` : '')

const containerRef = ref<HTMLElement>()
const viewportRef = ref<HTMLElement>()
const pageRefs = ref<Map<number, HTMLElement>>(new Map())

const totalPages = ref(0)
const currentPage = ref(1)

function getViewportRect() {
  return viewportRef.value?.getBoundingClientRect() || null
}

function getPagePosition(pageNum: number) {
  if (!viewportRef.value || !totalPages.value) return null
  const vpRect = viewportRef.value.getBoundingClientRect()
  const scrollRatio = (pageNum - 1) / totalPages.value
  const scrollHeight = viewportRef.value.scrollHeight - viewportRef.value.clientHeight
  return {
    top: vpRect.top + scrollRatio * scrollHeight - viewportRef.value.scrollTop,
    bottom: vpRect.top + scrollRatio * scrollHeight + vpRect.height / totalPages.value - viewportRef.value.scrollTop,
  }
}



function setPageRef(p: number, el: any) {
  if (el) pageRefs.value.set(p, el as HTMLElement)
}

function onScroll() {
  const vp = viewportRef.value
  if (!vp) return
  const pages = Array.from(pageRefs.value.entries())
  let bestPage = 1
  let bestDist = Infinity
  for (const [num, el] of pages) {
    const rect = el.getBoundingClientRect()
    const vpRect = vp.getBoundingClientRect()
    const dist = Math.abs(rect.top - vpRect.top)
    if (dist < bestDist) {
      bestDist = dist
      bestPage = num
    }
  }
  currentPage.value = bestPage
}

function prevPage() {
  if (currentPage.value > 1) scrollToPage(currentPage.value - 1)
}

function nextPage() {
  if (currentPage.value < totalPages.value) scrollToPage(currentPage.value + 1)
}

function scrollToPage(p: number) {
  const el = pageRefs.value.get(p)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    currentPage.value = p
  }
}

watch(() => props.highlightPage, (page) => {
  if (page && page >= 1 && page <= totalPages.value) {
    nextTick(() => scrollToPage(page))
  }
})

watch(() => props.docId, () => {
  totalPages.value = 0
  currentPage.value = 1
  pageRefs.value.clear()
})

function onPdfRendered(pages: number) {
  totalPages.value = pages
}

const overlayStyle = computed(() => ({
  top: `${((props.highlightPage || 1) - 1) / (totalPages.value || 1) * 100}%`,
}))

defineExpose({ viewportRef, getViewportRect, getPagePosition, onPdfRendered, scrollToPage, totalPages })
</script>

<style scoped>
.pdf-preview {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  background: rgba(255, 255, 255, 0.01);
}

.pdf-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.doc-title {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  letter-spacing: 1px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.page-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  border-radius: 4px;
  padding: 2px 10px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}
.page-btn:hover:not(:disabled) {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.3);
  color: #00d4ff;
}
.page-btn:disabled {
  opacity: 0.3;
  cursor: default;
}

.page-num {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  min-width: 48px;
  text-align: center;
}

.pdf-viewport {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  scroll-behavior: smooth;
}

.pdf-viewport::-webkit-scrollbar {
  width: 4px;
}
.pdf-viewport::-webkit-scrollbar-track {
  background: transparent;
}
.pdf-viewport::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.pdf-render {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  max-width: 100%;
}

.pdf-page-wrapper {
  width: 100%;
  max-width: 600px;
  border-radius: 4px;
  overflow: hidden;
  transition: box-shadow 0.3s;
  position: relative;
}
.pdf-page-wrapper.page-highlight {
  box-shadow:
    0 0 20px rgba(0, 212, 255, 0.3),
    0 0 60px rgba(0, 212, 255, 0.15),
    0 0 100px rgba(123, 47, 247, 0.08);
}
.pdf-page-wrapper.page-highlight::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(0, 212, 255, 0.08) 0%,
    transparent 30%,
    transparent 70%,
    rgba(123, 47, 247, 0.08) 100%
  );
  pointer-events: none;
  animation: energyShield 2s ease-in-out infinite;
}

@keyframes energyShield {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Page left-edge indicator for highlighted page */
.pdf-page-wrapper.page-highlight::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #00d4ff, #7b2ff7);
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.5);
  z-index: 2;
  animation: indicatorGlow 1.5s ease-in-out infinite;
}

@keyframes indicatorGlow {
  0%, 100% { box-shadow: 0 0 8px rgba(0, 212, 255, 0.3); }
  50% { box-shadow: 0 0 20px rgba(0, 212, 255, 0.7), 0 0 40px rgba(123, 47, 247, 0.3); }
}

.unsupported-notice {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 12px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 14px;
}
.unsupported-notice .sub {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.25);
}

.page-overlay {
  position: absolute;
  left: 0;
  right: 0;
  height: 40px;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: top 0.4s ease;
}

.overlay-beam {
  position: absolute;
  left: 0;
  top: 50%;
  width: 40px;
  height: 1px;
  background: linear-gradient(90deg, rgba(0, 212, 255, 0.6), transparent);
}

.overlay-label {
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.2);
  color: rgba(0, 212, 255, 0.7);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  letter-spacing: 1px;
  backdrop-filter: blur(8px);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>

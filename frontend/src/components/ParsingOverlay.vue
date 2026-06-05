<template>
  <div class="parsing-wrapper">
    <div class="upload-card">
      <div class="file-header">
        <div class="file-icon" :class="phase">
          <svg v-if="phase === 'uploading'" width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path d="M12 16V4M12 4L6 10M12 4L18 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4 16V19C4 20.1 4.9 21 6 21H18C19.1 21 20 20.1 20 19V16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <div class="file-meta">
          <div class="file-name" :title="fileName">{{ fileName }}</div>
          <div class="file-size-row">
            <span class="file-size">{{ phase === 'uploading' ? uploaded : fileSize }}</span>
          </div>
        </div>
      </div>

      <div v-if="phase === 'uploading'" class="phase-section">
        <div class="step-header">
          <div class="step-badge active">1</div>
          <span class="step-label">上传文件</span>
          <span class="step-percent">{{ uploadPercent }}%</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill upload-color" :style="{ width: uploadPercent + '%' }">
            <div class="progress-shimmer"></div>
          </div>
        </div>
        <div class="stage-row">
          <div class="stage-indicator">
            <span class="stage-dot uploading"></span>
            <span class="stage-text">{{ stage }}</span>
          </div>
          <div v-if="speed" class="speed-text">{{ speed }} · 剩余 {{ eta }}</div>
        </div>
      </div>

      <div v-if="phase === 'parsing'" class="phase-section">
        <div class="step-header">
          <div class="step-badge done">1</div>
          <span class="step-label done-label">上传文件</span>
          <span class="step-check">✓</span>
        </div>
        <div class="step-header">
          <div class="step-badge active">2</div>
          <span class="step-label">AI 处理</span>
          <span class="step-percent">{{ processingPercent }}%</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill parse-color" :style="{ width: processingPercent + '%' }">
            <div class="progress-shimmer"></div>
          </div>
        </div>
        <div class="stage-row">
          <div class="stage-indicator">
            <span class="stage-dot parsing"></span>
            <span class="stage-text">{{ stage }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue'

const props = defineProps<{
  fileName: string
  fileSize: string
  uploaded: string
  progress: number
  stage?: string
  phase: 'uploading' | 'parsing'
}>()

const uploadPercent = computed(() => props.phase !== 'uploading' ? 100 : Math.min(100, props.progress))
const processingPercent = computed(() => props.phase !== 'parsing' ? 0 : Math.min(100, props.progress))

let lastLoaded = 0
let lastTime = Date.now()
const speedMbps = ref(0)
let speedTimer: ReturnType<typeof setInterval> | null = null

function parseSize(s: string): number {
  const m = s.match(/^([\d.]+)\s*(B|KB|MB|GB)$/i)
  if (!m) return 0
  const v = parseFloat(m[1]); const u = m[2].toUpperCase()
  if (u === 'B') return v
  if (u === 'KB') return v * 1024
  if (u === 'MB') return v * 1024 * 1024
  if (u === 'GB') return v * 1024 * 1024 * 1024
  return 0
}

watch(() => props.uploaded, () => {
  if (speedTimer) return
  speedTimer = setInterval(() => {
    const now = Date.now(); const elapsed = (now - lastTime) / 1000
    if (elapsed > 0) {
      const curLoaded = parseSize(props.uploaded); const diff = curLoaded - lastLoaded
      if (diff > 0) speedMbps.value = diff / elapsed / 1024 / 1024
    }
    lastTime = now; lastLoaded = parseSize(props.uploaded)
  }, 1000)
})

onBeforeUnmount(() => { if (speedTimer) clearInterval(speedTimer) })

const speed = computed(() => {
  if (props.phase !== 'uploading') return ''
  if (speedMbps.value >= 1) return `${speedMbps.value.toFixed(1)} MB/s`
  if (speedMbps.value > 0) return `${(speedMbps.value * 1024).toFixed(0)} KB/s`
  return ''
})

const eta = computed(() => {
  if (props.phase !== 'uploading' || !speedMbps.value) return '计算中'
  const remaining = parseSize(props.fileSize) - parseSize(props.uploaded)
  if (remaining <= 0) return '即将完成'
  const sec = remaining / 1024 / 1024 / speedMbps.value
  if (sec < 60) return `${Math.ceil(sec)}秒`
  return `${Math.ceil(sec / 60)}分钟`
})
</script>

<style scoped>
.parsing-wrapper {
  display: flex; align-items: center; justify-content: center; height: 100%; padding: 24px;
  background: linear-gradient(135deg, #0a0e1a, #131829);
}
.upload-card {
  width: 100%; max-width: 520px; padding: 32px; border-radius: 20px;
  background: rgba(20,25,45,0.6); backdrop-filter: blur(20px);
  border: 1px solid rgba(0,212,255,0.1);
  box-shadow: 0 20px 60px rgba(0,0,0,0.4), 0 0 40px rgba(0,212,255,0.05);
}
.file-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.file-icon {
  flex-shrink: 0; width: 52px; height: 52px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(123,47,247,0.15));
  color: #00d4ff; border: 1px solid rgba(0,212,255,0.2);
}
.file-icon.parsing { color: #7b2ff7; background: linear-gradient(135deg,rgba(123,47,247,0.15),rgba(0,212,255,0.15)); border-color: rgba(123,47,247,0.2); }
.file-icon.uploading { animation: iconPulse 2s ease-in-out infinite; }
@keyframes iconPulse { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-3px)} }
.file-meta { flex: 1; min-width: 0; }
.file-name { color: rgba(255,255,255,0.92); font-size: 15px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px; }
.file-size-row { display: flex; align-items: center; gap: 6px; color: rgba(255,255,255,0.5); font-size: 12px; }
.file-size { font-variant-numeric: tabular-nums; }
.phase-section { margin-bottom: 12px; }
.step-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.step-badge { width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; flex-shrink: 0; }
.step-badge.active { background: linear-gradient(135deg,#00d4ff,#7b2ff7); color: white; box-shadow: 0 0 12px rgba(0,212,255,0.4); }
.step-badge.done { background: #00d4ff; color: white; box-shadow: 0 0 8px rgba(0,212,255,0.3); }
.step-label { flex: 1; color: rgba(255,255,255,0.7); font-size: 13px; }
.step-label.done-label { color: rgba(255,255,255,0.4); text-decoration: line-through; }
.step-check { color: #00d4ff; font-size: 14px; font-weight: 600; }
.step-percent { color: #00d4ff; font-size: 13px; font-weight: 500; font-variant-numeric: tabular-nums; }
.progress-track { height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; overflow: hidden; margin-bottom: 10px; }
.progress-fill { height: 100%; border-radius: 3px; transition: width 0.3s ease; position: relative; overflow: hidden; }
.progress-fill.upload-color { background: linear-gradient(90deg,#00d4ff,#0099cc); }
.progress-fill.parse-color { background: linear-gradient(90deg,#7b2ff7,#b44dff); }
.progress-shimmer { position: absolute; inset: 0; background: linear-gradient(90deg,transparent 0%,rgba(255,255,255,0.3) 50%,transparent 100%); animation: shimmer 1.5s infinite; }
@keyframes shimmer { 0%{transform:translateX(-100%)} 100%{transform:translateX(100%)} }
.stage-row { display: flex; justify-content: space-between; align-items: center; min-height: 20px; }
.stage-indicator { display: flex; align-items: center; gap: 8px; }
.stage-dot { width: 6px; height: 6px; border-radius: 50%; animation: dotPulse 1.5s ease-in-out infinite; }
.stage-dot.uploading { background: #00d4ff; box-shadow: 0 0 8px #00d4ff; }
.stage-dot.parsing { background: #b44dff; box-shadow: 0 0 8px #b44dff; }
@keyframes dotPulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.8); } }
.stage-text { color: rgba(255,255,255,0.6); font-size: 12px; letter-spacing: 0.3px; }
.speed-text { color: rgba(255,255,255,0.35); font-size: 11px; font-variant-numeric: tabular-nums; }
</style>

<template>
  <div class="parsing-wrapper">
    <div class="file-card">
      <div class="scan-area">
        <div class="scan-line"></div>
        <div class="scan-glow"></div>
      </div>
      <div class="file-icon">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
          <path d="M6 4H20L26 10V26C26 27.1 25.1 28 24 28H6C4.9 28 4 27.1 4 26V6C4 4.9 4.9 4 6 4Z" stroke="#00d4ff" stroke-width="1.5" fill="rgba(0,212,255,0.05)"/>
          <path d="M14 14V22M10 18H18" stroke="#00d4ff" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </div>
      <div class="file-info">
        <span class="file-name">{{ fileName }}</span>
        <span class="file-size">{{ fileSize }}</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
      <div class="status-text">{{ statusText }}</div>
    </div>
    <div class="fiber-lines">
      <div v-for="i in 6" :key="i" class="fiber" :style="fiberStyle(i)"></div>
    </div>
    <div class="particles-container">
      <div
        v-for="i in 12"
        :key="i"
        class="particle"
        :style="particleStyle(i)"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  fileName: string
  fileSize: string
  progress: number
}>()

const statusText = computed(() => {
  if (props.progress < 30) return '正在接收数据流...'
  if (props.progress < 60) return 'AI 量子引擎解析中...'
  if (props.progress < 90) return '构建语义索引...'
  return '准备就绪'
})

function fiberStyle(i: number) {
  const angle = 200 + i * 8
  const delay = i * 0.3
  return {
    transform: `rotate(${angle}deg)`,
    animationDelay: `${delay}s`,
  }
}

function particleStyle(i: number) {
  const top = 20 + Math.random() * 60
  const delay = i * 0.4
  const duration = 1.5 + Math.random() * 2
  const size = 2 + Math.random() * 3
  return {
    top: `${top}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    width: `${size}px`,
    height: `${size}px`,
  }
}
</script>

<style scoped>
.parsing-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.file-card {
  position: relative;
  z-index: 2;
  width: 360px;
  padding: 24px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 40px rgba(0, 212, 255, 0.08);
}

.scan-area {
  position: absolute;
  inset: 0;
  border-radius: 16px;
  overflow: hidden;
  pointer-events: none;
}

.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00ff88, transparent);
  box-shadow: 0 0 12px rgba(0, 255, 136, 0.6), 0 0 24px rgba(0, 255, 136, 0.3);
  animation: scanDown 2.5s ease-in-out infinite;
}

.scan-glow {
  position: absolute;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(180deg, transparent, rgba(0, 255, 136, 0.03), transparent);
  animation: glowDown 2.5s ease-in-out infinite;
}

@keyframes scanDown {
  0% { top: -2px; }
  100% { top: 100%; }
}

@keyframes glowDown {
  0% { top: -80px; }
  100% { top: 100%; }
}

.file-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.file-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  margin-bottom: 16px;
}

.file-name {
  color: rgba(255, 255, 255, 0.85);
  font-size: 15px;
  font-weight: 500;
  text-align: center;
  word-break: break-all;
}

.file-size {
  color: rgba(255, 255, 255, 0.35);
  font-size: 12px;
}

.progress-track {
  height: 3px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #7b2ff7);
  border-radius: 2px;
  transition: width 0.5s ease;
  box-shadow: 0 0 8px rgba(0, 212, 255, 0.4);
}

.status-text {
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 2px;
}

.fiber-lines {
  position: absolute;
  right: 30px;
  top: 0;
  bottom: 0;
  width: 120px;
  pointer-events: none;
}

.fiber {
  position: absolute;
  right: 0;
  top: 50%;
  width: 120px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.15), transparent);
  transform-origin: right center;
  animation: fiberPulse 2s ease-in-out infinite;
}

@keyframes fiberPulse {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 0.8; }
}

.particles-container {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  pointer-events: none;
}

.particle {
  position: absolute;
  right: 0;
  border-radius: 50%;
  background: rgba(0, 212, 255, 0.6);
  box-shadow: 0 0 6px rgba(0, 212, 255, 0.4);
  animation: particleFly 2.5s ease-out infinite;
}

@keyframes particleFly {
  0% {
    transform: translateX(0) translateY(0);
    opacity: 1;
  }
  100% {
    transform: translateX(-400px) translateY(-20px);
    opacity: 0;
  }
}
</style>

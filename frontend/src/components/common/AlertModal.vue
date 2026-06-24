<template>
  <Teleport to="body">
    <!-- 전체 화면 캔버스 confetti (모달 밖) -->
    <canvas
      v-if="modalType === 'successConfetti'"
      ref="confettiCanvas"
      class="confetti-canvas"
    />

    <Transition name="modal-fade">
      <div v-if="isVisible" class="modal-overlay" @click.self="onCancel">
        <div class="modal-box">

          <!-- 아이콘 -->
          <div class="modal-icon" :class="
            modalType === 'confirm' ? 'icon-confirm' :
            modalType === 'success' || modalType === 'successConfetti' ? 'icon-success' :
            'icon-alert'
          ">
            <i :class="
              modalType === 'confirm' ? 'bi bi-question-lg' :
              modalType === 'success' || modalType === 'successConfetti' ? 'bi bi-check-lg' :
              'bi bi-info-lg'
            " />
          </div>

          <!-- 내용 -->
          <p class="modal-title">{{ modalTitle }}</p>
          <p class="modal-message">{{ modalMessage }}</p>

          <!-- 버튼 -->
          <div class="modal-actions" :class="{ single: modalType !== 'confirm' }">
            <button v-if="modalType === 'confirm'" class="btn-cancel" @click="onCancel">
              {{ modalCancelText }}
            </button>
            <button class="btn-confirm" @click="onConfirm">
              {{ modalConfirmText }}
            </button>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useAlert } from '@/composables/useAlert'

const {
  isVisible,
  modalTitle,
  modalMessage,
  modalType,
  modalConfirmText,
  modalCancelText,
  onConfirm,
  onCancel,
} = useAlert()

const confettiCanvas = ref(null)
let animationId = null

const COLORS = [
  '#6A7F5A', '#F2C15D', '#86A78A', '#c0756a',
  '#7a9bc4', '#A0BAA3', '#f4a261', '#e76f51',
  '#2a9d8f', '#e9c46a', '#264653',
]

const SHAPES = ['circle', 'rect', 'triangle']

function createParticles(canvas) {
  const particles = []
  const count = 180

  for (let i = 0; i < count; i++) {
    const angle = (Math.random() * Math.PI * 2)
    const speed = 4 + Math.random() * 10
    particles.push({
      x: canvas.width / 2 + (Math.random() - 0.5) * 200,
      y: canvas.height / 2 + (Math.random() - 0.5) * 100,
      vx: Math.cos(angle) * speed * (Math.random() > 0.5 ? 1 : -1),
      vy: -Math.abs(Math.sin(angle) * speed) - Math.random() * 8,
      gravity: 0.25 + Math.random() * 0.15,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      shape: SHAPES[Math.floor(Math.random() * SHAPES.length)],
      size: 6 + Math.random() * 10,
      rotation: Math.random() * Math.PI * 2,
      rotationSpeed: (Math.random() - 0.5) * 0.2,
      opacity: 1,
      decay: 0.012 + Math.random() * 0.008,
    })
  }
  return particles
}

function drawParticle(ctx, p) {
  ctx.save()
  ctx.globalAlpha = p.opacity
  ctx.fillStyle = p.color
  ctx.translate(p.x, p.y)
  ctx.rotate(p.rotation)

  if (p.shape === 'circle') {
    ctx.beginPath()
    ctx.arc(0, 0, p.size / 2, 0, Math.PI * 2)
    ctx.fill()
  } else if (p.shape === 'rect') {
    ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2)
  } else {
    ctx.beginPath()
    ctx.moveTo(0, -p.size / 2)
    ctx.lineTo(p.size / 2, p.size / 2)
    ctx.lineTo(-p.size / 2, p.size / 2)
    ctx.closePath()
    ctx.fill()
  }

  ctx.restore()
}

function launchConfetti(canvas) {
  const ctx = canvas.getContext('2d')
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight

  const particles = createParticles(canvas)

  // 두 번째 burst — 살짝 딜레이 후 추가 발사
  setTimeout(() => {
    const extra = createParticles(canvas)
    extra.forEach(p => {
      p.x = Math.random() * canvas.width
      p.vy = -6 - Math.random() * 6
      particles.push(p)
    })
  }, 300)

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i]
      p.x += p.vx
      p.y += p.vy
      p.vy += p.gravity
      p.vx *= 0.99
      p.rotation += p.rotationSpeed
      p.opacity -= p.decay

      if (p.opacity <= 0) {
        particles.splice(i, 1)
        continue
      }

      drawParticle(ctx, p)
    }

    if (particles.length > 0) {
      animationId = requestAnimationFrame(animate)
    } else {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
    }
  }

  animate()
}

watch(isVisible, async (val) => {
  if (val && modalType.value === 'successConfetti') {
    await nextTick()
    await nextTick() // 두 번 기다려야 canvas가 DOM에 올라와요
    if (confettiCanvas.value) {
      if (animationId) cancelAnimationFrame(animationId)
      launchConfetti(confettiCanvas.value)
    }
  } else {
    if (animationId) cancelAnimationFrame(animationId)
  }
})
</script>

<style scoped>
.confetti-canvas {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 3000;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-box {
  background: #fff;
  border-radius: 20px;
  padding: 32px 28px 24px;
  width: 100%;
  max-width: 360px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  text-align: center;
  position: relative;
  z-index: 2001;
}

.modal-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  margin-bottom: 16px;
}
.icon-alert   { background: #EAF0EB; color: #6A7F5A; }
.icon-confirm { background: #f5eccb; color: #8a6d1a; }
.icon-success { background: #dde8de; color: #4a7a51; }

.modal-title {
  font-size: 1rem;
  font-weight: 700;
  color: #2d2d25;
  margin-bottom: 8px;
}

.modal-message {
  font-size: 0.88rem;
  color: #6b6b5e;
  line-height: 1.7;
  margin-bottom: 24px;
  white-space: pre-line;
}

.modal-actions {
  display: flex;
  gap: 10px;
  width: 100%;
}
.modal-actions.single { justify-content: center; }

.btn-cancel {
  flex: 1;
  padding: 10px 0;
  border-radius: 10px;
  border: 1.5px solid #d4d3c4;
  background: #fff;
  color: #6b6b5e;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-cancel:hover { background: #f5f4f0; }

.btn-confirm {
  flex: 1;
  padding: 10px 0;
  border-radius: 10px;
  border: none;
  background: #6A7F5A;
  color: #fff;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-confirm:hover { background: #5a6e4c; }
.modal-actions.single .btn-confirm { max-width: 160px; }

.modal-fade-enter-active { animation: modalIn 0.2s ease; }
.modal-fade-leave-active { animation: modalIn 0.15s ease reverse; }
@keyframes modalIn {
  from { opacity: 0; transform: scale(0.95); }
  to   { opacity: 1; transform: scale(1); }
}
</style>
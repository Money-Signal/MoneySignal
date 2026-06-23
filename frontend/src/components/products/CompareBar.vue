<template>
  <Transition name="slide-up">
    <div v-if="store.compareList.length > 0" class="compare-bar">
      <div class="compare-bar-inner container">

        <div class="compare-slots">
          <div
            v-for="product in store.compareList"
            :key="product.id"
            class="compare-slot filled"
          >
            <div class="slot-info">
              <span class="slot-bank">{{ product.kor_co_nm }}</span>
              <span class="slot-name">{{ product.fin_prdt_nm }}</span>
            </div>
            <button class="slot-remove" @click="store.removeFromCompare(product.id)">
              <i class="bi bi-x" />
            </button>
          </div>

          <div
            v-for="n in (3 - store.compareList.length)"
            :key="'empty-' + n"
            class="compare-slot empty"
          >
            <i class="bi bi-plus-circle me-1" />상품 추가
          </div>
        </div>

        <div class="compare-actions">
          <button class="btn-clear" @click="store.clearCompare()">초기화</button>
          <button
            class="btn-compare"
            :disabled="store.compareList.length < 2"
            @click="$emit('open')"
          >
            <i class="bi bi-bar-chart-line me-1" />
            비교하기 {{ store.compareList.length }}/3
          </button>
        </div>

      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useProductStore } from '@/stores/product'
const store = useProductStore()
defineEmits(['open'])
</script>

<style scoped>
.compare-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #F5F4EC;
  border-top: 1.5px solid #D8D6C5;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.08);
  z-index: 900;
  padding: 12px 0;
}

.compare-bar-inner {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.compare-slots {
  display: flex;
  gap: 10px;
  flex: 1;
  flex-wrap: wrap;
}

.compare-slot {
  flex: 1;
  min-width: 160px;
  max-width: 240px;
  border-radius: 10px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.compare-slot.filled {
  background: #fff;
  border: 1.5px solid #C8C6B4;
}

.compare-slot.empty {
  background: #ECEADC;
  border: 1.5px dashed #C8C6B4;
  color: #a8a898;
  font-size: 0.8rem;
  justify-content: center;
}

.slot-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.slot-bank {
  font-size: 0.72rem;
  color: #9a9888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.slot-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: #2d2d25;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.slot-remove {
  background: none;
  border: none;
  padding: 0 2px;
  font-size: 1rem;
  color: #a0a090;
  cursor: pointer;
  line-height: 1;
  flex-shrink: 0;
  transition: color 0.15s;
}
.slot-remove:hover { color: #c0756a; }

.compare-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn-clear {
  padding: 8px 16px;
  font-size: 0.85rem;
  border: 1.5px solid #C8C6B4;
  border-radius: 8px;
  background: #ECEADC;
  color: #7a7a6a;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-clear:hover {
  border-color: #a8a898;
  color: #4a4a3a;
}

.btn-compare {
  padding: 8px 20px;
  font-size: 0.88rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  background: #5a5a4a;
  color: #F5F4EC;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-compare:hover:not(:disabled) { background: #3d3d30; }
.btn-compare:disabled {
  background: #C8C6B4;
  cursor: not-allowed;
}

/* 슬라이드 업 트랜지션 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>

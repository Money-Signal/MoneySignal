<template>
  <div class="filter-wrapper">
    <div class="asset-toggle-group">
      <button 
        :class="['toggle-btn', { 'active-gold': filters.assetType === 'gold' }]"
        @click="changeAsset('gold')"
      >
        금 시세
      </button>
      <button 
        :class="['toggle-btn', { 'active-silver': filters.assetType === 'silver' }]"
        @click="changeAsset('silver')"
      >
        은 시세
      </button>
    </div>

    <div class="date-control-group">
      <div class="input-container">
        <label><i class="bi bi-calendar-check me-1"></i> 시작일</label>
        <input type="date" v-model="filters.startDate" :min="minDate" :max="maxDate" />
      </div>
      
      <span class="date-separator">~</span>
      
      <div class="input-container">
        <label><i class="bi bi-calendar-x me-1"></i> 종료일</label>
        <input type="date" v-model="filters.endDate" :min="minDate" :max="maxDate" />
      </div>

      <div class="button-action-group">
        <button class="action-btn submit-btn" @click="emitFilter">
          <i class="bi bi-search"></i> 조회
        </button>
        <button class="action-btn reset-btn" @click="resetPeriod">
          <i class="bi bi-arrow-counterclockwise"></i> 전체기간
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  minDate: { type: String, default: '' },
  maxDate: { type: String, default: '' }
})

const emit = defineEmits(['filterChanged'])

const filters = ref({
  assetType: 'gold',
  startDate: '',
  endDate: ''
})

watch(() => [props.minDate, props.maxDate], ([newMin, newMax]) => {
  if (!filters.value.startDate && newMin) filters.value.startDate = newMin
  if (!filters.value.endDate && newMax) filters.value.endDate = newMax
}, { immediate: true })

const changeAsset = (type) => {
  filters.value.assetType = type
  emitFilter()
}

const emitFilter = () => {
  emit('filterChanged', { ...filters.value })
}

const resetPeriod = () => {
  filters.value.startDate = props.minDate
  filters.value.endDate = props.maxDate
  emitFilter()
}
</script>

<style scoped>
.filter-wrapper {
  background: #ffffff;
  border: 1px solid #E1E6E2;
  border-radius: 16px;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.02);
}

/* 자산 선택 버튼 공통 스타일 */
.asset-toggle-group {
  display: flex;
  gap: 10px;
}
.toggle-btn {
  padding: 10px 20px;
  border-radius: 20px;
  border: 1px solid #cbd5cc;
  background: #ffffff;
  color: #4a554b;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.toggle-btn:hover {
  background: #F4F7F2;
}

/* 🎯 [금 시세 활성화]: 고급스러운 톤다운 소프트 골드 테마 */
.toggle-btn.active-gold {
  background: #D4AF37; /* 클래식 골드 컬러 */
  color: #ffffff;
  border-color: #D4AF37;
  box-shadow: 0 4px 10px rgba(212, 175, 55, 0.25);
}

/* 🎯 [은 시세 활성화]: 반장님 그래프 선 색상(#86A78A)과 완벽 동기화 */
.toggle-btn.active-silver {
  background: #8A9A86; /* 그래프 선 색상 */
  color: #ffffff;
  border-color: #8A9A86;
  box-shadow: 0 4px 10px rgba(134, 167, 138, 0.25);
}

/* 날짜 입력 및 버튼 컨트롤 영역 */
.date-control-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.input-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.input-container label {
  font-size: 12px;
  color: #728273;
  font-weight: 600;
  padding-left: 2px;
  display: flex;
  align-items: center;
}
.input-container label i {
  color: #86A78A;
}
input[type="date"] {
  padding: 9px 14px;
  border-radius: 10px;
  border: 1px solid #D1DBC5;
  color: #2D3E2E;
  font-weight: 500;
  font-size: 14px;
  outline: none;
  background: #ffffff;
  transition: all 0.2s ease;
}
input[type="date"]:focus {
  border-color: #86A78A;
  box-shadow: 0 0 0 3px rgba(134, 167, 138, 0.15);
}
.date-separator {
  color: #A0BAA3;
  font-weight: 500;
  margin-top: 20px;
}

/* 버튼 그룹 스타일 */
.button-action-group {
  display: flex;
  gap: 8px;
  margin-top: 20px;
}
.action-btn {
  padding: 10px 18px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  border: 1px solid transparent;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 조회 버튼 */
.submit-btn {
  background: #2D3E2E;
  color: #ffffff;
}
.submit-btn:hover {
  background: #1E2B1F;
  box-shadow: 0 4px 12px rgba(45, 62, 46, 0.3);
  transform: translateY(-1px);
}

/* 전체기간 버튼 */
.reset-btn {
  background: #F4F7F2;
  color: #556256;
  border-color: #D1DBC5;
}
.reset-btn:hover {
  background: #E8EFE5;
  color: #2D3E2E;
  border-color: #86A78A;
  transform: translateY(-1px);
}
</style>
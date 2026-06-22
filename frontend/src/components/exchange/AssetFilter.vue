<template>
  <div class="filter-wrapper">
    <div class="asset-toggle-group">
      <button 
        :class="['toggle-btn', { active: filters.assetType === 'gold' }]"
        @click="changeAsset('gold')"
      >
        🪙 금 시세
      </button>
      <button 
        :class="['toggle-btn', { active: filters.assetType === 'silver' }]"
        @click="changeAsset('silver')"
      >
        🥈 은 시세
      </button>
    </div>

    <div class="date-control-group">
      <div class="input-container">
        <label>시작일</label>
        <input type="date" v-model="filters.startDate" :min="minDate" :max="maxDate" />
      </div>
      
      <span class="date-separator">~</span>
      
      <div class="input-container">
        <label>종료일</label>
        <input type="date" v-model="filters.endDate" :min="minDate" :max="maxDate" />
      </div>

      <div class="button-action-group">
        <button class="action-btn submit-btn" @click="emitFilter">
          🔍 조회
        </button>
        <button class="action-btn reset-btn" @click="resetPeriod">
          🔄 전체기간
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

// 엑셀 원본 날짜 한계값이 넘어오면 필터 기본값으로 자동 연동
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
  background: #f7f9f6;
  border: 1px solid #e1e6e2;
  border-radius: 14px;
  padding: 18px 24px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

/* 자산 선택 버튼 스타일 */
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
.toggle-btn.active {
  background: #556256;
  color: #ffffff;
  border-color: #556256;
  box-shadow: 0 4px 10px rgba(85, 98, 86, 0.2);
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
  gap: 4px;
}
.input-container label {
  font-size: 11px;
  color: #728273;
  font-weight: 600;
  padding-left: 2px;
}
input[type="date"] {
  padding: 9px 12px;
  border-radius: 8px;
  border: 1px solid #cbd5cc;
  color: #333;
  font-weight: 500;
  outline: none;
  background: #ffffff;
}
.date-separator {
  color: #8a9a8d;
  font-weight: bold;
  margin-top: 16px;
}

/* 🚨 버튼 그룹 스타일 통일 디자인 적용 */
.button-action-group {
  display: flex;
  gap: 8px;
  margin-top: 16px; /* 라벨 높이 밸런스 정렬 */
}
.action-btn {
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  border: none;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

/* 조회 버튼 - 메인 액션 테마 컬러 */
.submit-btn {
  background: #475569;
  color: #ffffff;
}
.submit-btn:hover {
  background: #334155;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(51, 65, 85, 0.2);
}

/* 전체기간 버튼 - 서브 보조 테마 컬러 */
.reset-btn {
  background: #64748b;
  color: #ffffff;
}
.reset-btn:hover {
  background: #475569;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(71, 85, 105, 0.2);
}
</style>
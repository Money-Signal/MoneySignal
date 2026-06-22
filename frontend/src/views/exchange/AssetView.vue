<template>
  <div class="asset-view-container">
    <h2>📈 원자재 실시간 자산 시세 조회</h2>
    
    <AssetFilter 
      :min-date="excelMinDate" 
      :max-date="excelMaxDate" 
      @filterChanged="handleFilterChange" 
    />
    
    <div class="chart-section">
      <AssetChart 
        v-if="!isLoading && chartData.labels && chartData.labels.length > 0" 
        :chart-data="chartData" 
      />
      
      <div v-else-if="isLoading" class="status-state">
        ⏳ 시세 데이터를 불러오는 중입니다...
      </div>

      <div v-else class="status-state empty-state">
        ❌ 해당 기간 내에 데이터가 존재하지 않습니다.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import AssetFilter from '@/components/exchange/AssetFilter.vue'
import AssetChart from '@/components/exchange/AssetChart.vue'

// 상태 관리 변수
const excelMinDate = ref('')
const excelMaxDate = ref('')
const isLoading = ref(false) // 🚨 로딩 상태 추가

// 차트 데이터 기본 구조 세팅
const chartData = ref({
  asset_type: 'gold',
  labels: [],
  prices: []
})

// 현재 필터 상태 관리
const currentFilters = ref({ 
  assetType: 'gold', 
  startDate: '', 
  endDate: '' 
})

// 백엔드 API 호출 함수
const fetchChartData = async () => {
  isLoading.value = true // 로딩 시작
  try {
    const response = await axios.get('http://localhost:8000/api/exchange/prices/', {
      params: {
        asset_type: currentFilters.value.assetType,
        start_date: currentFilters.value.startDate,
        end_date: currentFilters.value.endDate
      }
    })
    
    // 객체 할당으로 watch 트리거
    chartData.value = {
      asset_type: response.data.asset_type || currentFilters.value.assetType,
      labels: response.data.labels || [],
      prices: response.data.prices || []
    }
    
    // 엑셀 원본 시작일/종료일 저장
    excelMinDate.value = response.data.min_date || ''
    excelMaxDate.value = response.data.max_date || ''

  } catch (error) {
    console.error('시세 데이터를 가져오는데 실패했습니다:', error)
    chartData.value = { asset_type: 'gold', labels: [], prices: [] }
  } finally {
    isLoading.value = false // 로딩 종료
  }
}

// 필터 컴포넌트 이벤트 핸들러
const handleFilterChange = (filters) => {
  currentFilters.value = filters
  fetchChartData()
}

// 초기 로드
onMounted(() => {
  fetchChartData()
})
</script>

<style scoped>
.asset-view-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  color: #2D3E2E;
  margin-bottom: 20px;
  font-weight: 700;
}

.chart-section {
  background: #ffffff;
  border: 1px solid #E1E6E2;
  border-radius: 16px;
  padding: 24px;
  min-height: 450px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.status-state {
  color: #6B7A6E;
  font-size: 16px;
  font-weight: 600;
}

/* 데이터 없을 때 강조 스타일 */
.empty-state {
  color: #dc2626; /* 부드러운 경고형 레드 컬러 */
  background: #fef2f2;
  padding: 12px 24px;
  border-radius: 8px;
  border: 1px dashed #fca5a5;
}
</style>
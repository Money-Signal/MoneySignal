<template>
  <div class="asset-view-container">
    <h2 class="page-title">
      <i class="bi bi-graph-up-arrow me-2"></i> 원자재 실시간 자산 시세 조회
    </h2>
    
    <div class="row g-4 layout-content-wrapper">
      
      <div class="col-12 col-lg-8 left-main-panel">
        <AssetFilter 
          :min-date="excelMinDate" 
          :max-date="excelMaxDate" 
          @filterChanged="handleFilterChange" 
        />
        
        <div class="chart-section mt-3">
          <AssetChart 
            v-if="!isLoading && chartData && chartData.labels && chartData.labels.length > 0" 
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

      <div class="col-12 col-lg-4 right-news-panel">
        <CommodityNews :news-list="newsList" :loading="isNewsLoading" />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import AssetFilter from '@/components/exchange/AssetFilter.vue'
import AssetChart from '@/components/exchange/AssetChart.vue'
import CommodityNews from '@/components/exchange/CommodityNews.vue'

// 상태 관리 변수
const excelMinDate = ref('')
const excelMaxDate = ref('')
const isLoading = ref(false) 

// 뉴스 상태 변수
const newsList = ref([])
const isNewsLoading = ref(false)

// 🎯 처음부터 labels와 prices 배열을 명시적으로 초기화해서 'undefined' 원천 차단
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

// 뉴스 데이터를 가져오는 함수
const fetchNewsData = async () => {
  isNewsLoading.value = true
  try {
    const response = await axios.get('http://localhost:8000/api/exchange/news/', {
      params: { asset_type: currentFilters.value.assetType }
    })
    newsList.value = response.data.news || []
  } catch (error) {
    console.error('뉴스 데이터를 가져오는데 실패했습니다:', error)
    newsList.value = []
  } finally {
    isNewsLoading.value = false
  }
}

// 시세 데이터를 가져오는 함수
const fetchChartData = async () => {
  isLoading.value = true 
  try {
    const response = await axios.get('http://localhost:8000/api/exchange/prices/', {
      params: {
        asset_type: currentFilters.value.assetType,
        start_date: currentFilters.value.startDate,
        end_date: currentFilters.value.endDate
      }
    })
    
    // 🎯 데이터 매핑 시에도 방어 코드 추가
    chartData.value = {
      asset_type: response.data?.asset_type || currentFilters.value.assetType,
      labels: response.data?.labels || [],
      prices: response.data?.prices || []
    }
    
    excelMinDate.value = response.data?.min_date || ''
    excelMaxDate.value = response.data?.max_date || ''

  } catch (error) {
    console.error('시세 데이터를 가져오는데 실패했습니다:', error)
    // 에러 발생 시에도 빈 구조를 유지시켜 템플릿 크래시 방지
    chartData.value = { asset_type: 'gold', labels: [], prices: [] }
  } finally {
    isLoading.value = false 
  }
}

// 필터 변경 이벤트 핸들러
const handleFilterChange = (filters) => {
  currentFilters.value = filters
  fetchChartData()
  fetchNewsData()
}

onMounted(() => {
  fetchChartData()
  fetchNewsData()
})
</script>

<style scoped>
.asset-view-container {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
}

.page-title {
  color: #2D3E2E;
  margin-bottom: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
}
.page-title i {
  color: #86A78A;
}

.layout-content-wrapper {
  display: flex;
  align-items: stretch;
}

.left-main-panel {
  display: flex;
  flex-direction: column;
}

.chart-section {
  background: #ffffff;
  border: 1px solid #E1E6E2;
  border-radius: 16px;
  padding: 24px;
  height: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

/* 오른쪽 뉴스 판넬 상단 바짝 밀착 */
.right-news-panel :deep(.news-section-container) {
  margin-top: 0 !important;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 뉴스 목록 가로 1줄 및 스크롤바 높이 밸런싱 */
.right-news-panel :deep(.news-list) {
  grid-template-columns: 1fr !important; 
  max-height: 590px;
  overflow-y: auto;        
  padding-right: 4px;
}

.right-news-panel :deep(.news-list)::-webkit-scrollbar {
  width: 6px;
}
.right-news-panel :deep(.news-list)::-webkit-scrollbar-thumb {
  background: #c4c3b7;
  border-radius: 4px;
}

.status-state {
  color: #6B7A6E;
  font-size: 16px;
  font-weight: 600;
}

.empty-state {
  color: #dc2626; 
  background: #fef2f2;
  padding: 12px 24px;
  border-radius: 8px;
  border: 1px dashed #fca5a5;
}
</style>
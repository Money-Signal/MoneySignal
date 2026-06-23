<template>
  <div class="asset-view-container">
    <h2 class="page-title">
      <i class="bi bi-graph-up-arrow me-2"></i> 원자재 실시간 자산 시세 조회
    </h2>
    
    <div class="layout-content-wrapper">
      
      <div class="left-main-panel">
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
          <div v-else-if="isLoading" class="status-state">⏳ 시세 데이터를 불러오는 중입니다...</div>
          <div v-else class="status-state empty-state">❌ 해당 기간 내에 데이터가 존재하지 않습니다.</div>
        </div>
      </div>

      <div class="right-news-panel">
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

const excelMinDate = ref('')
const excelMaxDate = ref('')
const isLoading = ref(false) 
const newsList = ref([])
const isNewsLoading = ref(false)

const chartData = ref({ asset_type: 'gold', labels: [], prices: [] })
const currentFilters = ref({ assetType: 'gold', startDate: '', endDate: '' })

const fetchNewsData = async () => {
  isNewsLoading.value = true
  try {
    const response = await axios.get('http://localhost:8000/api/exchange/news/', { params: { asset_type: currentFilters.value.assetType } })
    newsList.value = response.data.news || []
  } catch (error) { newsList.value = [] } finally { isNewsLoading.value = false }
}

const fetchChartData = async () => {
  isLoading.value = true 
  try {
    const response = await axios.get('http://localhost:8000/api/exchange/prices/', {
      params: { asset_type: currentFilters.value.assetType, start_date: currentFilters.value.startDate, end_date: currentFilters.value.endDate }
    })
    chartData.value = { asset_type: response.data?.asset_type || currentFilters.value.assetType, labels: response.data?.labels || [], prices: response.data?.prices || [] }
    excelMinDate.value = response.data?.min_date || ''
    excelMaxDate.value = response.data?.max_date || ''
  } catch (error) { chartData.value = { asset_type: 'gold', labels: [], prices: [] } } finally { isLoading.value = false }
}

const handleFilterChange = (filters) => { currentFilters.value = filters; fetchChartData(); fetchNewsData() }

onMounted(() => { fetchChartData(); fetchNewsData() })
</script>

<style scoped>
.asset-view-container { padding: 24px; max-width: 1600px; margin: 0 auto; }
.page-title { color: #2D3E2E; margin-bottom: 24px; font-weight: 700; display: flex; align-items: center; }
.page-title i { color: #86A78A; }

/* 높이 정렬 핵심 스타일 */
.layout-content-wrapper {
  display: flex;
  align-items: stretch; /* 자식 높이 강제 동일화 */
  gap: 24px;
}

.left-main-panel { flex: 2; display: flex; flex-direction: column; }
.right-news-panel { flex: 1; min-width: 300px; }

.chart-section {
  background: #ffffff;
  border: 1px solid #E1E6E2;
  border-radius: 16px;
  padding: 24px;
  flex-grow: 1; /* 남은 공간 전체 채움 */
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

/* 오른쪽 뉴스 판넬 정렬 */
.right-news-panel :deep(.news-section-container) {
  height: 100%;
  margin-top: 0 !important;
  display: flex;
  flex-direction: column;
}

.right-news-panel :deep(.news-list) {
  flex-grow: 1;
  overflow-y: auto;
  max-height: 520px; /* 차트 영역과 시각적 높이 일치 */
  padding-right: 4px;
}
</style>
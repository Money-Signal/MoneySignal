<template>
  <div class="video-search-container">
    <div class="inner-container">
    <PageHeader title="영상 검색" description="금융 관련 유튜브 영상을 검색하고 시청하세요." />

    <div class="search-box">
      <input 
        v-model="searchQuery" 
        @keyup.enter="triggerNewSearch" 
        placeholder="검색어를 입력하세요..." 
      />
      <button @click="triggerNewSearch">검색</button>
    </div>

    <div v-if="videos.length > 0 && !isLoading" class="sort-toggle-group">
      <button 
        :class="['sort-btn', { active: currentSort === 'relevance' }]" 
        @click="changeSort('relevance')"
      >
        <i class="bi bi-hand-thumbs-up-fill me-1"></i> 추천순
      </button>
      <button 
        :class="['sort-btn', { active: currentSort === 'viewCount' }]" 
        @click="changeSort('viewCount')"
      >
        <i class="bi bi-fire me-1"></i> 인기순
      </button>
      <button 
        :class="['sort-btn', { active: currentSort === 'date' }]" 
        @click="changeSort('date')"
      >
        <i class="bi bi-clock-fill me-1"></i> 날짜순
      </button>
    </div>

    <div v-if="isLoading" class="status-msg">
      <div class="spinner-border spinner-border-sm text-success me-2" role="status"></div>
      영상을 불러오는 중입니다...
    </div>
    <div v-else-if="videos.length === 0" class="status-msg">
      <i class="bi bi-exclamation-triangle me-2"></i>검색 결과가 없습니다.
    </div>
    
    <div v-else class="video-grid-wrapper">
      <VideoList :videos="videos" />
    </div>

    <div v-if="videos.length > 0 && !isLoading" class="pagination-container">
      <nav aria-label="Page navigation">
        <ul class="custom-pagination">
          
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button class="page-link" @click="changePage(currentPage - 1)">
              <i class="bi bi-chevron-left"></i>
            </button>
          </li>

          <li 
            v-for="page in totalPages" 
            :key="page" 
            class="page-item" 
            :class="{ active: page === currentPage }"
          >
            <button class="page-link" @click="changePage(page)">
              {{ page }}
            </button>
          </li>

          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <button class="page-link" @click="changePage(currentPage + 1)">
              <i class="bi bi-chevron-right"></i>
            </button>
          </li>

        </ul>
      </nav>
    </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import VideoList from '@/components/video/VideoList.vue'
import PageHeader from '@/components/common/PageHeader.vue'

const searchQuery = ref('') 
const videos = ref([])
const isLoading = ref(false)

const currentPage = ref(1)
const totalPages = ref(1)
const currentSort = ref('relevance')

const fetchVideos = async (pageNumber = 1) => {
  isLoading.value = true
  try {
    const response = await axios.get('http://localhost:8000/api/video/search/', {
      params: { 
        q: searchQuery.value || '재테크', 
        page: pageNumber,
        sort_by: currentSort.value
      }
    })
    
    videos.value = response.data.videos || []
    currentPage.value = response.data.currentPage || 1
    totalPages.value = response.data.totalPages || 1
    
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (error) {
    console.error('유튜브 검색 에러:', error)
  } finally {
    isLoading.value = false
  }
}

const triggerNewSearch = () => {
  currentSort.value = 'relevance' 
  fetchVideos(1) 
}

const changeSort = (sortType) => {
  if (currentSort.value !== sortType) {
    currentSort.value = sortType
    fetchVideos(1) 
  }
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    fetchVideos(page)
  }
}

onMounted(() => {
  fetchVideos(1) 
})
</script>

<style scoped>
.video-search-container {
  background-color: #f9f8f5;
  min-height: 100vh;
}
.inner-container {
  max-width: 1320px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
}

h2 {
  color: #86A78A;
  margin-bottom: 30px;
  font-weight: 700;
}

.search-box {
  margin: 0 auto 25px;
  width: 100%;
  max-width: 600px;
  display: flex;
  gap: 10px;
}

input {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid #A0BAA3;
  border-radius: 8px;
  outline: none;
  background-color: #ffffff;
}

button {
  padding: 12px 24px;
  background-color: #A0BAA3;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.3s;
}
button:hover {
  background-color: #86A78A;
}

.status-msg {
  margin-top: 30px;
  color: #556256;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sort-toggle-group {
  display: flex;
  background: #ffffff;
  padding: 4px;
  border-radius: 10px;
  border: 1px solid #A0BAA3;
  margin: 0 auto 30px;
  width: fit-content;
}
.sort-btn {
  padding: 6px 16px;
  border: none;
  background: transparent;
  color: #728273;
  font-size: 13px;
  font-weight: bold;
  border-radius: 7px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.sort-btn:hover {
  color: #2D3E2E;
}
.sort-btn.active {
  background: #86A78A;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

/* 🎯 [핵심 수정] 3개씩 2줄(3*2) 배열을 강제 적용하는 스포일러 스타일 */
.video-grid-wrapper {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}
/* 자식 컴포넌트인 VideoList 안의 그리드 속성을 오버라이딩하여 최대 3열로 강제 제어합니다 */
.video-grid-wrapper :deep(.video-list) {
  display: grid !important;
  grid-template-columns: repeat(3, 1fr) !important; /* 무조건 가로 3열 고정 🔗 */
  gap: 24px !important;
}

/* 태블릿이나 모바일 화면을 위한 미디어 쿼리 대응 */
@media (max-width: 992px) {
  .video-grid-wrapper :deep(.video-list) {
    grid-template-columns: repeat(2, 1fr) !important; /* 패드 화면에선 2열 */
  }
}
@media (max-width: 576px) {
  .video-grid-wrapper :deep(.video-list) {
    grid-template-columns: repeat(1, 1fr) !important; /* 모바일에선 1열 */
  }
}

/* 페이지네이션 디자인 */
.pagination-container {
  margin-top: 50px;
  margin-bottom: 20px;
}
.custom-pagination {
  display: flex;
  list-style: none;
  padding: 0;
  gap: 6px;
  justify-content: center;
}
.page-link {
  color: #556256;
  background-color: #ffffff;
  border: 1px solid #A0BAA3;
  padding: 8px 14px;
  font-weight: bold;
  font-size: 14px;
  border-radius: 6px;
  transition: all 0.2s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.page-link:hover {
  background-color: #f0f3ee;
  border-color: #86A78A;
}
.page-item.active .page-link {
  background-color: #86A78A;
  border-color: #86A78A;
  color: #ffffff;
  box-shadow: 0 4px 10px rgba(134, 167, 138, 0.2);
}
.page-item.disabled .page-link {
  color: #b5beb6;
  background-color: #e4e6e4;
  border-color: #d1d5d1;
  cursor: not-allowed;
}
</style>
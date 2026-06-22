<template>
  <div class="video-search-container">
    <h2>🎥 영상 검색</h2>
    
    <div class="search-box">
      <input 
        v-model="searchQuery" 
        @keyup.enter="handleSearch" 
        placeholder="검색어를 입력하세요..." 
      />
      <button @click="handleSearch">검색</button>
    </div>

    <div v-if="isLoading" class="status-msg">⏳ 검색 중입니다...</div>
    <div v-else-if="videos.length === 0" class="status-msg">검색 결과가 없습니다.</div>
    <VideoList v-else :videos="videos" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import VideoList from '@/components/video/VideoList.vue'

const searchQuery = ref([])
const videos = ref([])
const isLoading = ref(false)

const handleSearch = async () => {
  isLoading.value = true
  try {
    const response = await axios.get('http://localhost:8000/api/video/search/', {
    params: { q: searchQuery.value }
    })
    videos.value = response.data.videos
  } catch (error) {
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  handleSearch() // 최초 접속 시 기본 검색어(재테크)로 자동 로드
})
</script>

<style scoped>
/* 전체 컨테이너: 배경색 적용 */
.video-search-container {
  background-color: #EBEADD;
  min-height: 100vh;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

h2 {
  color: #86A78A; /* 포인트 컬러 2 */
  margin-bottom: 30px;
}

/* 검색창 영역 */
.search-box {
  margin-bottom: 40px;
  width: 100%;
  max-width: 600px;
  display: flex;
  gap: 10px;
}

input {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid #A0BAA3; /* 포인트 컬러 1 */
  border-radius: 8px;
  outline: none;
  background-color: #ffffff;
}

button {
  padding: 12px 24px;
  background-color: #A0BAA3; /* 포인트 컬러 1 */
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.3s;
}

button:hover {
  background-color: #86A78A; /* 호버 시 포인트 컬러 2 */
}

/* 영상 리스트 레이아웃 */
.video-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  width: 100%;
  max-width: 1200px;
}
</style>
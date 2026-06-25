<template>
  <div class="video-search-container">
    <div class="inner-container">
      <PageHeader title="영상 검색" description="금융 관련 유튜브 영상을 검색하고 시청하세요." />

      <LoadingSpinner v-if="isLoading" />
      <template v-else>

      <div class="search-box">
        <input
          v-model="searchQuery"
          @keyup.enter="triggerNewSearch"
          placeholder="검색어를 입력하세요..."
        />
        <button @click="triggerNewSearch">검색</button>
      </div>

      <div v-if="videos.length > 0 && !isLoading" class="sort-toggle-group">
        <button :class="['sort-btn', { active: currentSort === 'relevance' }]" @click="changeSort('relevance')">
          <i class="bi bi-hand-thumbs-up-fill me-1"></i> 추천순
        </button>
        <button :class="['sort-btn', { active: currentSort === 'viewCount' }]" @click="changeSort('viewCount')">
          <i class="bi bi-fire me-1"></i> 인기순
        </button>
        <button :class="['sort-btn', { active: currentSort === 'date' }]" @click="changeSort('date')">
          <i class="bi bi-clock-fill me-1"></i> 날짜순
        </button>
      </div>

      <div v-if="videos.length === 0" class="status-msg">
        <i class="bi bi-exclamation-triangle me-2"></i>검색 결과가 없습니다.
      </div>

      <div v-else class="carousel-section">
        <div class="carousel-container">
          <button
            class="nav-btn"
            @click="prevSlide"
            :disabled="currentSlide === 0"
          >
            <i class="bi bi-chevron-left"></i>
          </button>

          <div class="carousel-viewport">
            <Transition :name="`slide-${direction}`">
              <div class="video-grid" :key="currentSlide">
                <VideoCard
                  v-for="video in visibleVideos"
                  :key="video.id"
                  :video="video"
                />
              </div>
            </Transition>
          </div>

          <button
            class="nav-btn"
            @click="nextSlide"
            :disabled="currentSlide >= totalSlides - 1"
          >
            <i class="bi bi-chevron-right"></i>
          </button>
        </div>

        <div class="dots-container">
          <span
            v-for="i in totalSlides"
            :key="i"
            :class="['dot', { active: i - 1 === currentSlide }]"
            @click="goToSlide(i - 1)"
          ></span>
        </div>
      </div>

      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import VideoCard from '@/components/video/VideoCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const searchQuery = ref('')
const videos = ref([])
const isLoading = ref(false)
const currentSort = ref('relevance')
const currentSlide = ref(0)
const direction = ref('right')

const ITEMS_PER_SLIDE = 6

const totalSlides = computed(() => Math.ceil(videos.value.length / ITEMS_PER_SLIDE))

const visibleVideos = computed(() => {
  const start = currentSlide.value * ITEMS_PER_SLIDE
  return videos.value.slice(start, start + ITEMS_PER_SLIDE)
})

const fetchVideos = async () => {
  isLoading.value = true
  currentSlide.value = 0
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/video/search/`, {
      params: {
        q: searchQuery.value || '재테크',
        sort_by: currentSort.value,
      },
    })
    videos.value = response.data.videos || []
  } catch (error) {
    console.error('유튜브 검색 에러:', error)
  } finally {
    isLoading.value = false
  }
}

const triggerNewSearch = () => {
  currentSort.value = 'relevance'
  fetchVideos()
}

const changeSort = (sortType) => {
  if (currentSort.value !== sortType) {
    currentSort.value = sortType
    fetchVideos()
  }
}

const nextSlide = () => {
  if (currentSlide.value < totalSlides.value - 1) {
    direction.value = 'right'
    currentSlide.value++
  }
}

const prevSlide = () => {
  if (currentSlide.value > 0) {
    direction.value = 'left'
    currentSlide.value--
  }
}

const goToSlide = (index) => {
  direction.value = index > currentSlide.value ? 'right' : 'left'
  currentSlide.value = index
}

onMounted(() => fetchVideos())
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

button:hover:not(:disabled) {
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

/* 정렬 버튼 */
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
  background-color: transparent;
}

.sort-btn.active {
  background: #86A78A;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

/* 캐러셀 */
.carousel-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.carousel-container {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.nav-btn {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  padding: 0;
  border-radius: 50%;
  background-color: #ffffff;
  border: 2px solid #A0BAA3;
  color: #556256;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  cursor: pointer;
}

.nav-btn:hover:not(:disabled) {
  background-color: #86A78A;
  border-color: #86A78A;
  color: #ffffff;
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  background-color: #e4e6e4;
  border-color: #d1d5d1;
}

.carousel-viewport {
  flex: 1;
  overflow: hidden;
  position: relative;
  min-height: 560px;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

/* 점 인디케이터 */
.dots-container {
  display: flex;
  gap: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #d1d5d1;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dot.active {
  background-color: #86A78A;
  width: 24px;
  border-radius: 4px;
}

/* 슬라이드 애니메이션 */
.slide-right-enter-active,
.slide-right-leave-active,
.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform 0.35s ease, opacity 0.35s ease;
}

.slide-right-leave-active,
.slide-left-leave-active {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}

.slide-right-enter-from {
  transform: translateX(60px);
  opacity: 0;
}

.slide-right-leave-to {
  transform: translateX(-60px);
  opacity: 0;
}

.slide-left-enter-from {
  transform: translateX(-60px);
  opacity: 0;
}

.slide-left-leave-to {
  transform: translateX(60px);
  opacity: 0;
}

/* 반응형 */
@media (max-width: 992px) {
  .video-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 576px) {
  .video-grid {
    grid-template-columns: 1fr;
  }

  .nav-btn {
    width: 36px;
    height: 36px;
    font-size: 13px;
  }
}
</style>

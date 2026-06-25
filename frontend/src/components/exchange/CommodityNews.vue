<template>
  <div class="news-section-container">
    <h3 class="section-title">
      <i class="bi bi-newspaper me-2"></i> 실시간 주요 뉴스
    </h3>
    
    <LoadingSpinner v-if="loading" />

    <div v-else-if="newsList && newsList.length > 0" class="news-list">
      <div v-for="(item, index) in newsList" :key="index" class="news-item">
        <a :href="item.link" target="_blank" rel="noopener noreferrer" class="news-link">
          <div class="news-header">
            <span class="news-source">
              <i class="bi bi-globe me-1"></i> 네이버 뉴스
            </span>
            <span class="news-time">
              <i class="bi bi-clock me-1"></i> {{ formatDate(item.pubDate) }}
            </span>
          </div>
          <h4 class="news-title" v-html="item.title"></h4>
          <p class="news-desc" v-html="item.description"></p>
          <div class="news-footer">
            <span>자세히 보기 <i class="bi bi-box-arrow-up-right ms-1"></i></span>
          </div>
        </a>
      </div>
    </div> <div v-else class="news-status text-center no-data">
      <i class="bi bi-chat-square-dots fs-3"></i>
      <p class="mt-2">관련 뉴스를 찾을 수 없습니다.</p>
    </div>
    
  </div>
</template>

<script setup>
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

defineProps({
  newsList: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false }
})

// 네이버의 독특한 시간 규격(RFC 822)을 한국식으로 예쁘게 바꾸는 함수
const formatDate = (dateStr) => {
  try {
    const date = new Date(dateStr)
    return `${date.getMonth() + 1}월 ${date.getDate()}일 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
  } catch (e) {
    return dateStr
  }
}
</script>

<style scoped>
.news-section-container {
  font-family: 'Pretendard', -apple-system, sans-serif;
  background-color: #F7F6F2; /* 지도 페이지와 톤앤매너 매칭 */
  border: 1px solid #e6e5da;
  border-radius: 12px;
  padding: 20px;
  margin-top: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #333d29;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}
.section-title i { color: #86A78A; }

.news-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}

.news-item {
  background-color: #ffffff;
  border: 1px solid #e6e5da;
  border-radius: 8px;
  transition: all 0.2s ease-in-out;
}

.news-item:hover {
  border-color: #86A78A;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(134, 167, 138, 0.15);
}

.news-link {
  text-decoration: none !important;
  color: inherit;
  padding: 14px;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
}

.news-header {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #888;
  margin-bottom: 8px;
}
.news-source i { color: #A0BAA3; }

.news-title {
  font-size: 13px;
  font-weight: 600;
  color: #222;
  margin: 0 0 6px 0;
  line-height: 1.4;
}

.news-desc {
  font-size: 12px;
  color: #666;
  margin: 0 0 12px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* 텍스트가 길면 두 줄만 보여주고 말줄임표(...) */
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-footer {
  margin-top: auto;
  font-size: 11px;
  color: #86A78A;
  font-weight: 600;
  text-align: right;
}

.news-status {
  padding: 40px 0;
  color: #666;
}
.no-data i { color: #c4c3b7; }
</style>
<template>
  <div class="video-grid-container">
    <VideoCard 
      v-for="video in videos" 
      :key="video.id" 
      :video="video" 
    />
  </div>
</template>

<script setup>
import VideoCard from '@/components/video/VideoCard.vue'

defineProps({
  videos: {
    type: Array,
    required: true,
    default: () => []
  }
})
</script>

<style scoped>
/* 화면 크기에 따라 알아서 격자 개수가 조절되는 반응형 그리드 */
.video-grid-container {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 20px;
  padding: 10px 0;
}

@media (min-width: 640px) {
  .video-grid-container {
    grid-template-columns: repeat(2, minmax(0, 1fr)); /* 모바일 가로/태블릿: 2개 */
  }
}

/* 🎯 [수정] 1024px 이상일 때 가로 3개로 설정 */
@media (min-width: 1024px) {
  .video-grid-container {
    grid-template-columns: repeat(3, minmax(0, 1fr)); /* 데스크탑 기본: 3개 */
  }
}

/* 🎯 [수정] 기존 1280px 조건에서도 4개로 늘어나지 않고 3개 상태를 유지하도록 제한합니다! */
@media (min-width: 1280px) {
  .video-grid-container {
    grid-template-columns: repeat(3, minmax(0, 1fr)); /* 초대형 화면도 3개 고정 ✨ */
  }
}
</style>
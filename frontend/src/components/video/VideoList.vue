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
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .video-grid-container {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (min-width: 1280px) {
  .video-grid-container {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
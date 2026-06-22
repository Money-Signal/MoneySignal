<template>
  <div class="video-card" @click="openVideo">
    <div class="thumbnail-wrapper">
      <img :src="video.thumbnail" :alt="video.title" class="thumbnail-img" />
    </div>

    <div class="video-info">
      <h3 class="video-title">{{ video.title }}</h3>
      <p class="channel-name">📺 {{ video.channelTitle }}</p>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  video: {
    type: Object,
    required: true
  }
})

// 카드를 누르면 실제 유튜브 영상 링크로 이동
const openVideo = () => {
  if (props.video.id) {
    const videoUrl = `https://www.youtube.com/watch?v=${props.video.id}`
    window.open(videoUrl, '_blank')
  }
}
</script>

<style scoped>
.video-card {
  background: #ffffff;
  border: 1px solid #e1e6e2;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
}

/* 마우스를 올리면 카드가 살짝 떠오르는 부드러운 효과 */
.video-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.thumbnail-wrapper {
  width: 100%;
  position: relative;
  padding-top: 56.25%; /* 16:9 유튜브 황금 비율 유지 */
  background: #000;
}

.thumbnail-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-info {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-grow: 1;
}

/* 제목이 너무 길어지면 2줄 처리 후 말줄임(...) 표시 */
.video-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.channel-name {
  font-size: 12px;
  color: #64748b;
  margin: 0;
  font-weight: 500;
}
</style>
<template>
  <div class="detail-container" v-if="video">
    <div class="content-wrapper container">
      <div class="main-content row g-4">
        <div class="video-container col-lg-8">
          <div class="video-wrapper">
            <iframe
              :src="`https://www.youtube.com/embed/${video.id}`"
              allowfullscreen
              class="video-player"
            ></iframe>
          </div>
        </div>
        
        <div class="info-card col-lg-4">
          <h1 class="title mb-3">{{ video.title }}</h1>
          <div class="meta-info mb-4 d-flex gap-3 text-muted fw-bold">
            <div class="channel text-dark">📺 {{ video.channelTitle }}</div>
            <div class="views">조회수: {{ parseInt(video.viewCount).toLocaleString() }}회</div>
          </div>
          
          <hr class="my-3" />
          
          <div class="description-header" style="font-size: 0.8rem; color: #6c757d; margin-bottom: 8px; font-weight: 600;">
            📋 영상 상세 설명
          </div>
          <div class="description-box p-4 bg-white border rounded-3 shadow-sm" style="margin-top: 4px; border-left: 4px solid #86A78A; background-color: #fcfcfc !important;">
            <p class="description-text mb-0" :class="{ 'collapsed': !isExpanded }" style="white-space: pre-wrap; line-height: 1.8; color: #333; font-size: 0.95rem;">
              {{ video.description }}
            </p>
            <button @click="isExpanded = !isExpanded" class="btn btn-link p-0 mt-2 text-success fw-bold" style="text-decoration: none; font-size: 0.85rem;">
              {{ isExpanded ? '접기 🔼' : '...더보기 🔽' }}
            </button>
          </div>
        </div>
      </div>

      <div class="related-section mt-5" v-if="relatedVideos.length">
        <div class="p-3 mb-4 bg-white border-start border-4 border-success shadow-sm rounded">
          <h3 class="mb-0 text-success fw-bold">✨ 함께 보면 좋은 영상</h3>
        </div>

        <div class="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4">
          <div v-for="rv in relatedVideos" :key="rv.id" class="col">
            <div class="card h-100 shadow-sm border-0 transition-hover" @click="goToVideo(rv.id)" style="cursor: pointer;">
              <img :src="rv.thumbnail" class="card-img-top" alt="thumbnail" />
              <div class="card-body">
                <h5 class="card-title text-truncate" style="font-size: 1rem;">{{ rv.title }}</h5>
                <p class="card-text text-muted" style="font-size: 0.85rem;">{{ rv.channelTitle }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const video = ref(null);
const relatedVideos = ref([]);
const isExpanded = ref(false); // 더보기/접기 상태 관리

const fetchVideoData = async (videoId) => {
  try {
    const res = await axios.get(`http://localhost:8000/api/video/detail/${videoId}/`);
    video.value = res.data.video;
    const resRelated = await axios.get(`http://localhost:8000/api/video/related/${videoId}/`);
    relatedVideos.value = resRelated.data.related;
    isExpanded.value = false; // 새 영상 불러올 때마다 접힌 상태로 초기화
  } catch (error) {
    console.error("데이터 로드 실패:", error);
  }
};

watch(() => route.params.videoId, (newId) => fetchVideoData(newId));
onMounted(() => fetchVideoData(route.params.videoId));

const goToVideo = (id) => {
  router.push(`/video/${id}`);
  window.scrollTo(0, 0);
};
</script>

<style scoped>
.detail-container { background-color: #EBEADD; min-height: 100vh; padding: 40px 20px; }
.video-wrapper { position: relative; width: 100%; padding-bottom: 56.25%; border-radius: 12px; border: 3px solid #A0BAA3; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.video-player { position: absolute; width: 100%; height: 100%; }
.info-card { padding: 30px; background: white; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 5px solid #86A78A; }

/* 더보기 토글 스타일 */
.description-text.collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.transition-hover { transition: transform 0.2s ease-in-out; }
.transition-hover:hover { transform: translateY(-8px); box-shadow: 0 10px 20px rgba(0,0,0,0.15) !important; }
.border-success { border-color: #86A78A !important; }
.text-success { color: #86A78A !important; }
.title { font-size: 1.5rem; }
</style>
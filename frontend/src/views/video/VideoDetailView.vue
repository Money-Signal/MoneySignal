<template>
  <div class="detail-container" v-if="video">
    <div class="content-wrapper container">
      <div class="main-content row g-4">
        
        <div class="col-12 col-lg-8 d-flex flex-column gap-3">
          
          <div class="video-wrapper">
            <iframe
              :src="`https://www.youtube.com/embed/${video.id}`"
              allowfullscreen
              class="video-player"
            ></iframe>
          </div>

          <div class="video-main-info p-3 bg-white rounded-3 shadow-sm border-start border-4 border-success">
            <h1 class="title mb-3">{{ video.title }}</h1>
            <div class="meta-info d-flex gap-3 text-muted fw-bold align-items-center flex-wrap">
              <div class="channel text-dark"><i class="bi bi-tv me-1 text-success"></i> {{ video.channelTitle }}</div>
              <div class="views"><i class="bi bi-eye me-1"></i> 조회수: {{ parseInt(video.viewCount).toLocaleString() }}회</div>
            </div>
          </div>

          <div class="description-box p-4 bg-white border rounded-3 shadow-sm" style="border-left: 4px solid #86A78A; background-color: #fcfcfc !important;">
            <p class="description-text mb-0" :class="{ 'collapsed': !isExpanded }" style="white-space: pre-wrap; line-height: 1.8; color: #333; font-size: 0.95rem;">
              {{ video.description }}
            </p>
            <button @click="isExpanded = !isExpanded" class="btn btn-link p-0 mt-2 text-success fw-bold" style="text-decoration: none; font-size: 0.85rem;">
              <span v-if="isExpanded">접기 <i class="bi bi-chevron-up ms-1"></i></span>
              <span v-else>...더보기 <i class="bi bi-chevron-down ms-1"></i></span>
            </button>
          </div>
        </div>
        
        <div class="col-12 col-lg-4">
          <div class="related-section" v-if="relatedVideos.length">
            <div class="p-3 mb-3 bg-white border-start border-4 border-success shadow-sm rounded">
              <h5 class="mb-0 text-success fw-bold related-title">
                <i class="bi bi-stars me-2"></i>함께 보면 좋은 영상
              </h5>
            </div>

            <div class="related-sidebar-list d-flex flex-column gap-3">
              <div 
                v-for="rv in relatedVideos.slice(0, 6)" 
                :key="rv.id" 
                class="card related-sidebar-card shadow-sm border-0 transition-hover" 
                @click="goToVideo(rv.id)"
              >
                <div class="row g-0 align-items-center">
                  <div class="col-5">
                    <img :src="rv.thumbnail" class="sidebar-card-img" alt="thumbnail" />
                  </div>
                  <div class="col-7">
                    <div class="card-body p-2 ps-3">
                      <h6 class="card-title text-line-clamp-2 mb-1" style="font-size: 0.9rem; font-weight: 600; line-height: 1.3;">
                        {{ rv.title }}
                      </h6>
                      <p class="card-text text-muted mb-0" style="font-size: 0.8rem;">{{ rv.channelTitle }}</p>
                    </div>
                  </div>
                </div>
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
const isExpanded = ref(false);

const fetchVideoData = async (videoId) => {
  try {
    const res = await axios.get(`http://localhost:8000/api/video/detail/${videoId}/`);
    video.value = res.data.video;
    const resRelated = await axios.get(`http://localhost:8000/api/video/related/${videoId}/`);
    relatedVideos.value = resRelated.data.related;
    isExpanded.value = false;
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
.detail-container { background-color: #f9f8f5; min-height: 100vh; padding: 2.5rem 2rem; }
.video-wrapper { position: relative; width: 100%; padding-bottom: 56.25%; border-radius: 12px; border: 3px solid #A0BAA3; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.video-player { position: absolute; width: 100%; height: 100%; }

.video-main-info {
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.04);
}

.description-text {
  word-break: break-all;
  overflow-wrap: break-word;
  max-width: 100%;
}

/* 더보기 접기 기본 4줄 캡슐화 */
.description-text.collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 🎯 [신규] 사이드바 세로형 비디오 카드 맞춤 디자인 스타일링 */
.related-sidebar-card {
  cursor: pointer;
  overflow: hidden;
  border-radius: 10px;
  background-color: #ffffff;
}
.sidebar-card-img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  display: block;
}
/* 두 줄 넘어가는 텍스트는 ... 처리하는 매직 코드 */
.text-line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.transition-hover { transition: transform 0.2s ease-in-out; }
.transition-hover:hover { transform: translateY(-4px); box-shadow: 0 6px 15px rgba(0,0,0,0.12) !important; }
.border-success { border-color: #86A78A !important; }
.text-success { color: #86A78A !important; }

.title { font-size: 1.4rem; font-weight: 700; color: #2D3E2E; }
.related-title { font-size: 1.1rem !important; letter-spacing: -0.5px; }
</style>
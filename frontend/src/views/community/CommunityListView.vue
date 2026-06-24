<template>
  <div class="page-outer">

    <div class="page-container">

      <PageHeader title="커뮤니티" description="금융 정보와 생각을 자유롭게 나눠보세요.">
        <RouterLink v-if="authStore.isLoggedIn" to="/community/write" class="write-btn">
          <i class="bi bi-pencil-square me-1" />글쓰기
        </RouterLink>
      </PageHeader>

      <!-- 인기글 섹션 -->
      <div v-if="popularPosts.length" class="section mb-5">
        <h3 class="section-title"><i class="bi bi-fire me-2" style="color:#F2A93B"/>인기글</h3>
        <div class="popular-grid">
          <div
            v-for="(post, i) in popularPosts"
            :key="post.id"
            class="popular-card"
            @click="router.push({ name: 'communityDetail', params: { id: post.id } })"
          >
            <div :class="['rank-num', `rank-${i + 1}`]">{{ i + 1 }}</div>
            <div class="popular-body">
              <div class="popular-tags">
                <span :class="['cat-tag', `cat-${post.category}`]">{{ categoryLabel(post.category) }}</span>
              </div>
              <p class="popular-title">{{ post.title }}</p>
              <div class="popular-footer">
                <span class="pf-author">{{ post.author_nickname }}</span>
                <span class="pf-likes"><i class="bi bi-heart-fill me-1" />{{ post.like_count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 카테고리 탭 -->
      <div class="tab-bar mb-3">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          :class="['tab-btn', `tab-${tab.value || 'ALL'}`, activeCategory === tab.value ? 'active' : '']"
          @click="onTabChange(tab.value)"
        >
          <i :class="['bi', tab.icon]" />
          {{ tab.label }}
        </button>
      </div>

      <!-- 검색 + 정렬 -->
      <div class="search-sort-row mb-4">
        <div class="search-wrap">
          <i class="bi bi-search search-icon" />
          <input v-model="searchQuery" class="search-input" placeholder="제목, 내용, 작성자 검색" />
          <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">
            <i class="bi bi-x-lg" />
          </button>
        </div>
        <div class="sort-group">
          <button :class="['sort-btn', sortBy === 'latest' ? 'active' : '']" @click="sortBy = 'latest'">최신순</button>
          <button :class="['sort-btn', sortBy === 'likes'  ? 'active' : '']" @click="sortBy = 'likes'">좋아요순</button>
          <button :class="['sort-btn', sortBy === 'views'  ? 'active' : '']" @click="sortBy = 'views'">조회수순</button>
        </div>
      </div>

      <!-- 로딩 -->
      <div v-if="store.isLoading" class="loading-wrap">
        <div class="spinner-border" style="color:#86A78A" role="status" />
      </div>

      <!-- 에러 -->
      <div v-else-if="store.error" class="alert alert-danger">{{ store.error }}</div>

      <!-- 빈 상태 -->
      <div v-else-if="filteredPosts.length === 0" class="empty-state">
        <i class="bi bi-chat-square-dots" />
        <p>{{ searchQuery ? `"${searchQuery}" 검색 결과가 없어요.` : '아직 게시글이 없어요.' }}</p>
        <RouterLink v-if="authStore.isLoggedIn && !searchQuery" to="/community/write" class="empty-write-btn">
          첫 글을 작성해보세요
        </RouterLink>
      </div>

      <!-- 게시글 목록 -->
      <div v-else>
        <p v-if="searchQuery" class="result-count mb-2"><b>{{ filteredPosts.length }}</b>개의 결과</p>
        <div class="post-list">
          <div
            v-for="post in filteredPosts"
            :key="post.id"
            class="post-card"
            @click="router.push({ name: 'communityDetail', params: { id: post.id } })"
          >
            <div class="pc-left">
              <div class="pc-meta-row">
                <span :class="['cat-tag', `cat-${post.category}`]">{{ categoryLabel(post.category) }}</span>
                <span class="pc-date">{{ formatDate(post.created_at) }}</span>
              </div>
              <p class="pc-title">{{ post.title }}</p>
              <p class="pc-preview">{{ post.content?.trim() }}</p>
              <div class="pc-bottom-row">
                <div class="pc-author-row">
                  <img :src="getAvatarUrl(post.author_image)" class="avatar" alt="프로필" />
                  <span class="pc-author">{{ post.author_nickname }}</span>
                </div>
                <div class="pc-stats">
                  <span class="stat-item heart"><i class="bi bi-heart-fill" />{{ post.like_count }}</span>
                  <span class="stat-item chat"><i class="bi bi-chat-fill" />{{ post.comment_count }}</span>
                  <span class="stat-item view"><i class="bi bi-eye-fill" />{{ post.view_count }}</span>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useCommunityStore } from '@/stores/community'
import { useAuthStore } from '@/stores/auth'
import PageHeader from '@/components/common/PageHeader.vue'

const router    = useRouter()
const store     = useCommunityStore()
const authStore = useAuthStore()

const BACKEND_URL   = 'http://127.0.0.1:8000'
const defaultAvatar = 'https://ui-avatars.com/api/?background=86A78A&color=fff&size=64'
const searchQuery    = ref('')
const activeCategory = ref('')
const allPosts       = ref([])
const sortBy         = ref('latest')

const tabs = [
  { value: '',           label: '전체',     icon: 'bi-grid-3x3-gap-fill' },
  { value: 'FREE',       label: '자유',     icon: 'bi-chat-square-text-fill' },
  { value: 'DEPOSIT',    label: '예금·적금', icon: 'bi-piggy-bank-fill' },
  { value: 'EXCHANGE',   label: '환율·해외', icon: 'bi-globe2' },
  { value: 'STOCK',      label: '주식·ETF', icon: 'bi-graph-up-arrow' },
  { value: 'REALESTATE', label: '부동산',   icon: 'bi-building-fill' },
  { value: 'QNA',        label: '질문',     icon: 'bi-patch-question-fill' },
]

const CATEGORY_MAP = {
  FREE: '자유', DEPOSIT: '예금·적금', EXCHANGE: '환율·해외',
  STOCK: '주식·ETF', REALESTATE: '부동산', QNA: '질문',
}
const categoryLabel = (value) => CATEGORY_MAP[value] ?? value

onMounted(async () => {
  await store.fetchPosts()
  allPosts.value = [...store.posts]
})

function onTabChange(category) {
  activeCategory.value = category
  searchQuery.value    = ''
  sortBy.value         = 'latest'
  store.fetchPosts(category)
}

const popularPosts = computed(() =>
  [...allPosts.value]
    .filter(p => p.like_count > 0)
    .sort((a, b) => b.like_count - a.like_count)
    .slice(0, 3)
)

const filteredPosts = computed(() => {
  let posts = store.posts
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    posts = posts.filter(p =>
      p.title.toLowerCase().includes(q) ||
      p.content?.toLowerCase().includes(q) ||
      p.author_nickname.toLowerCase().includes(q)
    )
  }
  if (sortBy.value === 'likes') return [...posts].sort((a, b) => b.like_count - a.like_count)
  if (sortBy.value === 'views') return [...posts].sort((a, b) => b.view_count - a.view_count)
  return posts
})

function getAvatarUrl(img) {
  if (!img) return defaultAvatar
  return img.startsWith('http') ? img : `${BACKEND_URL}${img}`
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr)
  const m = Math.floor(diff / 60000)
  const h = Math.floor(diff / 3600000)
  const d = Math.floor(diff / 86400000)
  if (m < 1)  return '방금 전'
  if (m < 60) return `${m}분 전`
  if (h < 24) return `${h}시간 전`
  if (d < 7)  return `${d}일 전`
  return dateStr.slice(0, 10).replaceAll('-', '.')
}
</script>

<style scoped>

/* ── 페이지 헤더 ── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}
.page-title h2 { font-size: 1.6rem; font-weight: 800; color: #2d2d25; margin-bottom: 4px; letter-spacing: -0.3px; }
.page-title p  { font-size: 0.86rem; color: #a0a090; margin: 0; }
.write-btn {
  padding: 10px 22px;
  background: #86A78A;
  color: #fff;
  border-radius: 50px;
  font-size: 0.88rem;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.2s;
  white-space: nowrap;
  box-shadow: 0 3px 10px rgba(107,158,112,0.3);
}
.write-btn:hover {
  background: #6e9272;
  transform: translateY(-1px);
  color: #fff;
}

/* ── 메인 컨텐츠 ── */

/* ── 섹션 제목 ── */
.section-title {
  font-size: 1rem;
  font-weight: 700;
  color: #2d2d25;
  margin-bottom: 14px;
}

/* ── 인기글 그리드 ── */
.popular-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.popular-card {
  background: #fff;
  border-radius: 18px;
  padding: 18px 20px;
  cursor: pointer;
  border: 1.5px solid #edecea;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
  transition: all 0.2s;
  display: flex;
  gap: 14px;
  align-items: flex-start;
}
.popular-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 28px rgba(107,158,112,0.14);
  border-color: #86A78A;
}
.rank-num {
  font-size: 1.65rem;
  font-weight: 900;
  flex-shrink: 0;
  line-height: 1;
  padding-top: 2px;
}
.rank-1 { color: #E8B84B; }
.rank-2 { color: #A8B0B8; }
.rank-3 { color: #C4895A; }
.popular-body { flex: 1; min-width: 0; }
.popular-tags { margin-bottom: 7px; }
.popular-title {
  font-size: 0.87rem;
  font-weight: 600;
  color: #2d2d25;
  margin: 0 0 12px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.popular-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.pf-author { font-size: 0.72rem; color: #b8b8a8; }
.pf-likes {
  font-size: 0.72rem;
  font-weight: 700;
  color: #E07070;
  display: flex;
  align-items: center;
  gap: 3px;
}

/* ── 카테고리 태그 ── */
.cat-tag {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 20px;
  letter-spacing: 0.2px;
}
.cat-FREE       { background: #f0efea; color: #6b6b5a; }
.cat-DEPOSIT    { background: #e0f2e0; color: #3a7040; }
.cat-EXCHANGE   { background: #e0e8f8; color: #3a4a8a; }
.cat-STOCK      { background: #fef0de; color: #8a5a1a; }
.cat-REALESTATE { background: #f0e0f8; color: #6a3a7a; }
.cat-QNA        { background: #fde0e0; color: #8a3a3a; }

/* ── 카테고리 탭 (언더라인) ── */
.tab-bar {
  display: flex;
  gap: 0;
  border-bottom: 2px solid #e8e7de;
  overflow-x: auto;
  scrollbar-width: none;
}
.tab-bar::-webkit-scrollbar { display: none; }
.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  font-size: 0.83rem;
  font-weight: 500;
  color: #aaa99a;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}
.tab-btn:hover { color: #5a5a4a; }

.tab-ALL.active        { color: #3d3d30; border-bottom-color: #3d3d30; font-weight: 700; }
.tab-FREE.active       { color: #6b6b5a; border-bottom-color: #6b6b5a; font-weight: 700; }
.tab-DEPOSIT.active    { color: #3a7040; border-bottom-color: #3a7040; font-weight: 700; }
.tab-EXCHANGE.active   { color: #3a4a8a; border-bottom-color: #3a4a8a; font-weight: 700; }
.tab-STOCK.active      { color: #8a5a1a; border-bottom-color: #8a5a1a; font-weight: 700; }
.tab-REALESTATE.active { color: #6a3a7a; border-bottom-color: #6a3a7a; font-weight: 700; }
.tab-QNA.active        { color: #8a3a3a; border-bottom-color: #8a3a3a; font-weight: 700; }

/* ── 검색 + 정렬 행 ── */
.search-sort-row { display: flex; align-items: center; gap: 10px; }
.search-wrap { position: relative; display: flex; align-items: center; flex: 1; }
.search-icon { position: absolute; left: 14px; color: #b0b0a0; font-size: 0.85rem; pointer-events: none; }
.search-input {
  width: 100%;
  padding: 12px 40px 12px 40px;
  font-size: 0.9rem;
  border: 1.5px solid #e8e7de;
  border-radius: 14px;
  background: #fff;
  outline: none;
  color: #2d2d25;
  transition: all 0.15s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.search-input:focus {
  border-color: #86A78A;
  box-shadow: 0 0 0 3px rgba(134,167,138,0.12);
}
.search-input::placeholder { color: #c8c7b8; }
.search-clear {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #b0b0a0;
  font-size: 0.78rem;
  cursor: pointer;
  padding: 2px;
  display: flex;
  align-items: center;
}
.search-clear:hover { color: #6b6b5a; }

/* ── 로딩 ── */
.loading-wrap { text-align: center; padding: 60px 0; }

/* ── 결과 카운트 ── */
.result-count { font-size: 0.82rem; color: #a0a090; margin: 0; }
.result-count b { color: #86A78A; }
.sort-group { display: flex; gap: 4px; flex-shrink: 0; }
.sort-btn {
  padding: 5px 13px;
  font-size: 0.78rem;
  font-weight: 500;
  color: #a0a090;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.12s;
}
.sort-btn:hover { color: #5a5a4a; background: #eeede5; }
.sort-btn.active { color: #3d6b42; font-weight: 700; background: #e8f2e9; border-color: #b8d8ba; }

/* ── 게시글 목록 ── */
.post-list { display: flex; flex-direction: column; gap: 8px; }
.post-card {
  background: #fff;
  border-radius: 16px;
  padding: 18px 22px;
  cursor: pointer;
  border: 1.5px solid #edecea;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.18s;
}
.post-card:hover {
  border-color: #86A78A;
  box-shadow: 0 6px 20px rgba(107,158,112,0.12);
  transform: translateY(-1px);
}
.pc-left { flex: 1; min-width: 0; }
.pc-meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.pc-date { font-size: 0.74rem; color: #c0bfb0; }
.pc-title {
  font-size: 0.97rem;
  font-weight: 700;
  color: #2d2d25;
  margin: 0 0 6px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}
.pc-preview {
  font-size: 0.82rem;
  color: #b0b0a0;
  margin: 0 0 10px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
  white-space: pre-wrap;
}
.pc-bottom-row { display: flex; align-items: center; justify-content: space-between; }
.pc-author-row { display: flex; align-items: center; gap: 6px; }
.avatar { width: 20px; height: 20px; border-radius: 50%; object-fit: cover; }
.pc-author { font-size: 0.78rem; color: #aaa99a; font-weight: 500; }
.pc-stats { display: flex; align-items: center; gap: 10px; }
.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  color: #c4c3b4;
}
.stat-item i { font-size: 0.7rem; }
.stat-item.heart { color: #dba8a8; }
.stat-item.chat  { color: #a8c0a8; }
.stat-item.view  { color: #c4c3b4; }

/* ── 빈 상태 ── */
.empty-state {
  text-align: center;
  padding: 80px 0 60px;
}
.empty-state i {
  font-size: 3rem;
  display: block;
  margin-bottom: 14px;
  color: #d4d3c4;
}
.empty-state p { font-size: 0.9rem; color: #c0bfb0; margin-bottom: 20px; }
.empty-write-btn {
  display: inline-block;
  padding: 10px 26px;
  background: #86A78A;
  color: #fff;
  border-radius: 50px;
  font-size: 0.88rem;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.15s;
  box-shadow: 0 4px 12px rgba(107,158,112,0.3);
}
.empty-write-btn:hover { background: #6e9272; transform: translateY(-1px); color: #fff; }
</style>

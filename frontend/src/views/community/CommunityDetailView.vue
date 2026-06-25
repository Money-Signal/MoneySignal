<template>
  <div class="page-wrap">
    <div class="container py-4" style="max-width: 780px;">

      <!-- 로딩 -->
      <div v-if="store.isLoading" class="loading-wrap">
        <div class="spinner-border" style="color:#86A78A" role="status" />
      </div>

      <!-- 에러 -->
      <div v-else-if="store.error" class="alert alert-danger">{{ store.error }}</div>

      <template v-else-if="store.post">

        <!-- 뒤로가기 -->
        <button class="back-btn mb-4" @click="router.push({ name: 'communityList' })">
          <i class="bi bi-arrow-left me-1" />목록으로
        </button>

        <!-- 게시글 본문 -->
        <div class="post-box">

          <!-- 카테고리 + 제목 -->
          <div class="post-headline">
            <span :class="['cat-tag', `cat-${store.post.category}`]">{{ categoryLabel(store.post.category) }}</span>
            <h2 class="post-title">{{ store.post.title }}</h2>
          </div>

          <!-- 작성자 정보 + 수정/삭제 -->
          <div class="post-meta-row">
            <div class="author-info">
              <img :src="getAvatarUrl(store.post.author_image)" class="avatar" alt="프로필" @error="$event.target.src = defaultAvatar" />
              <div class="author-text">
                <span class="author-name">{{ store.post.author_nickname }}</span>
                <div class="post-info-row">
                  <span class="post-date">{{ formatDate(store.post.created_at) }}</span>
                  <span class="view-count"><i class="bi bi-eye" />{{ store.post.view_count }}</span>
                </div>
              </div>
            </div>
            <div v-if="isAuthor" class="action-group">
              <button class="action-btn" @click="router.push({ name: 'communityWrite', query: { id: store.post.id } })">
                <i class="bi bi-pencil me-1" />수정
              </button>
              <button class="action-btn danger" @click="onDelete">
                <i class="bi bi-trash me-1" />삭제
              </button>
            </div>
          </div>

          <div class="divider" />

          <!-- 본문 -->
          <p class="post-content">{{ store.post.content }}</p>

          <!-- 첨부 이미지 -->
          <div v-if="store.post.image" class="post-image-wrap">
            <img :src="getImageUrl(store.post.image)" class="post-image" alt="첨부 이미지" />
          </div>

          <!-- 좋아요 -->
          <div class="like-area">
            <button :class="['like-btn', store.post.is_liked ? 'liked' : '']" @click="onLike">
              <i :class="store.post.is_liked ? 'bi bi-heart-fill' : 'bi bi-heart'" />
              <span>{{ store.post.like_count }}</span>
              <span class="like-label">{{ store.post.is_liked ? '좋아요 취소' : '좋아요' }}</span>
            </button>
          </div>
        </div>

        <!-- 댓글 섹션 -->
        <div class="comment-section">

          <!-- 댓글 헤더 -->
          <div class="comment-header-row">
            <span class="comment-count-label">
              <i class="bi bi-chat me-1" />댓글 {{ store.post.comments.length }}
            </span>
          </div>

          <!-- 댓글 없음 -->
          <div v-if="store.post.comments.length === 0" class="no-comment">
            <i class="bi bi-chat-dots" />
            <p>첫 댓글을 남겨보세요!</p>
          </div>

          <!-- 댓글 목록 -->
          <div
            v-for="comment in store.post.comments"
            :key="comment.id"
            class="comment-item"
          >
            <img :src="getAvatarUrl(comment.author_image)" class="avatar-sm" alt="프로필" @error="$event.target.src = defaultAvatar" />
            <div class="comment-body">
              <div class="comment-meta">
                <span class="comment-author">{{ comment.author_nickname }}</span>
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                <button
                  v-if="authStore.user?.nickname === comment.author_nickname"
                  class="comment-delete-btn"
                  @click="onCommentDelete(comment.id)"
                >삭제</button>
              </div>
              <p class="comment-content">{{ comment.content }}</p>
            </div>
          </div>

          <!-- 댓글 입력 -->
          <div v-if="authStore.isLoggedIn" class="comment-form">
            <img :src="getAvatarUrl(authStore.user?.profile_image)" class="avatar-sm" alt="내 프로필" @error="$event.target.src = defaultAvatar" />
            <div class="comment-input-wrap">
              <textarea
                v-model="commentContent"
                class="comment-input"
                placeholder="댓글을 입력하세요."
                rows="2"
                @input="autoGrow($event.target)"
              />
              <div class="comment-form-footer">
                <span class="char-count">{{ commentContent.length }} / 500</span>
                <button class="submit-btn" :disabled="!commentContent.trim()" @click="onCommentSubmit">
                  등록
                </button>
              </div>
            </div>
          </div>
          <p v-else class="login-nudge">
            <RouterLink to="/login">로그인</RouterLink> 후 댓글을 작성할 수 있어요.
          </p>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useCommunityStore } from '@/stores/community'
import { useAuthStore } from '@/stores/auth'
import { useAlert } from '@/composables/useAlert'

const {confirm} = useAlert()

const router    = useRouter()
const route     = useRoute()
const store     = useCommunityStore()
const authStore = useAuthStore()

const commentContent = ref('')

const CATEGORY_MAP = {
  FREE: '자유', DEPOSIT: '예금·적금', EXCHANGE: '환율·해외',
  STOCK: '주식·ETF', REALESTATE: '부동산', QNA: '질문',
}
const categoryLabel = (value) => CATEGORY_MAP[value] ?? value
const BACKEND_URL   = 'http://127.0.0.1:8000'
const defaultAvatar = 'https://ui-avatars.com/api/?background=86A78A&color=fff&size=64'

function getAvatarUrl(img) {
  if (!img) return defaultAvatar
  return img.startsWith('http') ? img : `${BACKEND_URL}${img}`
}

function getImageUrl(img) {
  if (!img) return ''
  return img.startsWith('http') ? img : `${BACKEND_URL}${img}`
}

const isAuthor = computed(() =>
  authStore.isLoggedIn && authStore.user?.nickname === store.post?.author_nickname
)

onMounted(() => {
  store.fetchPost(route.params.id)
})

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

function autoGrow(el) {
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

async function onLike() {
  if (!authStore.isLoggedIn) {
    router.push({ name: 'login' })
    return
  }
  await store.likePost(store.post.id)
}

async function onDelete() {
  const result = await confirm('게시글을 삭제할까요?', '게시글 삭제', {
    confirmText: '삭제',
    cancelText: '취소'
  })
  if (!result) return
  await store.removePost(store.post.id)
  router.push({ name: 'communityList' })
}

async function onCommentSubmit() {
  if (!commentContent.value.trim()) return
  await store.submitComment(store.post.id, commentContent.value)
  commentContent.value = ''
}

async function onCommentDelete(commentId) {
  const result = await confirm('댓글을 삭제할까요?', '댓글 삭제', {
    confirmText: '삭제',
    cancelText: '취소'
  })
  if (!result) return
  await store.removeComment(store.post.id, commentId)
}
</script>

<style scoped>
.page-wrap {
  min-height: 100vh;
  background: #f9f8f5;
}

/* ── 로딩 ── */
.loading-wrap { text-align: center; padding: 80px 0; }

/* ── 뒤로가기 ── */
.back-btn {
  display: inline-flex;
  align-items: center;
  background: #fff;
  border: 1.5px solid #e8e7de;
  color: #6b8a6e;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  padding: 7px 14px;
  border-radius: 50px;
  transition: all 0.15s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.back-btn:hover {
  background: #f0f7f0;
  border-color: #86A78A;
  color: #4a6e4e;
}

/* ── 게시글 박스 ── */
.post-box {
  background: #fff;
  border-radius: 20px;
  padding: 32px 32px 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  border: 1px solid #edecea;
  margin-bottom: 16px;
}

/* ── 카테고리 태그 ── */
.cat-tag {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.2px;
  margin-bottom: 12px;
}
.cat-FREE       { background: #f0efea; color: #6b6b5a; }
.cat-DEPOSIT    { background: #e0f2e0; color: #3a7040; }
.cat-EXCHANGE   { background: #e0e8f8; color: #3a4a8a; }
.cat-STOCK      { background: #fef0de; color: #8a5a1a; }
.cat-REALESTATE { background: #f0e0f8; color: #6a3a7a; }
.cat-QNA        { background: #fde0e0; color: #8a3a3a; }

/* ── 헤드라인 ── */
.post-headline { margin-bottom: 18px; }
.post-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #1e1e18;
  line-height: 1.4;
  margin: 0;
  letter-spacing: -0.3px;
}

/* ── 메타 행 ── */
.post-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.author-info { display: flex; align-items: center; gap: 10px; }
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #edecea;
}
.author-text { display: flex; flex-direction: column; gap: 2px; }
.author-name { font-size: 0.88rem; font-weight: 700; color: #3a3a30; }
.post-info-row { display: flex; align-items: center; gap: 10px; }
.post-date   { font-size: 0.75rem; color: #b0b0a0; }
.view-count  { font-size: 0.75rem; color: #b0b0a0; display: flex; align-items: center; gap: 4px; }

/* ── 수정/삭제 ── */
.action-group { display: flex; gap: 8px; }
.action-btn {
  font-size: 0.78rem;
  padding: 6px 14px;
  border-radius: 50px;
  border: 1.5px solid #e0dfd0;
  background: #fff;
  color: #6b6b5a;
  cursor: pointer;
  transition: all 0.15s;
  font-weight: 500;
}
.action-btn:hover { background: #f8f7f2; border-color: #c8c7b8; }
.action-btn.danger { border-color: #ecc0c0; color: #c07070; }
.action-btn.danger:hover { background: #fdf4f4; border-color: #e09090; }

/* ── 구분선 ── */
.divider {
  height: 1px;
  background: linear-gradient(to right, #f0efea, #e8e7de, #f0efea);
  margin-bottom: 24px;
}

/* ── 본문 ── */
.post-content {
  font-size: 0.97rem;
  color: #4a4a4a;
  line-height: 1.9;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
  margin-bottom: 24px;
  min-height: 80px;
}

/* ── 첨부 이미지 ── */
.post-image-wrap {
  margin-bottom: 24px;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid #edecea;
}
.post-image {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  display: block;
}

/* ── 좋아요 영역 ── */
.like-area {
  display: flex;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #f0efea;
}
.like-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 28px;
  border-radius: 50px;
  border: 2px solid #e8e7de;
  background: #fafaf6;
  font-size: 0.9rem;
  font-weight: 600;
  color: #a0a090;
  cursor: pointer;
  transition: all 0.2s;
}
.like-btn:hover { border-color: #e08080; color: #e07070; background: #fef5f5; }
.like-btn.liked {
  border-color: #e08080;
  color: #d06060;
  background: linear-gradient(135deg, #fef0f0, #fdf5f5);
  box-shadow: 0 4px 14px rgba(220,100,100,0.15);
}
.like-btn i { font-size: 1rem; }
.like-label { font-size: 0.8rem; color: inherit; }

/* ── 댓글 섹션 ── */
.comment-section {
  background: #fff;
  border-radius: 20px;
  padding: 24px 32px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  border: 1px solid #edecea;
}
.comment-header-row {
  padding-bottom: 16px;
  border-bottom: 1.5px solid #f0efea;
  margin-bottom: 8px;
}
.comment-count-label {
  font-size: 0.92rem;
  font-weight: 700;
  color: #3a3a30;
}

/* ── 댓글 없음 ── */
.no-comment {
  text-align: center;
  padding: 28px 0;
  color: #c8c7b8;
}
.no-comment i { font-size: 1.6rem; display: block; margin-bottom: 8px; }
.no-comment p { font-size: 0.85rem; margin: 0; }

/* ── 댓글 아이템 ── */
.comment-item {
  display: flex;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid #f5f4ef;
}
.avatar-sm {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  border: 1.5px solid #edecea;
  margin-top: 2px;
}
.comment-body { flex: 1; min-width: 0; }
.comment-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.comment-author { font-size: 0.82rem; font-weight: 700; color: #3a3a30; }
.comment-date   { font-size: 0.74rem; color: #c0bfb0; }
.comment-delete-btn {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 0.72rem;
  color: #c0a0a0;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.12s;
}
.comment-delete-btn:hover { color: #e07070; background: #fdf4f4; }
.comment-content {
  font-size: 0.88rem;
  color: #5a5a4a;
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.65;
}

/* ── 댓글 입력 ── */
.comment-form {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1.5px solid #f0efea;
}
.comment-input-wrap {
  flex: 1;
  border: 1.5px solid #e0dfd0;
  border-radius: 14px;
  overflow: hidden;
  transition: all 0.15s;
}
.comment-input-wrap:focus-within {
  border-color: #86A78A;
  box-shadow: 0 0 0 3px rgba(134,167,138,0.1);
}
.comment-input {
  width: 100%;
  padding: 12px 14px;
  font-size: 0.88rem;
  border: none;
  resize: none;
  outline: none;
  overflow: hidden;
  min-height: 60px;
  color: #3a3a30;
  background: #fff;
  line-height: 1.6;
}
.comment-form-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #fafaf6;
  border-top: 1px solid #f0efea;
}
.char-count { font-size: 0.74rem; color: #c0bfb0; }
.submit-btn {
  padding: 6px 18px;
  background: #86A78A;
  color: #fff;
  border: none;
  border-radius: 50px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
}
.submit-btn:hover { background: #6e9272; }
.submit-btn:disabled { background: #c8d9c9; cursor: not-allowed; }

/* ── 로그인 유도 ── */
.login-nudge {
  font-size: 0.85rem;
  color: #a0a090;
  text-align: center;
  padding: 20px 0 4px;
  border-top: 1.5px solid #f0efea;
  margin-top: 20px;
}
.login-nudge a { color: #86A78A; font-weight: 700; text-decoration: none; }
.login-nudge a:hover { text-decoration: underline; }
</style>

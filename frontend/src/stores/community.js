import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getPosts, getPost, createPost, updatePost, deletePost,
  togglePostLike, createComment, deleteComment,
} from '@/api/community'

export const useCommunityStore = defineStore('community', () => {
  const posts    = ref([])   // 게시글 목록
  const post     = ref(null) // 게시글 상세
  const isLoading = ref(false)
  const error     = ref(null)

  // 게시글 목록 불러오기 (category 없으면 전체 조회)
  async function fetchPosts(category = '') {
    isLoading.value = true
    error.value = null
    try {
      const { data } = await getPosts(category)
      posts.value = data
    } catch (e) {
      error.value = '게시글을 불러오지 못했습니다.'
    } finally {
      isLoading.value = false
    }
  }

  // 게시글 상세 불러오기
  async function fetchPost(postId) {
    isLoading.value = true
    error.value = null
    try {
      const { data } = await getPost(postId)
      post.value = data
    } catch (e) {
      error.value = '게시글을 불러오지 못했습니다.'
    } finally {
      isLoading.value = false
    }
  }

  // 게시글 작성 - 성공 시 작성된 게시글 id 반환
  async function submitPost(formData) {
    const { data } = await createPost(formData)
    return data.id
  }

  // 게시글 수정
  async function editPost(postId, formData) {
    await updatePost(postId, formData)
  }

  // 게시글 삭제
  async function removePost(postId) {
    await deletePost(postId)
  }

  // 좋아요 토글 - 상세 페이지의 like_count, is_liked 즉시 반영
  async function likePost(postId) {
    const { data } = await togglePostLike(postId)
    if (post.value && post.value.id === postId) {
      post.value.like_count = data.like_count
      post.value.is_liked   = data.liked
    }
  }

  // 댓글 작성 - 성공 시 상세 데이터 재조회로 댓글 목록 갱신
  async function submitComment(postId, content) {
    await createComment(postId, { content })
    await fetchPost(postId)
  }

  // 댓글 삭제 - 성공 시 상세 데이터 재조회로 댓글 목록 갱신
  async function removeComment(postId, commentId) {
    await deleteComment(commentId)
    await fetchPost(postId)
  }

  return {
    posts, post, isLoading, error,
    fetchPosts, fetchPost, submitPost, editPost, removePost,
    likePost, submitComment, removeComment,
  }
})

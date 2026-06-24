<template>
  <div class="page-wrap">

    <div class="container main-content" style="max-width: 780px;">
      <div class="page-header">
        <h2 class="page-title">{{ isEdit ? '게시글 수정' : '게시글 작성' }}</h2>
        <p class="page-sub">{{ isEdit ? '내용을 수정하고 완료 버튼을 눌러주세요.' : '커뮤니티에 글을 남겨보세요.' }}</p>
      </div>
      <div class="write-box">

        <!-- 카테고리 선택 -->
        <div class="field-group">
          <label class="field-label">카테고리</label>
          <div class="category-wrap">
            <label
              v-for="opt in categoryOptions"
              :key="opt.value"
              :class="['cat-option', form.category === opt.value ? 'selected' : '']"
            >
              <input type="radio" v-model="form.category" :value="opt.value" class="cat-radio" />
              {{ opt.label }}
            </label>
          </div>
        </div>

        <!-- 제목 -->
        <div class="field-group">
          <label class="field-label">제목</label>
          <input
            v-model="form.title"
            type="text"
            class="title-input"
            placeholder="제목을 입력하세요."
            maxlength="200"
          />
          <div class="char-hint">{{ form.title.length }} / 200</div>
        </div>

        <!-- 내용 -->
        <div class="field-group">
          <label class="field-label">내용</label>
          <textarea
            v-model="form.content"
            class="content-input"
            placeholder="내용을 입력하세요."
            rows="14"
          />
        </div>

        <!-- 이미지 첨부 -->
        <div class="field-group">
          <label class="field-label">이미지 첨부 <span class="optional">(선택)</span></label>

          <!-- 업로드 유도 영역 -->
          <div v-if="!imagePreview" class="upload-area" @click="fileInput.click()" @dragover.prevent @drop.prevent="onDrop">
            <div class="upload-icon-wrap">
              <i class="bi bi-cloud-arrow-up" />
            </div>
            <p class="upload-title">클릭하거나 이미지를 끌어다 놓으세요</p>
            <span class="upload-hint">JPG, PNG, GIF · 최대 5MB</span>
          </div>

          <!-- 미리보기 -->
          <div v-else class="preview-wrap">
            <img :src="imagePreview" class="preview-img" alt="첨부 이미지 미리보기" />
            <button class="remove-img-btn" @click="removeImage" title="이미지 제거">
              <i class="bi bi-x-lg" />
            </button>
          </div>

          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            style="display:none"
            @change="onFileChange"
          />
        </div>

        <!-- 버튼 -->
        <div class="btn-row">
          <button class="cancel-btn" @click="router.back()">
            <i class="bi bi-x-lg me-1" />취소
          </button>
          <button
            class="submit-btn"
            :disabled="!form.title.trim() || !form.content.trim()"
            @click="onSubmit"
          >
            <i :class="isEdit ? 'bi bi-check-lg me-1' : 'bi bi-send me-1'" />
            {{ isEdit ? '수정 완료' : '작성 완료' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCommunityStore } from '@/stores/community'

const router = useRouter()
const route  = useRoute()
const store  = useCommunityStore()

const isEdit = computed(() => !!route.query.id)

const categoryOptions = [
  { value: 'FREE',       label: '자유' },
  { value: 'DEPOSIT',    label: '예금·적금' },
  { value: 'EXCHANGE',   label: '환율·해외' },
  { value: 'STOCK',      label: '주식·ETF' },
  { value: 'REALESTATE', label: '부동산' },
  { value: 'QNA',        label: '질문' },
]

const form = ref({ category: 'FREE', title: '', content: '' })
const imageFile    = ref(null)
const imagePreview = ref(null)
const fileInput    = ref(null)

onMounted(async () => {
  if (isEdit.value) {
    await store.fetchPost(route.query.id)
    form.value.category = store.post.category
    form.value.title    = store.post.title
    form.value.content  = store.post.content
    if (store.post.image) {
      const BACKEND_URL = 'http://127.0.0.1:8000'
      const img = store.post.image
      imagePreview.value = img.startsWith('http') ? img : `${BACKEND_URL}${img}`
    }
  }
})

function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  setImage(file)
}

function onDrop(e) {
  const file = e.dataTransfer.files[0]
  if (!file || !file.type.startsWith('image/')) return
  setImage(file)
}

function setImage(file) {
  imageFile.value    = file
  imagePreview.value = URL.createObjectURL(file)
}

function removeImage() {
  imageFile.value    = null
  imagePreview.value = null
  if (fileInput.value) fileInput.value.value = ''
}

async function onSubmit() {
  if (!form.value.title.trim() || !form.value.content.trim()) return

  const formData = new FormData()
  formData.append('category', form.value.category)
  formData.append('title',    form.value.title)
  formData.append('content',  form.value.content)
  if (imageFile.value) {
    formData.append('image', imageFile.value)
  }

  if (isEdit.value) {
    await store.editPost(route.query.id, formData)
    router.push({ name: 'communityDetail', params: { id: route.query.id } })
  } else {
    await store.submitPost(formData)
    router.push({ name: 'communityList' })
  }
}
</script>

<style scoped>
.page-wrap {
  min-height: 100vh;
  background: #F5F4EE;
}

/* ── 페이지 헤더 ── */
.page-header { margin-bottom: 20px; }
.page-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: #2d2d25;
  margin-bottom: 4px;
  letter-spacing: -0.3px;
}
.page-sub {
  font-size: 0.86rem;
  color: #a0a090;
  margin: 0;
}

/* ── 메인 콘텐츠 ── */
.main-content { padding-top: 28px; padding-bottom: 48px; }

/* ── 작성 박스 ── */
.write-box {
  background: #fff;
  border-radius: 20px;
  padding: 32px 32px 28px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  border: 1px solid #edecea;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

/* ── 필드 그룹 ── */
.field-group { display: flex; flex-direction: column; gap: 8px; }
.field-label {
  font-size: 0.82rem;
  font-weight: 700;
  color: #5a5a4a;
  letter-spacing: 0.3px;
}
.optional {
  font-size: 0.75rem;
  font-weight: 400;
  color: #b0b0a0;
}

/* ── 카테고리 라디오 ── */
.category-wrap { display: flex; flex-wrap: wrap; gap: 8px; }
.cat-radio { display: none; }
.cat-option {
  padding: 7px 16px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #6b6b5a;
  background: #f8f7f2;
  border: 1.5px solid #e8e7de;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
}
.cat-option:hover { border-color: #86A78A; color: #3d6b42; }
.cat-option.selected {
  background: #86A78A;
  color: #fff;
  border-color: #86A78A;
  box-shadow: 0 3px 10px rgba(107,158,112,0.3);
}

/* ── 제목 입력 ── */
.title-input {
  width: 100%;
  padding: 13px 16px;
  font-size: 1rem;
  font-weight: 600;
  border: 1.5px solid #e0dfd0;
  border-radius: 12px;
  outline: none;
  transition: all 0.15s;
  color: #2d2d25;
  background: #fff;
}
.title-input:focus {
  border-color: #86A78A;
  box-shadow: 0 0 0 3px rgba(134,167,138,0.1);
}
.title-input::placeholder { color: #c8c7b8; font-weight: 400; }
.char-hint { font-size: 0.74rem; color: #c8c7b8; text-align: right; }

/* ── 내용 입력 ── */
.content-input {
  width: 100%;
  padding: 13px 16px;
  font-size: 0.93rem;
  border: 1.5px solid #e0dfd0;
  border-radius: 12px;
  outline: none;
  resize: vertical;
  line-height: 1.75;
  transition: all 0.15s;
  color: #4a4a4a;
  background: #fff;
  min-height: 200px;
}
.content-input:focus {
  border-color: #86A78A;
  box-shadow: 0 0 0 3px rgba(134,167,138,0.1);
}
.content-input::placeholder { color: #c8c7b8; }

/* ── 업로드 영역 ── */
.upload-area {
  border: 2px dashed #d8d7ce;
  border-radius: 14px;
  padding: 36px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.18s;
  background: #fafaf6;
}
.upload-area:hover {
  border-color: #86A78A;
  background: #f2f8f3;
}
.upload-icon-wrap {
  width: 52px;
  height: 52px;
  background: #f0f7f1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}
.upload-icon-wrap i {
  font-size: 1.5rem;
  color: #86A78A;
}
.upload-title {
  font-size: 0.88rem;
  font-weight: 600;
  color: #5a5a4a;
  margin: 0 0 4px;
}
.upload-hint { font-size: 0.78rem; color: #b8b8a8; }

/* ── 이미지 미리보기 ── */
.preview-wrap {
  position: relative;
  display: inline-block;
  width: 100%;
  border-radius: 14px;
  overflow: hidden;
  border: 1.5px solid #edecea;
}
.preview-img {
  width: 100%;
  max-height: 380px;
  object-fit: cover;
  display: block;
}
.remove-img-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.55);
  color: #fff;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  backdrop-filter: blur(4px);
}
.remove-img-btn:hover { background: rgba(0,0,0,0.75); }

/* ── 버튼 행 ── */
.btn-row {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 6px;
  border-top: 1px solid #f0efea;
}
.cancel-btn {
  padding: 10px 20px;
  border: 1.5px solid #e0dfd0;
  border-radius: 50px;
  background: #fff;
  color: #6b6b5a;
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.cancel-btn:hover { background: #f5f5ec; border-color: #c8c7b8; }
.submit-btn {
  padding: 10px 26px;
  background: #86A78A;
  color: #fff;
  border: none;
  border-radius: 50px;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 4px 12px rgba(107,158,112,0.3);
}
.submit-btn:hover { background: #6e9272; transform: translateY(-1px); box-shadow: 0 6px 16px rgba(107,158,112,0.35); }
.submit-btn:disabled { background: #c8d9c9; cursor: not-allowed; box-shadow: none; transform: none; }
</style>

<template>
  <!-- 플로팅 버튼 -->
  <button class="chat-fab" @click="toggleChat" :class="{ open: isOpen }" aria-label="챗봇 열기">
    <i v-if="!isOpen" class="bi bi-chat-dots-fill"></i>
    <i v-else class="bi bi-x-lg"></i>
  </button>

  <!-- 챗 윈도우 -->
  <Transition name="chat-pop">
    <div v-if="isOpen" class="chat-window">

      <!-- 헤더 -->
      <div class="chat-header">
        <div class="chat-header-info">
          <div class="chat-avatar">S</div>
          <div>
            <p class="chat-name">Signal</p>
            <p class="chat-status">MoneySignal 금융 도우미</p>
          </div>
        </div>
        <button class="chat-close" @click="toggleChat">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <!-- 메시지 영역 -->
      <div class="chat-messages" ref="messagesEl">
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="chat-msg"
          :class="msg.role"
        >
          <div v-if="msg.role === 'assistant'" class="msg-avatar">S</div>
          <div class="msg-bubble" v-html="formatMessage(msg.content)"></div>
        </div>

        <!-- 로딩 -->
        <div v-if="loading" class="chat-msg assistant">
          <div class="msg-avatar">S</div>
          <div class="msg-bubble loading-bubble">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <!-- 빠른 질문 -->
      <div v-if="messages.length === 1" class="quick-btns">
        <button
          v-for="q in quickQuestions"
          :key="q"
          class="quick-btn"
          @click="sendQuick(q)"
        >{{ q }}</button>
      </div>

      <!-- 입력창 -->
      <div class="chat-input-wrap">
        <input
          v-model="inputText"
          class="chat-input"
          placeholder="질문을 입력하세요..."
          @keydown.enter="sendMessage"
          :disabled="loading"
        />
        <button class="chat-send" @click="sendMessage" :disabled="loading || !inputText.trim()">
          <i class="bi bi-send-fill"></i>
        </button>
      </div>

    </div>
  </Transition>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from 'axios'

const isOpen = ref(false)
const inputText = ref('')
const loading = ref(false)
const messagesEl = ref(null)

const quickQuestions = [
  '어떤 서비스를 제공해?',
  '금리 높은 예금 추천해줘',
  '적금 상품 뭐가 있어?',
]

const messages = ref([
  {
    role: 'assistant',
    content: '안녕하세요! 저는 MoneySignal의 금융 도우미 Signal이에요 😊 예적금 상품 추천이나 서비스 안내가 필요하시면 말씀해 주세요!',
  },
])

const toggleChat = () => {
  isOpen.value = !isOpen.value
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

const formatMessage = (text) => {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
}

const sendQuick = (question) => {
  inputText.value = question
  sendMessage()
}

const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const res = await axios.post('http://localhost:8000/api/chatbot/', { message: text })
    messages.value.push({ role: 'assistant', content: res.data.answer })
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: '죄송해요, 잠시 문제가 생겼어요. 다시 시도해 주세요 🙏',
    })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}
</script>

<style scoped>
/* 플로팅 버튼 */
.chat-fab {
  position: fixed;
  bottom: 28px;
  right: 28px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #6A7F5A;
  color: #fff;
  border: none;
  cursor: pointer;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(106, 127, 90, 0.35);
  z-index: 1000;
  transition: background 0.2s, transform 0.2s;
}
.chat-fab:hover { background: #5a6e4c; transform: scale(1.06); }
.chat-fab.open { background: #888; }

/* 챗 윈도우 */
.chat-window {
  position: fixed;
  bottom: 90px;
  right: 28px;
  width: 460px;
  max-height: 700px;
  height: 700px;
  background: #fff;
  border-radius: 18px;
  border: 0.5px solid #e8e6e0;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  z-index: 999;
  overflow: hidden;
}

/* 헤더 */
.chat-header {
  background: #6A7F5A;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}
.chat-header-info { display: flex; align-items: center; gap: 10px; }
.chat-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(255,255,255,0.25);
  color: #fff;
  font-size: 15px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}
.chat-name { font-size: 14px; font-weight: 700; color: #fff; }
.chat-status { font-size: 11px; color: rgba(255,255,255,0.75); margin-top: 1px; }
.chat-close {
  background: none;
  border: none;
  color: rgba(255,255,255,0.8);
  font-size: 14px;
  cursor: pointer;
  padding: 4px;
}
.chat-close:hover { color: #fff; }

/* 메시지 영역 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}
.chat-msg {
  display: flex;
  align-items: flex-end;
  gap: 7px;
}
.chat-msg.user { flex-direction: row-reverse; }

.msg-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #6A7F5A;
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.msg-bubble {
  max-width: 300px;
  padding: 9px 13px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.6;
  word-break: break-word;
}
.assistant .msg-bubble {
  background: #f5f4f0;
  color: #1a1a1a;
  border-bottom-left-radius: 4px;
}
.user .msg-bubble {
  background: #6A7F5A;
  color: #fff;
  border-bottom-right-radius: 4px;
}

/* 로딩 점 */
.loading-bubble {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
}
.loading-bubble span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #aaa;
  animation: bounce 1.2s infinite ease-in-out;
}
.loading-bubble span:nth-child(2) { animation-delay: 0.2s; }
.loading-bubble span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-6px); }
}

/* 빠른 질문 */
.quick-btns {
  padding: 0 14px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex-shrink: 0;
}
.quick-btn {
  background: #f0f4f0;
  border: 0.5px solid #d4e0d4;
  border-radius: 20px;
  padding: 7px 14px;
  font-size: 12px;
  color: #6A7F5A;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}
.quick-btn:hover { background: #e4ede4; }

/* 입력창 */
.chat-input-wrap {
  padding: 10px 12px;
  border-top: 0.5px solid #eee;
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}
.chat-input {
  flex: 1;
  border: 0.5px solid #e0ddd5;
  border-radius: 20px;
  padding: 8px 14px;
  font-size: 13px;
  outline: none;
  background: #fafaf8;
  transition: border-color 0.15s;
}
.chat-input:focus { border-color: #6A7F5A; }
.chat-input:disabled { opacity: 0.6; }

.chat-send {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #6A7F5A;
  color: #fff;
  border: none;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  flex-shrink: 0;
}
.chat-send:hover:not(:disabled) { background: #5a6e4c; }
.chat-send:disabled { background: #ccc; cursor: default; }

/* 애니메이션 */
.chat-pop-enter-active { animation: popIn 0.22s ease; }
.chat-pop-leave-active { animation: popIn 0.18s ease reverse; }
@keyframes popIn {
  from { opacity: 0; transform: translateY(12px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
</style>
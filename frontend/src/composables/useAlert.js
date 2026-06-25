import { ref } from 'vue'

const isVisible = ref(false)
const modalTitle = ref('')
const modalMessage = ref('')
const modalType = ref('alert') // 'alert' | 'confirm'
const modalConfirmText = ref('확인')
const modalCancelText = ref('취소')

let resolvePromise = null

export function useAlert() {
  const alert = (message, title = '알림') => {
    modalTitle.value = title
    modalMessage.value = message
    modalType.value = 'alert'
    modalConfirmText.value = '확인'
    isVisible.value = true

    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  const confirm = (message, title = '확인', { confirmText = '확인', cancelText = '취소' } = {}) => {
    modalTitle.value = title
    modalMessage.value = message
    modalType.value = 'confirm'
    modalConfirmText.value = confirmText
    modalCancelText.value = cancelText
    isVisible.value = true

    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  const success = (message, title = '완료') => {
  modalTitle.value = title
  modalMessage.value = message
  modalType.value = 'success'
  modalConfirmText.value = '확인'
  isVisible.value = true

  return new Promise((resolve) => {
    resolvePromise = resolve
  })
}

  const onConfirm = () => {
    isVisible.value = false
    resolvePromise?.(true)
  }

  const onCancel = () => {
    isVisible.value = false
    resolvePromise?.(false)
  }

  const successConfetti = (message, title = '완료') => {
  modalTitle.value = title
  modalMessage.value = message
  modalType.value = 'successConfetti'  // 새 타입
  modalConfirmText.value = '확인'
  isVisible.value = true

  return new Promise((resolve) => {
    resolvePromise = resolve
  })
}

  return {
    isVisible,
    modalTitle,
    modalMessage,
    modalType,
    modalConfirmText,
    modalCancelText,
    alert,
    confirm,
    onConfirm,
    onCancel,
    success,
    successConfetti,
  }
}
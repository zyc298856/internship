<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../services/api'

const router = useRouter()
const sessions = ref<any[]>([])
const currentSessionId = ref<number | null>(null)
const messages = ref<any[]>([])

const inputText = ref('')
const inputImage = ref<File | null>(null)
const inputImageUrl = ref('')
const loading = ref(false)

const messagesContainer = ref<HTMLElement | null>(null)

const fetchSessions = async () => {
  try {
    const res = await api.get('/chat/sessions')
    sessions.value = res.data
    if (sessions.value.length > 0 && !currentSessionId.value) {
      selectSession(sessions.value[0].id)
    }
  } catch (err) {
    ElMessage.error('Failed to load sessions')
  }
}

const createSession = async () => {
  try {
    const formData = new FormData()
    formData.append('title', `Chat ${sessions.value.length + 1}`)
    const res = await api.post('/chat/sessions', formData)
    sessions.value.unshift(res.data)
    selectSession(res.data.id)
  } catch (err) {
    ElMessage.error('Failed to create session')
  }
}

const selectSession = async (id: number) => {
  currentSessionId.value = id
  await fetchMessages(id)
}

const deleteSession = async (id: number, event: Event) => {
  event.stopPropagation()
  try {
    await ElMessageBox.confirm('Are you sure you want to delete this chat session?', 'Warning', {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })
    
    await api.delete(`/chat/sessions/${id}`)
    ElMessage.success('Session deleted')
    
    sessions.value = sessions.value.filter(s => s.id !== id)
    
    if (currentSessionId.value === id) {
      if (sessions.value.length > 0) {
        selectSession(sessions.value[0].id)
      } else {
        currentSessionId.value = null
        messages.value = []
      }
    }
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('Failed to delete session')
    }
  }
}

const fetchMessages = async (id: number) => {
  try {
    const res = await api.get(`/chat/sessions/${id}/messages`)
    messages.value = res.data.map((m: any) => formatMessage(m))
    scrollToBottom()
  } catch (err) {
    ElMessage.error('Failed to load messages')
  }
}

const formatMessage = (m: any) => {
  // Check if content has image bracket format: [image_url]\nrest_of_text
  let text = m.content
  let image = null
  if (text.startsWith('[') && text.includes(']\n')) {
    const splitIndex = text.indexOf(']\n')
    image = text.substring(1, splitIndex)
    text = text.substring(splitIndex + 2)
  }
  return { ...m, display_text: text, image_url: image }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    inputImage.value = target.files[0]
    inputImageUrl.value = URL.createObjectURL(target.files[0])
  }
}

const removeImage = () => {
  inputImage.value = null
  inputImageUrl.value = ''
}

const sendMessage = async () => {
  if (!inputText.value.trim() && !inputImage.value && !inputImageUrl.value) return
  if (!currentSessionId.value) {
     await createSession()
  }

  const sid = currentSessionId.value
  const formData = new FormData()
  formData.append('text', inputText.value)
  if (inputImage.value) {
    formData.append('image', inputImage.value)
  } else if (inputImageUrl.value && !inputImageUrl.value.startsWith('blob:')) {
    formData.append('image_url', inputImageUrl.value)
  }

  // Optimistic UI update
  messages.value.push({
    role: 'user',
    display_text: inputText.value,
    image_url: inputImageUrl.value
  })
  inputText.value = ''
  removeImage()
  scrollToBottom()
  loading.value = true

  // Add empty assistant message for streaming
  const assistantMsgIndex = messages.value.push({ role: 'assistant', display_text: '' }) - 1
  
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/chat/sessions/${sid}/message`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    })

    if (!response.body) throw new Error('No response body')

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || '' // keep the last incomplete chunk in the buffer
      
      for (const line of lines) {
        if (line.trim() === '') continue
        if (line.startsWith('data: [DONE]')) return
        if (line.startsWith('data: ')) {
          try {
             const data = JSON.parse(line.substring(6))
             if (data.error !== undefined) {
               messages.value[assistantMsgIndex].display_text = '⚠️ Error: ' + data.error
               scrollToBottom()
             } else if (data.text !== undefined) {
               messages.value[assistantMsgIndex].display_text += data.text
               scrollToBottom()
             }
          } catch(e) {
             console.error('Failed to parse stream chunk:', line, e)
          }
        }
      }
    }
  } catch (err) {
    ElMessage.error('Failed to send message')
  } finally {
    loading.value = false
  }
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

onMounted(() => {
  fetchSessions()
})
</script>

<template>
  <div class="chat-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2 class="logo">GLM-4V-Plus</h2>
        <el-button type="primary" size="small" circle icon="el-icon-plus" @click="createSession">+</el-button>
      </div>
      <div class="session-list">
        <div 
          v-for="s in sessions" 
          :key="s.id" 
          class="session-item"
          :class="{ active: s.id === currentSessionId }"
          @click="selectSession(s.id)"
        >
          <div class="session-info">
            <div class="session-title">{{ s.title }}</div>
            <div class="session-date">{{ new Date(s.created_at.replace(' ', 'T')).toLocaleDateString() }}</div>
          </div>
          <el-button class="delete-btn" type="danger" text circle size="small" @click="deleteSession(s.id, $event)">×</el-button>
        </div>
      </div>
      <div class="sidebar-footer">
        <el-button type="danger" text @click="logout" size="small">Logout</el-button>
      </div>
    </aside>

    <main class="chat-main">
      <div class="messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-state">
          <div class="glowing-orb"></div>
          <h3>Initialize Nexus</h3>
          <p>Start a conversation or upload an image for GLM-4V-Plus to analyze.</p>
        </div>
        
        <div 
          v-for="(msg, idx) in messages" 
          :key="idx"
          class="message-wrapper"
          :class="msg.role === 'user' ? 'user-msg' : 'assistant-msg'"
        >
          <div class="message-bubble">
            <template v-if="msg.image_url">
              <img :src="msg.image_url" class="msg-image" alt="Uploaded Image" />
            </template>
            <div class="msg-text">{{ msg.display_text }}</div>
            <div v-if="loading && idx === messages.length -1 && msg.role === 'assistant'" class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <div class="image-preview" v-if="inputImageUrl">
          <img :src="inputImageUrl" />
          <div class="remove-btn" @click="removeImage">×</div>
        </div>
        <div class="input-controls">
          <el-button type="primary" circle class="upload-btn" @click="$refs.fileInput.click()">
             <i class="el-icon-picture">+</i>
          </el-button>
          <input type="file" ref="fileInput" hidden @change="handleFileChange" accept="image/*" />
          
          <el-input
            v-model="inputText"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 4 }"
            placeholder="Ask GLM-4V-Plus something..."
            class="chat-input"
            @keydown.enter.exact.prevent="sendMessage"
          />
          <el-button type="primary" :loading="loading" class="send-btn" circle @click="sendMessage">
            >
          </el-button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: var(--bg-dark);
}

.sidebar {
  width: 280px;
  background: rgba(25, 25, 25, 0.95);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
}

.sidebar-header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.logo {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 800;
  background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.session-item {
  padding: 12px 15px;
  border-radius: 10px;
  cursor: pointer;
  margin-bottom: 5px;
  transition: all 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-info {
  flex: 1;
  overflow: hidden;
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s ease;
  margin-left: 10px;
}

.session-item:hover .delete-btn {
  opacity: 1;
}

.session-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.session-item.active {
  background: rgba(0, 229, 255, 0.1);
  border-left: 3px solid var(--primary);
}

.session-title {
  color: #fff;
  font-size: 0.95rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-date {
  color: #718096;
  font-size: 0.75rem;
  margin-top: 4px;
}

.sidebar-footer {
  padding: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: center;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  background-image: radial-gradient(circle at center, rgba(30,30,40,1) 0%, rgba(10,10,10,1) 100%);
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 10%;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.empty-state {
  margin: auto;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.glowing-orb {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: radial-gradient(circle, #00e5ff 0%, #0072ff 100%);
  box-shadow: 0 0 40px rgba(0, 229, 255, 0.4);
  animation: pulse 3s infinite alternate;
}

@keyframes pulse {
  0% { transform: scale(1); box-shadow: 0 0 20px rgba(0, 229, 255, 0.4); }
  100% { transform: scale(1.1); box-shadow: 0 0 60px rgba(0, 229, 255, 0.8); }
}

.message-wrapper {
  display: flex;
  width: 100%;
}

.user-msg {
  justify-content: flex-end;
}

.assistant-msg {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 1rem;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  color: #fff;
  line-height: 1.5;
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}

.user-msg .message-bubble {
  background: linear-gradient(135deg, rgba(0, 198, 255, 0.1), rgba(0, 114, 255, 0.2));
  border-color: rgba(0, 229, 255, 0.2);
  border-bottom-right-radius: 5px;
}

.assistant-msg .message-bubble {
  border-bottom-left-radius: 5px;
}

.msg-image {
  max-width: 100%;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.msg-text {
  white-space: pre-wrap;
}

.input-area {
  padding: 1.5rem 10%;
  background: linear-gradient(0deg, rgba(10,10,10,1) 0%, rgba(10,10,10,0) 100%);
}

.image-preview {
  position: relative;
  display: inline-block;
  margin-bottom: 10px;
}

.image-preview img {
  height: 80px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.2);
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  background: red;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
}

.input-controls {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  background: rgba(30, 30, 30, 0.6);
  backdrop-filter: blur(10px);
  padding: 10px;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

::v-deep(.chat-input .el-textarea__inner) {
  background: transparent !important;
  box-shadow: none !important;
  color: #fff !important;
  border: none !important;
  resize: none;
}

.upload-btn, .send-btn {
  background: rgba(255,255,255,0.1);
  border: none;
  color: var(--primary);
  font-weight: bold;
}

.upload-btn:hover, .send-btn:hover {
  background: rgba(0, 229, 255, 0.2);
  color: white;
  box-shadow: 0 0 15px rgba(0, 229, 255, 0.3);
}

.typing-indicator span {
  display: inline-block;
  width: 6px;
  height: 6px;
  background-color: var(--primary);
  border-radius: 50%;
  margin: 0 2px;
  animation: bounce 1.4s infinite ease-in-out both;
}
.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>

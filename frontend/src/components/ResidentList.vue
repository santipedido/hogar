<template>
  <div class="resident-list">
    <h2>Residentes</h2>
    <button @click="openAdd" class="add-btn">Agregar residente</button>

    <ResidentForm
      v-if="showForm"
      :modelValue="selectedResident"
      :isEdit="isEdit"
      @submit="handleFormSubmit"
      @cancel="closeForm"
    />

    <div v-if="loading" class="loader">
      <IconSpinner :size="50" />
      <p>{{ loadingMessage }}</p>
      <div v-if="initialLoad && countdown > 0" class="progress-bar">
        <div 
          class="progress" 
          :style="{ width: `${(countdown / 30) * 100}%` }"
        ></div>
      </div>
    </div>
    <div v-else-if="error" class="error">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <p>{{ error }}</p>
      <button @click="fetchResidents" class="retry-btn">Reintentar</button>
    </div>
    <div v-else>
      <div v-if="residents.length === 0" class="empty">No hay residentes registrados.</div>
      <div class="cards">
        <div v-for="resident in residents" :key="resident.id" class="card resident-card">
          <div class="photo-container">
            <img 
              v-if="resident.photo_url" 
              :src="resident.photo_url" 
              :alt="'Foto de ' + resident.name" 
              class="photo" 
            />
            <IconUserPlaceholder
              v-else
              class="photo-placeholder"
            />
          </div>

          <div class="info">
            <h3>{{ resident.name }}</h3>
            
            <span :class="['status', resident.status]">
              {{ resident.status === 'independent' ? 'Independiente' : 'Semidependiente' }}
            </span>

            <div class="admission-date" v-if="resident.admission_date">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                <line x1="16" y1="2" x2="16" y2="6" />
                <line x1="8" y1="2" x2="8" y2="6" />
                <line x1="3" y1="10" x2="21" y2="10" />
              </svg>
              <span>Ingreso: {{ formatDate(resident.admission_date) }}</span>
            </div>

            <div class="contact-info">
              <div v-if="resident.emergency_contact_name" class="contact-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                <span>{{ resident.emergency_contact_name }}</span>
              </div>

              <div v-if="resident.emergency_contact_phone" class="contact-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                </svg>
                <span>{{ resident.emergency_contact_phone }}</span>
              </div>
            </div>

            <div class="actions">
              <button @click="openEdit(resident)" class="edit-btn">Editar</button>
              <button @click="removeResident(resident.id)" class="delete-btn">Eliminar</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import ResidentForm from './ResidentForm.vue'
import IconSpinner from './icons/IconSpinner.vue'
import IconUserPlaceholder from './icons/IconUserPlaceholder.vue'

const residents = ref([])
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const isEdit = ref(false)
const selectedResident = ref(null)
const initialLoad = ref(true)
const countdown = ref(30) // 30 segundos de tiempo máximo estimado
const countdownInterval = ref(null)

const loadingMessage = computed(() => {
  if (!initialLoad.value) return 'Cargando residentes...'
  return countdown.value > 0
    ? `Iniciando el servidor... Esto puede tardar hasta ${countdown.value} segundos`
    : 'El servidor está tardando más de lo esperado...'
})

function startCountdown() {
  countdown.value = 30
  countdownInterval.value = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      clearInterval(countdownInterval.value)
    }
  }, 1000)
}

function stopCountdown() {
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
    countdownInterval.value = null
  }
}

async function fetchResidents() {
  loading.value = true
  error.value = ''
  
  if (initialLoad.value) {
    startCountdown()
  }

  try {
    const res = await fetch(import.meta.env.VITE_API_URL + '/residents/')
    if (!res.ok) throw new Error('No se pudo cargar la lista')
    residents.value = await res.json()
    initialLoad.value = false
  } catch (e) {
    if (e.message === 'Failed to fetch') {
      error.value = 'No se pudo conectar con el servidor. Es posible que esté iniciando, por favor espera un momento.'
    } else {
      error.value = e.message
    }
  } finally {
    loading.value = false
    stopCountdown()
  }
}

onMounted(fetchResidents)

function openAdd() {
  selectedResident.value = null
  isEdit.value = false
  showForm.value = true
}

function openEdit(resident) {
  selectedResident.value = { ...resident }
  isEdit.value = true
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  selectedResident.value = null
}

function cleanResidentData(data) {
  const cleaned = { ...data }
  Object.keys(cleaned).forEach(key => {
    if (cleaned[key] === '') cleaned[key] = null
  })
  return cleaned
}

async function handleFormSubmit(data) {
  try {
    const cleanedData = cleanResidentData(data)
    if (isEdit.value && selectedResident.value) {
      // Editar
      const res = await fetch(import.meta.env.VITE_API_URL + `/residents/${selectedResident.value.id}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cleanedData)
      })
      if (!res.ok) throw new Error('No se pudo editar el residente')
    } else {
      // Crear
      const res = await fetch(import.meta.env.VITE_API_URL + '/residents/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cleanedData)
      })
      if (!res.ok) throw new Error('No se pudo agregar el residente')
    }
    await fetchResidents()
    closeForm()
  } catch (e) {
    alert(e.message)
  }
}

async function removeResident(id) {
  if (!confirm('¿Seguro que deseas eliminar este residente?')) return
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + `/residents/${id}/`, {
      method: 'DELETE'
    })
    if (!res.ok) throw new Error('No se pudo eliminar el residente')
    await fetchResidents()
  } catch (e) {
    alert(e.message)
  }
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('es-ES', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  }).format(date)
}
</script>

<style scoped>
.add-btn {
  margin-bottom: 1.5rem;
}
.actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1rem;
}
.photo {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 50%;
  margin-bottom: 0.5rem;
  border: 2px solid var(--color-primary);
}
.info {
  text-align: center;
}
.loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
  color: var(--color-text-light);
  text-align: center;
}

.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
  color: var(--color-danger, #dc3545);
  text-align: center;
  background: var(--color-background-soft);
  border-radius: 8px;
  margin: 1rem 0;
}

.retry-btn {
  background: transparent;
  border: 1px solid var(--color-danger, #dc3545);
  color: var(--color-danger, #dc3545);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: var(--color-danger, #dc3545);
  color: white;
}

.progress-bar {
  width: 200px;
  height: 4px;
  background: var(--color-background-soft);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 1rem;
}

.progress {
  height: 100%;
  background: var(--color-primary);
  transition: width 1s linear;
}

.resident-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  background: var(--color-background-soft);
  border-radius: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
  gap: 1rem;
  width: 100%;
  max-width: 320px;
}

.resident-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.photo-container {
  width: 120px;
  height: 120px;
  border-radius: 60px;
  overflow: hidden;
  background: var(--color-background-mute);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid var(--color-primary);
}

.photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  color: var(--color-text-light);
  opacity: 0.5;
}

.info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0 1rem;
}

.info h3 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--color-heading);
}

.status {
  font-size: 0.875rem;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  background: var(--color-background-mute);
}

.status.independent {
  color: #10B981;
  background: rgba(16, 185, 129, 0.1);
}

.status.semi-dependent {
  color: #F59E0B;
  background: rgba(245, 158, 11, 0.1);
}

.admission-date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-light);
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
  margin: 0.75rem 0;
  padding: 0.75rem;
  background: var(--color-background-mute);
  border-radius: 8px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: var(--color-text);
  padding: 0.25rem;
}

.contact-item span {
  word-break: break-word;
  line-height: 1.4;
}

.actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  width: 100%;
  justify-content: center;
}

.edit-btn, .delete-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: all 0.2s;
  flex: 1;
  max-width: 120px;
}

.edit-btn {
  background: var(--color-primary);
  color: white;
  border: none;
}

.edit-btn:hover {
  background: var(--color-primary-dark, #3b82f6);
}

.delete-btn {
  background: transparent;
  border: 1px solid var(--color-danger, #dc3545);
  color: var(--color-danger, #dc3545);
}

.delete-btn:hover {
  background: var(--color-danger, #dc3545);
  color: white;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  padding: 1rem 0;
}
</style> 
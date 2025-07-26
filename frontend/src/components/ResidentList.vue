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
          <div class="card-content" @click="emit('select-resident', resident)">
            <img v-if="resident.photo_url" :src="resident.photo_url" alt="Foto" class="photo" />
            <div class="info">
              <h3>{{ resident.name }}</h3>
              <span :class="['status', resident.status]">
                {{ resident.status === 'independent' ? 'Independiente' : 'Semidependiente' }}
              </span>
              <p v-if="resident.emergency_contact_name">
                <strong>Contacto:</strong> {{ resident.emergency_contact_name }}
              </p>
              <p v-if="resident.emergency_contact_phone">
                <strong>Tel:</strong> {{ resident.emergency_contact_phone }}
              </p>
            </div>
          </div>
          <div class="actions">
            <button @click="openEdit(resident)">Editar</button>
            <button @click="removeResident(resident.id)" class="secondary danger">Eliminar</button>
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
    const res = await fetch(import.meta.env.VITE_API_URL + '/api/residents/')
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
      const res = await fetch(import.meta.env.VITE_API_URL + `/api/residents/${selectedResident.value.id}/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cleanedData)
      })
      if (!res.ok) throw new Error('No se pudo editar el residente')
    } else {
      // Crear
      const res = await fetch(import.meta.env.VITE_API_URL + '/api/residents/', {
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
    const res = await fetch(import.meta.env.VITE_API_URL + `/api/residents/${id}/`, {
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

const emit = defineEmits(['select-resident'])
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
  font-weight: 500;
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
  justify-items: center;
}

.card-content {
  cursor: pointer;
  padding: 1rem;
  transition: background-color 0.2s;
  border-radius: 8px;
}

.card-content:hover {
  background: var(--color-background-mute);
}

@media (max-width: 640px) {
  .cards {
    grid-template-columns: 1fr;
    padding: 1rem;
  }

  .resident-card {
    max-width: 100%;
    width: 100%;
  }

  .info {
    padding: 0 0.5rem;
  }

  .actions {
    flex-direction: column;
    width: 100%;
  }

  .edit-btn, .delete-btn {
    max-width: 100%;
  }
}

@media (min-width: 641px) and (max-width: 1024px) {
  .cards {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    padding: 1rem;
  }

  .resident-card {
    width: 100%;
  }
}

.resident-list {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}
</style> 
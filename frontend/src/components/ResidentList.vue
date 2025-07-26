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
            <div class="actions">
              <button @click="openEdit(resident)">Editar</button>
              <button @click="removeResident(resident.id)" class="secondary danger">Eliminar</button>
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
</style> 
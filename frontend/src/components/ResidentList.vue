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
      <p>Cargando residentes...</p>
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
import { ref, onMounted } from 'vue'
import ResidentForm from './ResidentForm.vue'
import IconSpinner from './icons/IconSpinner.vue'

const residents = ref([])
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const isEdit = ref(false)
const selectedResident = ref(null)

async function fetchResidents() {
  loading.value = true
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + '/residents/')
    if (!res.ok) throw new Error('No se pudo cargar la lista')
    residents.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
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
</style> 
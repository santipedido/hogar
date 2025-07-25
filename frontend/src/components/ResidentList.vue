<template>
  <div class="resident-list">
    <h2>Residentes</h2>
    <button @click="openAdd" class="add-btn">Agregar residente</button>
    <div v-if="loading" class="loader">Cargando...</div>
    <div v-else-if="error" class="error">Error: {{ error }}</div>
    <div v-else>
      <div v-if="residents.length === 0" class="empty">No hay residentes registrados.</div>
      <div class="cards">
        <div v-for="resident in residents" :key="resident.id" class="card">
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
              <button @click="removeResident(resident.id)" class="secondary">Eliminar</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <ResidentForm
      v-if="showForm"
      :modelValue="selectedResident"
      :isEdit="isEdit"
      @submit="handleFormSubmit"
      @cancel="closeForm"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ResidentForm from './ResidentForm.vue'

const residents = ref([])
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const isEdit = ref(false)
const selectedResident = ref(null)

async function fetchResidents() {
  loading.value = true
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + '/residents')
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

async function handleFormSubmit(data) {
  try {
    if (isEdit.value && selectedResident.value) {
      // Editar
      const res = await fetch(import.meta.env.VITE_API_URL + `/residents/${selectedResident.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!res.ok) throw new Error('No se pudo editar el residente')
    } else {
      // Crear
      const res = await fetch(import.meta.env.VITE_API_URL + '/residents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
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
    const res = await fetch(import.meta.env.VITE_API_URL + `/residents/${id}`, {
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
.resident-list {
  max-width: 900px;
  margin: 2rem auto;
  background: #f8f5f0;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 2px 8px #0001;
}
.cards {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  justify-content: center;
}
.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 4px #0002;
  padding: 1rem 1.5rem;
  min-width: 220px;
  max-width: 260px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.photo {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 50%;
  margin-bottom: 0.5rem;
  border: 2px solid #4a90e2;
}
.info {
  text-align: center;
}
.status {
  display: inline-block;
  margin: 0.5rem 0;
  padding: 0.2rem 0.8rem;
  border-radius: 8px;
  font-size: 0.95em;
  color: #fff;
}
.status.independent {
  background: #7ed957;
}
.status.semidependent {
  background: #4a90e2;
}
.loader {
  text-align: center;
  color: #4a90e2;
  font-weight: bold;
}
.error {
  color: #c00;
  text-align: center;
}
.empty {
  text-align: center;
  color: #888;
  margin-top: 2rem;
}
.add-btn {
  margin-bottom: 1.5rem;
}
.actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1rem;
}
button.secondary {
  background: #eee;
  color: #333;
}
</style> 
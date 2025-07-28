<template>
  <div class="medication-list">
    <div class="header">
      <h3>Medicación</h3>
      <div class="header-actions">
        <button @click="showCalendar = !showCalendar" class="calendar-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          {{ showCalendar ? 'Lista' : 'Calendario' }}
        </button>
        <button @click="openAdd" class="add-btn">Agregar medicación</button>
      </div>
    </div>

    <MedicationForm
      v-if="showForm"
      :modelValue="selectedMedication"
      :residentId="residentId"
      :isEdit="isEdit"
      @submit="handleFormSubmit"
      @cancel="closeForm"
    />

    <!-- Vista de Calendario -->
    <div v-if="showCalendar">
      <MedicationCalendar :residentId="residentId" />
    </div>

    <!-- Vista de Lista -->
    <div v-else>
      <div v-if="loading" class="loader">
        <IconSpinner :size="50" />
        <p>Cargando medicación...</p>
      </div>
      <div v-else-if="error" class="error">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <p>{{ error }}</p>
        <button @click="fetchMedications" class="retry-btn">Reintentar</button>
      </div>
      <div v-else>
        <div v-if="medications.length === 0" class="empty">
          No hay medicación registrada.
        </div>
        <div v-else class="medications">
          <div v-for="medication in medications" :key="medication.id" class="medication-card" :class="{ 'administered': medication.administered_at }">
            <div class="medication-info">
              <div class="name-badge">
                <h4>{{ medication.med_name }}</h4>
                <span v-if="medication.administered_at" class="administered-badge">Administrada</span>
              </div>
              <p class="dosage">{{ medication.dosage }}</p>
              <p class="frequency">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12,6 12,12 16,14"></polyline>
                </svg>
                {{ medication.frequency }}
              </p>
              <p v-if="medication.scheduled_time" class="scheduled-time">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                  <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
                Hora: {{ formatTime(medication.scheduled_time) }}
              </p>
              <p v-if="medication.administered_at" class="administered-time">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22,4 12,14.01 9,11.01"></polyline>
                </svg>
                Administrada: {{ formatDateTime(medication.administered_at) }}
              </p>
              <p v-if="medication.notes" class="notes">{{ medication.notes }}</p>
            </div>
            <div class="actions">
              <button 
                v-if="!medication.administered_at" 
                @click="administerMedication(medication.id)" 
                class="administer-btn"
              >
                Administrar
              </button>
              <button @click="openEdit(medication)" class="edit-btn">Editar</button>
              <button @click="removeMedication(medication.id)" class="delete-btn">Eliminar</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MedicationForm from './MedicationForm.vue'
import MedicationCalendar from './MedicationCalendar.vue'
import IconSpinner from './icons/IconSpinner.vue'

const props = defineProps({
  residentId: {
    type: String,
    required: true
  }
})

const medications = ref([])
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const isEdit = ref(false)
const selectedMedication = ref(null)
const showCalendar = ref(false)

async function fetchMedications() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + `/api/medications/resident/${props.residentId}`)
    if (!res.ok) throw new Error('No se pudo cargar la medicación')
    medications.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function formatTime(timeString) {
  if (!timeString) return ''
  return timeString.substring(0, 5) // Mostrar solo HH:MM
}

function formatDateTime(dateTimeString) {
  if (!dateTimeString) return ''
  const date = new Date(dateTimeString)
  return new Intl.DateTimeFormat('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

onMounted(fetchMedications)

function openAdd() {
  selectedMedication.value = null
  isEdit.value = false
  showForm.value = true
}

function openEdit(medication) {
  selectedMedication.value = { ...medication }
  isEdit.value = true
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  selectedMedication.value = null
}

async function handleFormSubmit(data) {
  try {
    if (isEdit.value && selectedMedication.value) {
      // Editar
      const res = await fetch(import.meta.env.VITE_API_URL + `/api/medications/${selectedMedication.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!res.ok) throw new Error('No se pudo editar la medicación')
    } else {
      // Crear
      const res = await fetch(import.meta.env.VITE_API_URL + '/api/medications/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!res.ok) throw new Error('No se pudo agregar la medicación')
    }
    await fetchMedications()
    closeForm()
  } catch (e) {
    alert(e.message)
  }
}

async function administerMedication(id) {
  if (!confirm('¿Confirmar que se administró esta medicación?')) return
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + `/api/medications/${id}/administer?user_id=current_user`, {
      method: 'POST'
    })
    if (!res.ok) throw new Error('No se pudo marcar como administrada')
    await fetchMedications()
  } catch (e) {
    alert(e.message)
  }
}

async function removeMedication(id) {
  if (!confirm('¿Seguro que deseas eliminar esta medicación?')) return
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + `/api/medications/${id}`, {
      method: 'DELETE'
    })
    if (!res.ok) throw new Error('No se pudo eliminar la medicación')
    await fetchMedications()
  } catch (e) {
    alert(e.message)
  }
}
</script>

<style scoped>
.medication-list {
  padding: 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h3 {
  margin: 0;
  color: var(--color-heading);
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.calendar-btn {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.calendar-btn:hover {
  background: var(--color-background-mute);
}

.add-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.add-btn:hover {
  background: var(--color-primary-dark, #3b82f6);
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
  transition: all 0.2s;
}

.retry-btn:hover {
  background: var(--color-danger, #dc3545);
  color: white;
}

.empty {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-light);
  background: var(--color-background-soft);
  border-radius: 8px;
}

.medications {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.medication-card {
  background: var(--color-background-soft);
  border-radius: 10px;
  padding: 1.5rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.medication-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.medication-card.administered {
  border: 2px solid var(--color-success, #28a745);
  opacity: 0.8;
}

.name-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.name-badge h4 {
  margin: 0;
  color: var(--color-heading);
}

.administered-badge {
  background: var(--color-success, #28a745);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.75rem;
}

.dosage {
  color: var(--color-text);
  font-size: 1rem;
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.frequency, .scheduled-time, .administered-time {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.5rem 0;
  font-size: 0.875rem;
  color: var(--color-text-light);
}

.notes {
  margin-top: 1rem;
  font-size: 0.875rem;
  color: var(--color-text-light);
  font-style: italic;
}

.actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.administer-btn, .edit-btn, .delete-btn {
  flex: 1;
  padding: 0.5rem;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.administer-btn {
  background: var(--color-success, #28a745);
  color: white;
  border: none;
}

.administer-btn:hover {
  background: var(--color-success-dark, #218838);
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

@media (max-width: 640px) {
  .medications {
    grid-template-columns: 1fr;
  }
  
  .medication-card {
    width: 100%;
  }
  
  .actions {
    flex-direction: column;
  }
}
</style> 
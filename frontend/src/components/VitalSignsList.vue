<template>
  <div class="vital-signs-list">
    <div class="header">
      <h3>Signos Vitales</h3>
      <div class="header-actions">
        <button @click="openAdd" class="add-btn">Agregar registro</button>
      </div>
    </div>

    <VitalSignForm
      v-if="showForm"
      :modelValue="selectedVitalSign"
      :residentId="residentId"
      :isEdit="isEdit"
      @submit="handleFormSubmit"
      @cancel="closeForm"
    />

    <div v-if="loading" class="loader">
      <IconSpinner :size="50" />
      <p>Cargando signos vitales...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="fetchVitalSigns" class="retry-btn">Reintentar</button>
    </div>
    <div v-else>
      <div v-if="vitalSigns.length === 0" class="empty">No hay registros de signos vitales.</div>
      <div v-else>
        <div v-for="vital in vitalSigns" :key="vital.id" class="card vital-card">
          <div class="info">
            <h4>{{ vital.type }}</h4>
            <p v-if="vital.type === 'Presión Arterial'">
              {{ vital.systolic }}/{{ vital.diastolic }} {{ vital.unit || 'mmHg' }}
            </p>
            <p v-else>
              {{ vital.value }} {{ vital.unit }}
            </p>
            <p class="taken-at">Tomado: {{ formatDateTime(vital.taken_at) }}</p>
            <p v-if="vital.notes" class="notes">{{ vital.notes }}</p>
            <p v-if="vital.taken_by" class="taken-by">Por: {{ vital.taken_by }}</p>
          </div>
          <div class="actions">
            <button @click="openEdit(vital)" class="edit-btn">Editar</button>
            <button @click="removeVitalSign(vital.id)" class="delete-btn">Eliminar</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import VitalSignForm from './VitalSignForm.vue'
import IconSpinner from './icons/IconSpinner.vue'

const props = defineProps({
  residentId: {
    type: String,
    required: true
  }
})

const vitalSigns = ref([])
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const isEdit = ref(false)
const selectedVitalSign = ref(null)

async function fetchVitalSigns() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + `/api/vital-signs/resident/${props.residentId}`)
    if (!res.ok) throw new Error('No se pudo cargar la lista')
    vitalSigns.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchVitalSigns)

function openAdd() {
  selectedVitalSign.value = null
  isEdit.value = false
  showForm.value = true
}

function openEdit(vital) {
  selectedVitalSign.value = { ...vital }
  isEdit.value = true
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  selectedVitalSign.value = null
}

async function handleFormSubmit(data) {
  try {
    if (isEdit.value && selectedVitalSign.value) {
      // Editar
      const res = await fetch(import.meta.env.VITE_API_URL + `/api/vital-signs/${selectedVitalSign.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!res.ok) throw new Error('No se pudo editar el registro')
    } else {
      // Crear
      const res = await fetch(import.meta.env.VITE_API_URL + '/api/vital-signs/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, resident_id: props.residentId })
      })
      if (!res.ok) throw new Error('No se pudo agregar el registro')
    }
    await fetchVitalSigns()
    closeForm()
  } catch (e) {
    alert(e.message)
  }
}

async function removeVitalSign(id) {
  if (!confirm('¿Seguro que deseas eliminar este registro?')) return
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + `/api/vital-signs/${id}`, {
      method: 'DELETE'
    })
    if (!res.ok) throw new Error('No se pudo eliminar el registro')
    await fetchVitalSigns()
  } catch (e) {
    alert(e.message)
  }
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
</script>

<style scoped>
.vital-signs-list {
  padding: 1rem;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}
.add-btn {
  margin-bottom: 0;
}
.card.vital-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: #fff;
}
.info {
  flex: 1;
}
.actions {
  display: flex;
  gap: 0.5rem;
}
.loader {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.empty {
  text-align: center;
  color: #888;
  margin-top: 2rem;
}
</style> 
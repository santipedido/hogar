<template>
  <div class="vital-signs-list">
    <div class="header">
      <h3>Signos Vitales</h3>
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

    <!-- Vista de Calendario -->
    <div v-if="showCalendar">
      <VitalSignsCalendar :residentId="residentId" />
    </div>

    <!-- Vista de Lista -->
    <div v-else>
      <div v-if="loading" class="loader">
        <IconSpinner :size="50" />
        <p>Cargando signos vitales...</p>
      </div>
      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="fetchVitalSigns" class="retry-btn">Reintentar</button>
      </div>
      <div v-else>
        <div v-if="paginatedData.length === 0" class="empty">No hay registros de signos vitales.</div>
        <div v-else>
          <div v-for="vital in paginatedData" :key="vital.id" class="card vital-card">
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
          
          <!-- Paginación -->
          <div v-if="pagination.total_pages > 1" class="pagination">
            <button 
              @click="goToPage(pagination.page - 1)" 
              :disabled="!pagination.has_prev"
              class="pagination-btn"
            >
              Anterior
            </button>
            
            <div class="pagination-info">
              Página {{ pagination.page }} de {{ pagination.total_pages }} 
              ({{ pagination.total_count }} registros)
            </div>
            
            <button 
              @click="goToPage(pagination.page + 1)" 
              :disabled="!pagination.has_next"
              class="pagination-btn"
            >
              Siguiente
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import VitalSignForm from './VitalSignForm.vue'
import VitalSignsCalendar from './VitalSignsCalendar.vue'
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
const showCalendar = ref(false)



const currentPage = ref(1)
const pagination = ref({
  page: 1,
  limit: 10,
  total_count: 0,
  total_pages: 0,
  has_next: false,
  has_prev: false
})

const paginatedData = computed(() => vitalSigns.value)

async function fetchVitalSigns(page = 1) {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + `/api/vital-signs/resident/${props.residentId}/paginated?page=${page}&limit=10`)
    if (!res.ok) throw new Error('No se pudo cargar la lista')
    const response = await res.json()
    vitalSigns.value = response.data
    pagination.value = response.pagination
    currentPage.value = page
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  if (page >= 1 && page <= pagination.value.total_pages) {
    fetchVitalSigns(page)
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

.calendar-btn {
  background: transparent !important;
  border: 1px solid var(--color-border) !important;
  color: var(--color-text) !important;
  padding: 0.5rem 1rem !important;
  border-radius: 6px !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
  display: flex !important;
  align-items: center !important;
  gap: 0.5rem !important;
  margin-bottom: 0 !important;
  box-shadow: none !important;
  font-size: 1rem !important;
  font-weight: normal !important;
}

.calendar-btn:hover {
  background: var(--color-background-mute) !important;
  transform: none !important;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding: 1rem;
  background: var(--color-background-soft);
  border-radius: 8px;
}

.pagination-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:disabled {
  background: var(--color-border);
  cursor: not-allowed;
}

.pagination-btn:not(:disabled):hover {
  background: var(--color-primary-dark);
}

.pagination-info {
  color: var(--color-text);
  font-size: 0.875rem;
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
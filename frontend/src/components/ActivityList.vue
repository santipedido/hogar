<template>
  <div class="activity-list">
    <div class="header">
      <h3>Actividades</h3>
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
        <button @click="openAdd" class="add-btn">Agregar actividad</button>
      </div>
    </div>

    <ActivityForm
      v-if="showForm"
      :modelValue="selectedActivity"
      :residentId="residentId"
      :isEdit="isEdit"
      @submit="handleFormSubmit"
      @cancel="closeForm"
    />

    <!-- Vista de Calendario -->
    <div v-if="showCalendar">
      <ActivityCalendar :residentId="residentId" />
    </div>

    <!-- Vista de Lista -->
    <div v-else>
      <div v-if="loading" class="loader">
        <IconSpinner :size="50" />
        <p>Cargando actividades...</p>
      </div>
      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="fetchActivities" class="retry-btn">Reintentar</button>
      </div>
      <div v-else>
        <div v-if="paginatedData.length === 0" class="empty">No hay actividades registradas.</div>
        <div v-else>
          <div v-for="activity in paginatedData" :key="activity.id" class="card activity-card">
            <div class="info">
              <div class="activity-header">
                <h4>{{ activity.title }}</h4>
                <span :class="['status-badge', activity.status]">
                  {{ getStatusText(activity.status) }}
                </span>
              </div>
              <p class="type">{{ activity.type }} - {{ activity.subtype }}</p>
              <p class="scheduled-at">Programada: {{ formatDateTime(activity.scheduled_at) }}</p>
              <p v-if="activity.completed_at" class="completed-at">Completada: {{ formatDateTime(activity.completed_at) }}</p>
              <p class="participants">Participantes: {{ activity.participants }}</p>
              <div v-if="activity.participants_data && activity.participants_data.length > 0" class="participants-details">
                <span 
                  v-for="participant in activity.participants_data" 
                  :key="`${participant.type}-${participant.id || participant.name}`"
                  class="participant-badge"
                  :class="participant.type"
                >
                  {{ participant.name }}
                </span>
              </div>
              <p v-if="activity.description" class="description">{{ activity.description }}</p>
              <p v-if="activity.notes" class="notes">{{ activity.notes }}</p>
              <p v-if="activity.registered_by" class="registered-by">Registrado por: {{ activity.registered_by }}</p>
              <div v-if="activity.is_recurring" class="recurring-info">
                <span class="recurring-badge">🔄 Actividad semanal</span>
                <span class="recurrence-day">{{ getDayText(activity.recurrence_day) }}</span>
              </div>
            </div>
            <div class="actions">
              <button @click="openEdit(activity)" class="edit-btn">Editar</button>
              <button @click="removeActivity(activity.id)" class="delete-btn">Eliminar</button>
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
import ActivityForm from './ActivityForm.vue'
import ActivityCalendar from './ActivityCalendar.vue'
import IconSpinner from './icons/IconSpinner.vue'

const props = defineProps({
  residentId: {
    type: String,
    required: true
  }
})

const activities = ref([])
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const isEdit = ref(false)
const selectedActivity = ref(null)
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

const paginatedData = computed(() => activities.value)

async function fetchActivities(page = 1) {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + `/api/activities/resident/${props.residentId}/paginated?page=${page}&limit=10`)
    if (!res.ok) throw new Error('No se pudo cargar la lista')
    const response = await res.json()
    activities.value = response.data
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
    fetchActivities(page)
  }
}

onMounted(fetchActivities)

function openAdd() {
  selectedActivity.value = null
  isEdit.value = false
  showForm.value = true
}

function openEdit(activity) {
  selectedActivity.value = { ...activity }
  isEdit.value = true
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  selectedActivity.value = null
}

async function handleFormSubmit(data) {
  try {
    if (isEdit.value && selectedActivity.value) {
      // Editar
      const res = await fetch(import.meta.env.VITE_API_URL + `/api/activities/${selectedActivity.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!res.ok) throw new Error('No se pudo editar la actividad')
    } else {
      // Crear
      const res = await fetch(import.meta.env.VITE_API_URL + '/api/activities/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!res.ok) throw new Error('No se pudo agregar la actividad')
    }
    await fetchActivities()
    closeForm()
  } catch (e) {
    alert(e.message)
  }
}

async function removeActivity(id) {
  if (!confirm('¿Seguro que deseas eliminar esta actividad?')) return
  try {
    const res = await fetch(import.meta.env.VITE_API_URL + `/api/activities/${id}`, {
      method: 'DELETE'
    })
    if (!res.ok) throw new Error('No se pudo eliminar la actividad')
    await fetchActivities()
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

function getStatusText(status) {
  const statusMap = {
    'scheduled': 'Programada',
    'completed': 'Completada',
    'cancelled': 'Cancelada'
  }
  return statusMap[status] || status
}

function getDayText(day) {
  const dayMap = {
    'monday': 'Lunes',
    'tuesday': 'Martes',
    'wednesday': 'Miércoles',
    'thursday': 'Jueves',
    'friday': 'Viernes',
    'saturday': 'Sábado',
    'sunday': 'Domingo'
  }
  return dayMap[day] || day
}
</script>

<style scoped>
.activity-list {
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
  margin-bottom: 0;
}

.calendar-btn:hover {
  background: var(--color-background-mute);
}

.card.activity-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: #fff;
}

.info {
  flex: 1;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.activity-header h4 {
  margin: 0;
  color: var(--color-heading);
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.scheduled {
  background: #e3f2fd;
  color: #1976d2;
}

.status-badge.completed {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-badge.cancelled {
  background: #ffebee;
  color: #c62828;
}

.type {
  margin: 0.25rem 0;
  color: var(--color-text-light);
  font-size: 0.875rem;
}

.scheduled-at,
.completed-at {
  margin: 0.25rem 0;
  color: var(--color-text);
  font-weight: 500;
}

.participants {
  margin: 0.25rem 0;
  color: var(--color-text);
}

.description {
  margin: 0.5rem 0;
  color: var(--color-text);
  font-style: italic;
}

.notes {
  margin: 0.25rem 0;
  color: var(--color-text-light);
  font-size: 0.875rem;
}

.registered-by {
  margin: 0.25rem 0;
  color: var(--color-text-light);
  font-size: 0.875rem;
}

.recurring-info {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.recurring-badge {
  background: #fff3e0;
  color: #e65100;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.recurrence-day {
  color: var(--color-text-light);
  font-size: 0.875rem;
}

.participants-details {
  margin: 0.5rem 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.participant-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.participant-badge.resident {
  background: #e3f2fd;
  color: #1976d2;
}

.participant-badge.staff {
  background: #e8f5e8;
  color: #2e7d32;
}

.participant-badge.family {
  background: #fff3e0;
  color: #e65100;
}

.actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
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
</style>
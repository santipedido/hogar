<template>
  <div class="activity-calendar">
    <div class="calendar-header">
      <h3>Calendario de Actividades</h3>
      <div class="calendar-controls">
        <button @click="previousMonth" class="nav-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15,18 9,12 15,6"></polyline>
          </svg>
        </button>
        <span class="current-month">{{ currentMonthName }} {{ currentYear }}</span>
        <button @click="nextMonth" class="nav-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9,18 15,12 9,6"></polyline>
          </svg>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loader">
      <IconSpinner :size="30" />
      <p>Cargando calendario...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="fetchCalendarData" class="retry-btn">Reintentar</button>
    </div>

    <div v-else class="calendar-container">
      <!-- Mensaje si no hay datos -->
      <div v-if="calendarData.value && calendarData.value.calendar_data && Object.keys(calendarData.value.calendar_data).length === 0" class="no-data-message">
        <p>No hay actividades registradas para {{ currentMonthName }} {{ currentYear }}</p>
        <p>Usa los botones de navegación para buscar en otros meses</p>
      </div>
      
      <!-- Días de la semana -->
      <div class="calendar-weekdays">
        <div v-for="day in weekDays" :key="day" class="weekday">{{ day }}</div>
      </div>

      <!-- Días del mes -->
      <div class="calendar-grid">
        <div 
          v-for="day in calendarDays" 
          :key="day.date" 
          class="calendar-day"
          :class="{
            'other-month': !day.isCurrentMonth,
            'today': day.isToday,
            'has-activities': day.activities && day.activities.length > 0
          }"
          @click="day.isCurrentMonth && day.activities && day.activities.length > 0 ? showDayDetails(day) : null"
        >
          <span class="day-number">{{ day.dayNumber }}</span>
          <div v-if="day.activities && day.activities.length > 0" class="activities-indicators">
            <div 
              v-for="activity in day.activities.slice(0, 3)" 
              :key="activity.id"
              class="activity-dot"
              :class="getActivityColor(activity.type)"
              :title="`${activity.title} - ${activity.type}`"
            ></div>
            <span v-if="day.activities.length > 3" class="more-indicator">+{{ day.activities.length - 3 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de detalles del día -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h4>{{ selectedDay?.date ? formatDate(selectedDay.date) : '' }}</h4>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedDay?.activities && selectedDay.activities.length > 0" class="day-activities">
            <div v-for="activity in selectedDay.activities" :key="activity.id" class="activity-item">
              <div class="activity-info">
                <div class="activity-header">
                  <h5>{{ activity.title }}</h5>
                  <span :class="['status-badge', activity.status]">
                    {{ getStatusText(activity.status) }}
                  </span>
                </div>
                <p class="type">{{ activity.type }} - {{ activity.subtype }}</p>
                <p class="time">{{ formatTime(activity.scheduled_at) }}</p>
                <p class="participants">Participantes: {{ activity.participants }}</p>
                <p v-if="activity.description" class="description">{{ activity.description }}</p>
                <p v-if="activity.notes" class="notes">{{ activity.notes }}</p>
                <p v-if="activity.registered_by" class="registered-by">Registrado por: {{ activity.registered_by }}</p>
                <div v-if="activity.is_recurring" class="recurring-info">
                  <span class="recurring-badge">🔄 Actividad semanal</span>
                  <span class="recurrence-day">{{ getDayText(activity.recurrence_day) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-activities">
            No hay actividades registradas para este día.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import IconSpinner from './icons/IconSpinner.vue'

const props = defineProps({
  residentId: {
    type: String,
    required: true
  }
})

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const loading = ref(false)
const error = ref('')
const calendarData = ref({ activities: [], calendar_data: {} })
const showModal = ref(false)
const selectedDay = ref(null)

const weekDays = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']

const currentMonthName = computed(() => {
  const months = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ]
  return months[currentMonth.value - 1]
})

const calendarDays = computed(() => {
  const days = []
  const firstDay = new Date(currentYear.value, currentMonth.value - 1, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value, 0)
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay())
  
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  // Verificar que calendarData.value existe y tiene la estructura correcta
  if (!calendarData.value || !calendarData.value.calendar_data) {
    return days
  }

  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)
    
    const dateKey = date.toISOString().split('T')[0]
    const isCurrentMonth = date.getMonth() === currentMonth.value - 1
    const isToday = date.getTime() === today.getTime()
    
    const activities = calendarData.value.calendar_data[dateKey] || []
    
    days.push({
      date: dateKey,
      dayNumber: date.getDate(),
      isCurrentMonth,
      isToday,
      activities: activities
    })
  }
  
  return days
})

async function fetchCalendarData() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(
      `${import.meta.env.VITE_API_URL}/api/activities/calendar/${props.residentId}?year=${currentYear.value}&month=${currentMonth.value}`
    )
    if (!res.ok) throw new Error('No se pudo cargar el calendario')
    calendarData.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function previousMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
  fetchCalendarData()
}

function nextMonth() {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
  fetchCalendarData()
}

function showDayDetails(day) {
  selectedDay.value = day
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedDay.value = null
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('es-ES', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}

function formatTime(dateTimeString) {
  const date = new Date(dateTimeString)
  return new Intl.DateTimeFormat('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

function getActivityColor(type) {
  const colors = {
    'Físicas': 'physical',
    'Recreativas': 'recreational',
    'Sociales': 'social',
    'Terapéuticas': 'therapeutic'
  }
  return colors[type] || 'default'
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

onMounted(fetchCalendarData)
</script>

<style scoped>
.activity-calendar {
  padding: 1rem;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.calendar-header h3 {
  margin: 0;
  color: var(--color-heading);
}

.calendar-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-btn {
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: var(--color-background-mute);
}

.current-month {
  font-weight: 600;
  color: var(--color-text-dark);
  min-width: 120px;
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
  text-align: center;
  padding: 2rem;
  color: var(--color-danger, #dc3545);
  background: var(--color-background-soft);
  border-radius: 8px;
}

.retry-btn {
  background: transparent;
  border: 1px solid var(--color-danger, #dc3545);
  color: var(--color-danger, #dc3545);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.calendar-container {
  background: var(--color-background-soft);
  border-radius: 10px;
  overflow: hidden;
}

.no-data-message {
  text-align: center;
  color: var(--color-text-light);
  padding: 2rem;
  background: var(--color-background-soft);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.no-data-message p {
  margin: 0.5rem 0;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: var(--color-background-mute);
}

.weekday {
  padding: 1rem 0.5rem;
  text-align: center;
  font-weight: 600;
  color: var(--color-text-dark);
  font-size: 0.875rem;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.calendar-day {
  min-height: 80px;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.calendar-day:hover {
  background: var(--color-background-mute);
}

.calendar-day.other-month {
  background: var(--color-background-mute);
  color: var(--color-text-light);
}

.calendar-day.today {
  background: var(--color-primary);
  color: white;
}

.calendar-day.has-activities {
  background: rgba(52, 152, 219, 0.1);
}

.day-number {
  font-weight: 600;
  font-size: 0.875rem;
}

.activities-indicators {
  position: absolute;
  bottom: 0.25rem;
  left: 0.25rem;
  right: 0.25rem;
  display: flex;
  gap: 0.125rem;
  flex-wrap: wrap;
}

.activity-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.activity-dot.physical { background: #4CAF50; }
.activity-dot.recreational { background: #2196F3; }
.activity-dot.social { background: #FF9800; }
.activity-dot.therapeutic { background: #9C27B0; }
.activity-dot.default { background: #95a5a6; }

.more-indicator {
  font-size: 0.625rem;
  color: var(--color-text-light);
  margin-left: 0.25rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--color-background);
  border-radius: 10px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h4 {
  margin: 0;
  color: var(--color-heading);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-light);
}

.modal-body {
  padding: 1.5rem;
}

.day-activities {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  background: var(--color-background-soft);
  border-radius: 8px;
  padding: 1rem;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.activity-header h5 {
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

.time {
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

.no-activities {
  text-align: center;
  color: var(--color-text-light);
  padding: 2rem;
}

@media (max-width: 640px) {
  .calendar-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .calendar-day {
    min-height: 60px;
    padding: 0.25rem;
  }
  
  .day-number {
    font-size: 0.75rem;
  }
  
  .activity-dot {
    width: 4px;
    height: 4px;
  }
}
</style>